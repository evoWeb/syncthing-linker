import * as fs from 'fs';
import * as path from 'path';

import { initializeAppConfig, processSourcePath } from './utilities';

function walkSync(dir: string, callback: (filePath: string) => void) {
    fs.readdirSync(dir).forEach(file => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        if (stat.isDirectory()) {
            walkSync(filePath, callback);
        } else {
            callback(filePath);
        }
    });
}

async function main() {
    const logger: Console = console,
        appConfig = initializeAppConfig();

    const source = appConfig.source;
    logger.info(`Searching in ${source}`);

    if (!fs.existsSync(source)) {
        logger.error(`Ignoring because ${source} does not exist.`);
        return;
    }

    walkSync(source, filePath => {
        processSourcePath(filePath, appConfig, logger);
    });
}

main().catch(console.error);
