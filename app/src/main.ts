import * as path from 'path';

import { Config } from './syncthing/Config';
import { Database } from './syncthing/Database';
import { Events } from './syncthing/Events';
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

function getSourcePathForEvent(event: any, config: any, database: any): string | null {
    const data = event.data || {};
    let sourcePath: string = '';
    if (data.error || (!data.folder && !data.item)) {
        return null;
    }

    try {
        const folder: any = config.folder(data.folder),
            file = database.file(data.folder, data.item);
        sourcePath = path.join(folder.path, file.get('local').name);
    } catch (error) {
        return null;
    }

    return sourcePath;
}

function sleep(ms: number) {
    return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
    const logger: Console = getLogger(),
        appConfig = initializeAppConfig();

    await checkServiceConfig(appConfig, logger);
    const config = new Config(appConfig);
    const database = new Database(appConfig);
    let lastSeenId: number = 0,
        continueWorking: boolean = true;

    logger.log('Waiting for events');
    while (continueWorking) {
        const eventStream = new Events(appConfig, lastSeenId, appConfig.filters);

        try {
            for await (const event of eventStream) {
                let sourcePath: string | null = getSourcePathForEvent(event, config, database);
                if (!sourcePath) {
                    continue;
                }
                processSourcePath(sourcePath, appConfig, logger);
                lastSeenId = event.id;
            }
            process.on('SIGINT', () => {
                logger.info('Stop waiting for events')
                continueWorking = false;
            });
        } catch (error) {
            await sleep(5000);
        }
    }
}

main().catch(console.error);
