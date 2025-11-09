

from abc import ABC, abstractmethod
from pathlib import Path
import tarfile
import os

class BaseCompressor(ABC):
    

    def __init__(self):
        self.extension = ""

    @abstractmethod
    def compress_file(
        self, input_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        pass

    @abstractmethod
    def compress_data(self, data: bytes) -> bytes:
        pass

    def compress(self, source: Path, destination: Path, progress_callback=None) -> None:
        source = Path(source)
        destination = Path(destination)

        if source.is_dir():
            self._compress_directory(source, destination, progress_callback)

        elif source.is_file():
            self.compress_file(source, destination, progress_callback)

        else:
            raise ValueError(f"Источник не существует: {source}")

    def _compress_directory(
        self, dir_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        tar_temp = output_path.with_suffix(".tar")

        try:

            with tarfile.open(tar_temp, "w") as tar:
                total_size = sum(
                    f.stat().st_size for f in dir_path.rglob("*") if f.is_file()
                )
                processed = 0

                for item in dir_path.rglob("*"):

                    if item.is_file():
                        arcname = item.relative_to(dir_path.parent)
                        tar.add(item, arcname=arcname)
                        processed += item.stat().st_size

                        if progress_callback and total_size > 0:
                            progress_callback(processed, total_size)

            self.compress_file(tar_temp, output_path, progress_callback)

        finally:

            if tar_temp.exists():
                tar_temp.unlink()

    def get_extension(self) -> str:
        return self.extension
