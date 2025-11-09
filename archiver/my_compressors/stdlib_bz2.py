from pathlib import Path
import bz2
from .base_compressor import BaseCompressor


class StdLibBz2Compressor(BaseCompressor):

    def __init__(self, level: int = 9):
        super().__init__()
        self.extension = ".bz2"
        self.level = max(1, min(9, level))

    def compress_data(self, data: bytes) -> bytes:

        if not data:
            return b""

        return bz2.compress(data, compresslevel=self.level)

    def compress_file(
        self, input_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)
        file_size = input_path.stat().st_size
        processed = 0

        if progress_callback:
            progress_callback(0, file_size)

        with open(input_path, "rb") as src, bz2.open(
            output_path, "wb", compresslevel=self.level
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
