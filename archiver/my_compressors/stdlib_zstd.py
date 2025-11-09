from pathlib import Path
from compression import zstd
from .base_compressor import BaseCompressor


class StdLibZstdCompressor(BaseCompressor):

    def __init__(self, level: int | None = None):
        super().__init__()
        self.extension = ".zst"
        self.level = level

    def compress_data(self, data: bytes) -> bytes:

        if not data:
            return b""

        return zstd.compress(data, level=self.level)

    def compress_file(
        self, input_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)
        file_size = input_path.stat().st_size
        processed = 0

        if progress_callback:
            progress_callback(0, file_size)

        with open(input_path, "rb") as src, zstd.open(
            output_path, "wb", level=self.level
        ) as dst:
            while True:
                chunk = src.read(1024 * 1024)
                if not chunk:
                    break
                dst.write(chunk)
                processed += len(chunk)
                if progress_callback and file_size > 0:
                    progress_callback(processed, file_size)

        if progress_callback:
            progress_callback(file_size, file_size)
