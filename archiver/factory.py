from pathlib import Path
from typing import Union
from .my_compressors import (
    BaseCompressor,
    ZstdCompressor,
    Bz2Compressor,
    StdLibZstdCompressor,
    StdLibBz2Compressor,
)
from .decompressors import (
    BaseDecompressor,
    ZstdDecompressor,
    Bz2Decompressor,
    StdLibZstdDecompressor,
    StdLibBz2Decompressor,
)


class ArchiveFactory:

    _compressors = {
        ".zst": {
            "custom": ZstdCompressor,
            "stdlib": StdLibZstdCompressor,
        },
        ".bz2": {
            "custom": Bz2Compressor,
            "stdlib": StdLibBz2Compressor,
        },
    }

    _decompressors = {
        ".zst": {
            "custom": ZstdDecompressor,
            "stdlib": StdLibZstdDecompressor,
        },
        ".bz2": {
            "custom": Bz2Decompressor,
            "stdlib": StdLibBz2Decompressor,
        },
    }

    @classmethod
    def get_compressor(
        cls,
        archive_path: Union[str, Path],
        level: int = 9,
        implementation: str = "custom",
    ) -> BaseCompressor:
        archive_path = Path(archive_path)
        ext = archive_path.suffix.lower()
        impl = implementation or "custom"
        impl = impl.lower()

        if ext not in cls._compressors:
            supported = ", ".join(cls._compressors.keys())
            raise ValueError(
                f"Неподдерживаемое расширение '{ext}'. " f"Поддерживаются: {supported}"
            )

        compressors = cls._compressors[ext]
        if impl not in compressors:
            available = ", ".join(sorted(compressors.keys()))
            raise ValueError(
                f"Неподдерживаемая реализация '{impl}' для '{ext}'. Доступны: {available}"
            )

        compressor_class = compressors[impl]
        return compressor_class(level=level)

    @classmethod
    def get_decompressor(
        cls, archive_path: Union[str, Path], implementation: str = "custom"
    ) -> BaseDecompressor:
        archive_path = Path(archive_path)
        ext = archive_path.suffix.lower()
        impl = implementation or "custom"
        impl = impl.lower()

        if ext not in cls._decompressors:
            supported = ", ".join(cls._decompressors.keys())
            raise ValueError(
                f"Неподдерживаемое расширение '{ext}'. " f"Поддерживаются: {supported}"
            )

        decompressors = cls._decompressors[ext]
        if impl not in decompressors:
            available = ", ".join(sorted(decompressors.keys()))
            raise ValueError(
                f"Неподдерживаемая реализация '{impl}' для '{ext}'. Доступны: {available}"
            )

        decompressor_class = decompressors[impl]
        return decompressor_class()

    @classmethod
    def register_compressor(
        cls, extension: str, compressor_class: type, implementation: str = "custom"
    ):
        if not extension.startswith("."):
            extension = "." + extension
        extension = extension.lower()
        impl = implementation or "custom"
        impl = impl.lower()
        cls._compressors.setdefault(extension, {})[impl] = compressor_class

    @classmethod
    def register_decompressor(
        cls,
        extension: str,
        decompressor_class: type,
        implementation: str = "custom",
    ):
        if not extension.startswith("."):
            extension = "." + extension
        extension = extension.lower()
        impl = implementation or "custom"
        impl = impl.lower()
        cls._decompressors.setdefault(extension, {})[impl] = decompressor_class

    @classmethod
    def supported_extensions(cls) -> list:
        extensions = set(cls._compressors.keys()) | set(cls._decompressors.keys())
        return sorted(list(extensions))

    @classmethod
    def available_implementations(cls, extension: str) -> list:
        if not extension.startswith("."):
            extension = "." + extension
        extension = extension.lower()
        compressor_impls = set(cls._compressors.get(extension, {}).keys())
        decompressor_impls = set(cls._decompressors.get(extension, {}).keys())
        implementations = compressor_impls | decompressor_impls
        return sorted(list(implementations))
