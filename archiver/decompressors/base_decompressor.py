from abc import ABC, abstractmethod
from pathlib import Path
import tarfile
import os


class BaseDecompressor(ABC):

    def __init__(self):
        self.extension = ""

    @abstractmethod
    def decompress_file(
        self, input_path: Path, output_path: Path, progress_callback=None
    ) -> None:
        pass

    @abstractmethod
    def decompress_data(self, data: bytes) -> bytes:
        pass

    def decompress(
        self, source: Path, destination: Path = None, progress_callback=None
    ) -> None:
        source = Path(source)

        if not source.exists():
            raise ValueError(f"Архив не существует: {source}")

        if destination is None:
            destination = source.with_suffix("")

        else:
            destination = Path(destination)

        temp_output = destination.with_suffix(".tmp")

        try:
            self.decompress_file(source, temp_output, progress_callback)

            if self._is_tar_archive(temp_output):
                self._extract_tar(temp_output, destination, progress_callback)
                temp_output.unlink()

            else:

                if temp_output != destination:

                    if destination.exists():
                        destination.unlink()

                    temp_output.rename(destination)

        except Exception as e:

            if temp_output.exists():
                temp_output.unlink()

            raise e

    def _is_tar_archive(self, file_path: Path) -> bool:
        try:
            with tarfile.open(file_path, "r") as tar:
                return True
        except:
            return False

    def _extract_tar(
        self, tar_path: Path, output_dir: Path, progress_callback=None
    ) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(tar_path, "r") as tar:
            members = tar.getmembers()
            total = len(members)

            for i, member in enumerate(members):
                tar.extract(member, output_dir)

                if progress_callback and total > 0:
                    progress_callback(i + 1, total)

    def get_extension(self) -> str:
        return self.extension
