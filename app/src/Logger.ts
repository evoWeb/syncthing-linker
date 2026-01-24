import fs from 'fs';
import { WriteStream } from 'fs';
import { format } from 'util';

export class Logger implements Console {
  protected logWriter: WriteStream;
  public Console: typeof console.Console = console.Console;

  constructor(logFilePath: string) {
    this.logWriter = fs.createWriteStream(logFilePath, {flags: 'a', mode: 0o644});
  }

  private write(level: string, ...args: any[]): void {
    const message = format(...args);
    const timestamp = new Date().toISOString();
    const output = `${timestamp} [${level.toUpperCase()}]: ${message}\n`;

    // Write to a file
    this.logWriter.write(output);
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
