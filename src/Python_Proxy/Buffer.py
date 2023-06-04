class Buffer:
    def __init__(self, buffer) -> None:
        self.buffer = bytearray(buffer)
        self.currentOffset = 0

    def readBytes(self, bytes: int):
        data = self.buffer[self.currentOffset: self.currentOffset + bytes]
        self.currentOffset += bytes
        return data