import * as path from 'path';

import Config from './syncthing/Config';
import Database from './syncthing/Database';
import Events, { Event, EventData } from './syncthing/Events';
import System from './syncthing/System';
import ServiceConfig from './syncthing/ServiceConfig';
import AppConfig from './AppConfig';
import Logger from './Logger';
import processSourcePath from './processSourcePath';

/**
 * Checks the connection to the Syncthing API
 *
 * @param config ServiceConfig
 * @param logger Console
 */
async function checkServiceConfig(config: ServiceConfig, logger: Console): Promise<void> {
  const system = new System(config, logger);

  const syncErrors = await system.errors();
  system.clear();

  if (syncErrors.length > 0) {
    syncErrors.forEach(e => logger.error(e.message));
    throw new Error('Accessing Syncthing API failed.');
  }
}

async function getSourcePathForEvent(
  event: Event,
  config: Config,
  database: Database,
  logger: Console
): Promise<string | null> {
  const data: EventData = event.data || { action: 'error', error: 'No data' };
  if (data.error || (!data.folder || !data.item)) {
    return null;
  }

  let sourcePath: string = '';
  try {
    const folder = await config.folder(data.folder),
      file = await database.file(data.folder, data.item);
    if (file.local.blocksHash === null) {
      return null;
    }
    sourcePath = path.join(folder.path, file.local.name);
  } catch (error) {
    return null;
  }

  return sourcePath;
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main(): Promise<void> {
  const logger: Console = Logger.getInstance('main'),
    eventLogger: Console = Logger.getInstance('event'),
    appConfig = AppConfig.getInstance();

  await checkServiceConfig(appConfig, Logger.getInstance('system'));
  const config = new Config(appConfig, Logger.getInstance('config')),
    database = new Database(appConfig, Logger.getInstance('database'));

  let lastSeenId: number = 0,
    continueWorking: boolean = true;

  process.on('SIGINT', () => {
    continueWorking = false;
  });

  logger.info('Waiting for events');
  while (continueWorking) {
    const eventStream = new Events(appConfig, eventLogger, lastSeenId, appConfig.filters);

    try {
      for await (const event of eventStream) {
        eventLogger.info(JSON.stringify(event));

        if (['delete'].includes(event.data.action)) {
          lastSeenId = event.id;
          continue;
        }

        let sourcePath: string | null = await getSourcePathForEvent(event, config, database, logger);
        if (!sourcePath) {
          continue;
        }

        lastSeenId = event.id;
        processSourcePath(sourcePath, appConfig, logger);
      }
    } catch (error: any) {
      // Timeout exceptions aren't logged because the next request continues where the previous ended.
      if (error.message !== 'Timeout while fetching new events') {
        logger.error(error);
      }
      await sleep(appConfig.timeout * 1000);
    }
  }
}

main().catch(console.error);
