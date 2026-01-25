import fs, { WriteStream } from 'fs';
import * as path from 'path';
import { format } from 'util';

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

export default class Logger implements Console {
  protected channel: string;
  protected logWriter: WriteStream;
  public Console: typeof console.Console = console.Console;

  constructor(logFilePath: string, channel?: string) {
    this.channel = channel?.toLowerCase() || '';
    this.logWriter = fs.createWriteStream(logFilePath, {flags: 'a', mode: 0o644});
    this.registerCleanupHandlers();
  }

  static getInstance(channel?: string): Console {
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

  private registerCleanupHandlers(): void {
    process.on('exit', () => this.close());
    process.on('SIGINT', () => this.close());
    process.on('SIGTERM', () => this.close());
    process.on('uncaughtException', error => {
      this.error('Uncaught exception:', error);
      this.close();
      process.exit(1);
    });
  }

  public close(): void {
    if (this.logWriter && !this.logWriter.closed) {
      this.logWriter.end();
    }
  }

  private write(level: string, ...args: any[]): void {
    const message = format(...args);
    const timestamp = (new Date()).toISOString().slice(0, -1) + '000+00:00';
    const channel = this.channel ? `${this.channel}.` : '';
    const output = `[${timestamp}] ${channel}${level.toUpperCase()}: ${message}\n`;

    // Write to a file
    try {
      this.logWriter.write(output);
    } catch (error) {}

    // Also write to stdout/stderr for visibility
    if (level === 'error' || level === 'warn') {
      process.stderr.write(output);
    } else {
      process.stdout.write(output);
    }
  }

  log(...args: any[]): void {
    this.write('log', ...args);
  }

  info(...args: any[]): void {
    this.write('info', ...args);
  }

  warn(...args: any[]): void {
    this.write('warn', ...args);
  }

  error(...args: any[]): void {
    this.write('error', ...args);
  }

  debug(...args: any[]): void {
    this.write('debug', ...args);
  }

  // Required by Console interface but often not used in custom loggers
  assert(condition?: boolean, ...data: any[]): void {
    if (!condition) {
      this.error('Assertion failed:', ...data);
    }
  }

  clear(): void {
  }

  count(label?: string): void {
  }

  countReset(label?: string): void {
  }

  dir(item?: any, options?: any): void {
    this.log(item);
  }

  dirxml(...data: any[]): void {
    this.log(...data);
  }

  group(...data: any[]): void {
  }

  groupCollapsed(...data: any[]): void {
  }

  groupEnd(): void {
  }

  profile(reportName?: string): void {
  }

  profileEnd(reportName?: string): void {
  }

  table(tabularData?: any, properties?: string[]): void {
    this.log(tabularData);
  }

  time(label?: string): void {
  }

  timeEnd(label?: string): void {
  }

  timeLog(label?: string, ...data: any[]): void {
  }

  timeStamp(label?: string): void {
  }

  trace(...data: any[]): void {
    this.error('Trace:', ...data);
  }
}
