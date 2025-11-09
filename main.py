import argparse
import sys
from pathlib import Path

from archiver.factory import ArchiveFactory
from archiver.utils.progress_bar import ProgressBar
from archiver.utils.benchmark import Benchmark, format_time


def compress_command(args):

    source = Path(args.source)
    output = Path(args.output)

    if not source.exists():
        print(f"Ошибка: Источник не существует: {source}", file=sys.stderr)
        sys.exit(1)

    try:
        compressor = ArchiveFactory.get_compressor(
            output, level=args.level, implementation=args.impl
        )
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    progress = None
    if args.progress:
        if source.is_file():
            total_size = source.stat().st_size
        else:
            total_size = sum(f.stat().st_size for f in source.rglob("*") if f.is_file())
        progress = ProgressBar(total=total_size, desc="Сжатие")

        def progress_callback(current, total):
            progress.update(current, total)

    else:
        progress_callback = None

    bench = Benchmark() if args.benchmark else None

    try:
        if bench:
            bench.start()

        print(f"Сжатие: {source} -> {output}")
        print(f"Формат: {output.suffix}")
        print(f"Уровень сжатия: {args.level}")
        print(f"Реализация: {args.impl}")

        compressor.compress(source, output, progress_callback)

        if bench:
            bench.stop()

        if output.exists():
            original_size = source.stat().st_size if source.is_file() else total_size
            compressed_size = output.stat().st_size
            ratio = (
                (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            )

            print(f"\n[OK] Архив успешно создан!")
            print(f"  Исходный размер: {_format_size(original_size)}")
            print(f"  Размер архива: {_format_size(compressed_size)}")
            print(f"  Степень сжатия: {ratio:.1f}%")

            if bench:
                print(f"  Время выполнения: {bench.format_elapsed()}")

    except Exception as e:
        print(f"\n[ERROR] Ошибка при сжатии: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if progress:
            progress.close()


def decompress_command(args):

    source = Path(args.source)
    output = Path(args.output) if args.output else None

    if not source.exists():
        print(f"Ошибка: Архив не существует: {source}", file=sys.stderr)
        sys.exit(1)

    try:
        decompressor = ArchiveFactory.get_decompressor(source, implementation=args.impl)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    progress = None
    if args.progress:
        total_size = source.stat().st_size
        progress = ProgressBar(total=total_size, desc="Распаковка")

        def progress_callback(current, total):
            progress.update(current, total)

    else:
        progress_callback = None

    bench = Benchmark() if args.benchmark else None

    try:
        if bench:
            bench.start()

        print(f"Распаковка: {source}")
        if output:
            print(f"Место: {output}")
        print(f"Реализация: {args.impl}")

        decompressor.decompress(source, output, progress_callback)

        if bench:
            bench.stop()

        final_output = output if output else source.with_suffix("")
        if final_output.exists() or final_output.is_dir():
            print(f"\n[OK] Архив успешно распакован!")
            print(f"  Расположение: {final_output}")

            if bench:
                print(f"  Время выполнения: {bench.format_elapsed()}")

    except Exception as e:
        print(f"\n[ERROR] Ошибка при распаковке: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if progress:
            progress.close()


def list_formats_command(args):

    extensions = ArchiveFactory.supported_extensions()
    print("Поддерживаемые форматы:")
    for ext in extensions:
        print(f"  {ext}")


def _format_size(size: int) -> str:

    for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} ПБ"


def main():

    parser = argparse.ArgumentParser(
        description="Консольная утилита архиватор/распаковщик",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    compress_parser = subparsers.add_parser(
        "compress", aliases=["c"], help="Сжать файл или директорию"
    )
    compress_parser.add_argument(
        "source", type=str, help="Путь к файлу или директории для сжатия"
    )
    compress_parser.add_argument(
        "output", type=str, help="Путь к выходному архиву (.zst или .bz2)"
    )
    compress_parser.add_argument(
        "-l",
        "--level",
        type=int,
        default=9,
        choices=range(1, 10),
        metavar="LEVEL",
        help="Уровень сжатия (1-9, по умолчанию: 9)",
    )
    compress_parser.add_argument(
        "-b",
        "--benchmark",
        action="store_true",
        help="Включить режим benchmark (показывать время выполнения)",
    )
    compress_parser.add_argument(
        "-p", "--progress", action="store_true", help="Показывать прогресс-бар"
    )
    compress_parser.add_argument(
        "--impl",
        type=str,
        choices=["custom", "stdlib"],
        default="custom",
        help="Выбор реализации алгоритма",
    )
    compress_parser.set_defaults(func=compress_command)

    decompress_parser = subparsers.add_parser(
        "decompress", aliases=["d", "extract", "x"], help="Распаковать архив"
    )
    decompress_parser.add_argument(
        "source", type=str, help="Путь к архиву для распаковки"
    )
    decompress_parser.add_argument(
        "output",
        type=str,
        nargs="?",
        default=None,
        help="Путь для распакованных файлов (опционально)",
    )
    decompress_parser.add_argument(
        "-b",
        "--benchmark",
        action="store_true",
        help="Включить режим benchmark (показывать время выполнения)",
    )
    decompress_parser.add_argument(
        "-p", "--progress", action="store_true", help="Показывать прогресс-бар"
    )
    decompress_parser.add_argument(
        "--impl",
        type=str,
        choices=["custom", "stdlib"],
        default="custom",
        help="Выбор реализации алгоритма",
    )
    decompress_parser.set_defaults(func=decompress_command)

    list_parser = subparsers.add_parser(
        "list-formats",
        aliases=["formats", "ls"],
        help="Показать поддерживаемые форматы",
    )
    list_parser.set_defaults(func=list_formats_command)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
