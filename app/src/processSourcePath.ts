import * as fs from 'fs';
import * as path from 'path';

import AppConfig from './AppConfig';

function sourcePathIsQualified(sourcePath: string, appConfig: AppConfig, logger: Console): boolean {
  if (!fs.existsSync(sourcePath)) {
    logger.info(`Ignoring event for ${sourcePath} because it does not exist.`);
    return false;
  }
  if (fs.lstatSync(sourcePath).isDirectory()) {
    logger.info(`Ignoring event for ${sourcePath} because it\'s a folder.`);
    return false;
  }
  if (!sourcePath.startsWith(appConfig.source)) {
    logger.info(`Ignoring event for ${sourcePath} because it does not start with ${appConfig.source}.`);
    return false;
  }
  if (appConfig.excludes && appConfig.excludes.test(sourcePath)) {
    logger.info(`Ignoring ${sourcePath} because it matches exclude pattern.`);
    return false;
  }
  return true;
}

function linkSourceToDestination(sourcePath: string, destinationPath: string, logger: Console): void {
  const destinationParent = path.dirname(destinationPath);
  if (!fs.existsSync(destinationParent)) {
    fs.mkdirSync(destinationParent, { recursive: true });
    logger.info(`Created parent directory ${destinationParent} for ${destinationPath}.`)
  }

  if (fs.existsSync(destinationPath)) {
    return;
  }

  try {
    fs.linkSync(sourcePath, destinationPath);
    logger.info(`Linked ${sourcePath} to ${destinationPath}`);
  } catch (error) {
    logger.error(`Error linking ${sourcePath} to ${destinationPath}:`, error);
  }
}

export default function processSourcePath(sourcePath: string, appConfig: AppConfig, logger: Console): void {
  if (!sourcePathIsQualified(sourcePath, appConfig, logger)) {
    return;
  }

  const relative = path.relative(appConfig.source, sourcePath),
    destinationPath = path.join(appConfig.destination, relative);

  linkSourceToDestination(sourcePath, destinationPath, logger);
}
