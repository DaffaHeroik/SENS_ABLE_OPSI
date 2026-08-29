interface SerialPort {
  open(options: { baudRate: number }): Promise<void>;
  close(): Promise<void>;
  writable?: WritableStream<Uint8Array>;
}

interface Navigator {
  serial?: {
    requestPort(options?: unknown): Promise<SerialPort>;
  };
}
