export class SyncthingException extends Error {
  /**
   * Base Syncthing Exception class all non-assertion errors will raise from.
   */
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);

    this.name = 'SyncthingException';
    // Maintain a proper stack trace for where our error was thrown (only available on V8)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, SyncthingException);
    }
  }
}
