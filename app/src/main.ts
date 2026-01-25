import * as path from 'path';

import { Config } from './syncthing/Config';
import { Database } from './syncthing/Database';
import { Events, Event, EventData } from './syncthing/Events';
import { System } from './syncthing/System';
import { ServiceConfig } from './syncthing/ServiceConfig';
import { initializeAppConfig, processSourcePath, getLogger } from './utilities';

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
    logger.info(folder, file);
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
  const logger: Console = getLogger(),
    appConfig = initializeAppConfig();

  await checkServiceConfig(appConfig, logger);
  const config = new Config(appConfig, logger),
    database = new Database(appConfig, logger);

  let lastSeenId: number = 0,
    continueWorking: boolean = true;

  process.on('SIGINT', () => {
    continueWorking = false;
  });

  logger.info('Waiting for events');
  while (continueWorking) {
    const eventStream = new Events(appConfig, logger, lastSeenId, appConfig.filters);

    try {
      for await (const event of eventStream) {
        lastSeenId = event.id;
        logger.info(JSON.stringify(event));
        let sourcePath: string | null = await getSourcePathForEvent(event, config, database, logger);
        if (!sourcePath) {
          continue;
        }
        if (['delete'].includes(event.data.action)) {
          logger.info('Skip item deletion')
          continue;
        }
        processSourcePath(sourcePath, appConfig, logger);
      }
    } catch (error: any) {
      if (error.message.includes('timeout')) {
        await sleep(appConfig.timeout * 1000);
        continue;
      }
      logger.error(error);
    }
  }
}

main().catch(console.error);
