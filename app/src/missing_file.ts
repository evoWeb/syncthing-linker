import * as fs from 'fs';
import * as path from 'path';

import AppConfig from './AppConfig';
import processSourcePath from './processSourcePath';

function walkSync(directory: string, callback: (filePath: string) => void): void {
  fs.readdirSync(directory)
    .forEach(file => {
      const filePath = path.join(directory, file),
        stat = fs.statSync(filePath);
      if (stat.isDirectory()) {
        walkSync(filePath, callback);
      } else {
        callback(filePath);
      }
    });
}

async function main(): Promise<void> {
  const logger: Console = console,
    appConfig = AppConfig.getInstance();

  logger.info(`Searching in ${appConfig.source}`);

  if (!fs.existsSync(appConfig.source)) {
    logger.error(`Ignoring because ${appConfig.source} does not exist.`);
    return;
  }

  walkSync(appConfig.source, filePath => {
    processSourcePath(filePath, appConfig, logger);
  });
}

main().catch(console.error);
