import * as fs from 'fs';
import * as path from 'path';
import * as yaml from 'js-yaml';

import { AppConfig } from './AppConfig';
import { Logger } from './Logger';

export function initializeAppConfig(configPath: string = '/config/config.yaml'): AppConfig {
  const fileContents = fs.readFileSync(configPath, 'utf8'),
    config: any = yaml.load(fileContents);

  if (!config) {
    throw new Error('Configuration is empty.');
  }

  const apiKey = process.env.SYNCTHING_API_KEY || '';
  if (!apiKey) {
    throw new Error('No API key found.');
  }

  const host: string = process.env.SYNCTHING_HOST || '127.0.0.1',
    port: number = parseInt(process.env.SYNCTHING_PORT || '8384'),
    isHttps: boolean = ['1', 'true', 'yes'].includes((process.env.SYNCTHING_HTTPS || '0').toLowerCase()),
    sslCertFile: string | undefined = process.env.SYNCTHING_CERT_FILE;

  return new AppConfig(
    apiKey,
    host,
    port,
    parseInt(process.env.SYNCTHING_TIMEOUT || '60'),
    isHttps,
    sslCertFile,
    config.source || '/files/source/',
    config.destination || '/files/destination/',
    (config.filter || 'ItemFinished').split(','),
    new RegExp(config.excludes || '')
  );
}

function linkSourceToDestination(sourcePath: string, destinationPath: string, logger: Console): void {
  const destinationParent = path.dirname(destinationPath);
  if (!fs.existsSync(destinationParent)) {
    fs.mkdirSync(destinationParent, {recursive: true});
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

export function processSourcePath(sourcePath: string, appConfig: AppConfig, logger: Console): void {
  if (!sourcePathIsQualified(sourcePath, appConfig, logger)) {
    return;
  }

  const relative = path.relative(appConfig.source, sourcePath),
    destinationPath = path.join(appConfig.destination, relative);

  linkSourceToDestination(sourcePath, destinationPath, logger);
}

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

function rotateOldLogs(logDirectory: string): void {
  try {
    if (!fs.existsSync(logDirectory)) {
      return;
    }

    const files = fs.readdirSync(logDirectory);
    const now = new Date();
    const tenDaysAgo = new Date(now.getTime() - 10 * 24 * 60 * 60 * 1000);

    files.forEach(file => {
      const match = file.match(/^linker-(\d{4})(\d{2})(\d{2})\.log$/);
      if (match) {
        const [, year, month, day] = match;
        const fileDate = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));

        if (fileDate < tenDaysAgo) {
          const filePath = path.join(logDirectory, file);
          fs.unlinkSync(filePath);
          console.info(`Deleted old log file: ${file}`);
        }
      }
    });
  } catch (error) {
    console.error('Error rotating logs:', error);
  }
}

export function getLogger(channel?: string): Console {
  if (!process.env.WRITE_LOGS) {
    return console;
  }

  const now = new Date(),
    year = now.getFullYear(),
    month = String(now.getMonth() + 1).padStart(2, '0'),
    day = String(now.getDate()).padStart(2, '0'),
    logPathOverride = process.env.LOG_PATH?.trim(),
    logfilePath = (logPathOverride && logPathOverride.length > 0)
      ? logPathOverride
      : `/logs/linker-${year}${month}${day}.log`;

  const logDirectory = path.dirname(logfilePath);
  rotateOldLogs(logDirectory);

  return new Logger(logfilePath, channel);
}
