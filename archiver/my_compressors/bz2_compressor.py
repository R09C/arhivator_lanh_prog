from pathlib import Path
import bz2
from .base_compressor import BaseCompressor


class Bz2Compressor(BaseCompressor):

    def __init__(self, level: int = 9):
        super().__init__()
        self.extension = ".bz2"
        self.level = max(1, min(9, level))

    def compress_data(self, data: bytes) -> bytes:
        if not data:
            return b""

        try:
            compressed = bz2.compress(data, compresslevel=self.level)
            return compressed
        except Exception as e:
            raise RuntimeError(f"Ошибка при сжатии bz2: {e}")

    def compress_file(
        self, input_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)
        file_size = input_path.stat().st_size

        if progress_callback:
            progress_callback(0, file_size)

        try:
            with open(input_path, "rb") as f_in:
                with bz2.open(
                    str(output_path), "wb", compresslevel=self.level
                ) as f_out:
                    chunk_size = 65536
                    bytes_processed = 0

                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        bytes_processed += len(chunk)

                        if progress_callback:
                            progress_callback(
                                min(bytes_processed, file_size), file_size
                            )
        except Exception as e:
            raise RuntimeError(f"Ошибка при сжатии файла: {e}")

        if progress_callback:
            progress_callback(file_size, file_size)
