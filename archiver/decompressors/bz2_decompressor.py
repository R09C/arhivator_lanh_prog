from pathlib import Path
import bz2
from .base_decompressor import BaseDecompressor


class Bz2Decompressor(BaseDecompressor):

    def __init__(self):
        super().__init__()
        self.extension = ".bz2"

    def decompress_data(self, data: bytes) -> bytes:
        if not data:
            return b""

        try:
            decompressed = bz2.decompress(data)
            return decompressed
        except Exception as e:
            raise RuntimeError(f"Ошибка при распаковке bz2: {e}")

    def decompress_file(
        self, input_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        input_path = Path(input_path)
        output_path = Path(output_path)
        file_size = input_path.stat().st_size

        if progress_callback:
            progress_callback(0, file_size)

        try:
            with bz2.open(str(input_path), "rb") as f_in:
                with open(output_path, "wb") as f_out:
                    chunk_size = 65536
                    bytes_processed = 0

                    while True:
                        chunk = f_in.read(chunk_size)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        bytes_processed += chunk_size

                        if progress_callback:
                            progress_callback(
                                min(bytes_processed, file_size), file_size
                            )
        except Exception as e:
            raise RuntimeError(f"Ошибка при распаковке файла: {e}")

        if progress_callback:
            progress_callback(file_size, file_size)
