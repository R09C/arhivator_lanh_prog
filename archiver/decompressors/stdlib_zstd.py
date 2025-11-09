from pathlib import Path
from compression import zstd
from .base_decompressor import BaseDecompressor


class StdLibZstdDecompressor(BaseDecompressor):

    def __init__(self):
        super().__init__()
        self.extension = ".zst"

    def decompress_data(self, data: bytes) -> bytes:

        if not data:
            return b""

        return zstd.decompress(data)

    def decompress_file(
        self, input_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)
        file_size = input_path.stat().st_size
        processed = 0

        if progress_callback:
            progress_callback(0, file_size)

        with zstd.open(input_path, "rb") as src, open(output_path, "wb") as dst:
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
