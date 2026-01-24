import * as path from 'path';

import { Config } from './syncthing/Config';
import { Database } from './syncthing/Database';
import { Events, Event } from './syncthing/Events';
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
  const system = new System(config);

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
  const data = event.data || {};
  if (data.error || (!data.folder && !data.item)) {
    return null;
  }

  let sourcePath: string = '';
  try {
    const folder = await config.folder(data.folder),
      file = await database.file(data.folder, data.item);
    logger.info(folder, file);
    sourcePath = path.join(folder.path, file.local.name);
  } catch (error: any) {
    return null;
  }

  return sourcePath;
}

function sleep(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  const logger: Console = getLogger(),
    appConfig = initializeAppConfig();

  await checkServiceConfig(appConfig, logger);
  const config = new Config(appConfig),
    database = new Database(appConfig);
  let lastSeenId: number = 0,
    continueWorking: boolean = true;

  process.on('SIGINT', () => {
    logger.info('Stop waiting for events')
    continueWorking = false;
  });

  logger.info('Waiting for events');
  while (continueWorking) {
    const eventStream = new Events(appConfig, logger, lastSeenId, appConfig.filters);

    try {
      for await (const event of eventStream) {
        logger.info(JSON.stringify(event));
        let sourcePath: string | null = await getSourcePathForEvent(event, config, database, logger);
        if (!sourcePath) {
          continue;
        }
        processSourcePath(sourcePath, appConfig, logger);
        lastSeenId = event.id;
      }
    } catch (error: any) {
      logger.error(error);
      await sleep(appConfig.timeout * 1000);
    }
  }
}

main().catch(console.error);
