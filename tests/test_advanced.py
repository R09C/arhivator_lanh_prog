import os
import sys
import time
import random
import string
from pathlib import Path


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from archiver.factory import ArchiveFactory


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")


def print_test(name):
    print(f"{Colors.YELLOW}[ТЕСТ]{Colors.RESET} {name}")


def print_success(msg):
    print(f"{Colors.GREEN}[OK]{Colors.RESET} {msg}")


def print_error(msg):
    print(f"{Colors.RED}[FAIL]{Colors.RESET} {msg}")


def format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} КБ"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} МБ"


def test_empty_file():
    print_test("Сжатие пустого файла")

    test_file = "test_empty.txt"
    with open(test_file, "wb") as f:
        pass

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_empty{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(archive, implementation=impl)
                comp.compress_file(test_file, archive)

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_empty_out{fmt.replace('.', '_')}_{impl}.txt"
                decomp.decompress_file(archive, output)

                with open(output, "rb") as f:
                    data = f.read()

                if len(data) == 0:
                    print_success(f"{impl} {fmt}: Пустой файл обработан корректно")
                else:
                    print_error(f"{impl} {fmt}: Ожидалось 0 байт, получено {len(data)}")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_single_byte():
    print_test("Сжатие файла из одного байта")

    test_file = "test_single.txt"
    test_data = b"X"
    with open(test_file, "wb") as f:
        f.write(test_data)

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_single{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(archive, implementation=impl)
                comp.compress_file(test_file, archive)

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_single_out{fmt.replace('.', '_')}_{impl}.txt"
                decomp.decompress_file(archive, output)

                with open(output, "rb") as f:
                    data = f.read()

                if data == test_data:
                    print_success(f"{impl} {fmt}: Один байт восстановлен")
                else:
                    print_error(f"{impl} {fmt}: Данные не совпадают")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_repetitive_data():
    print_test("Сжатие высокоповторяющихся данных")

    test_file = "test_repetitive.bin"
    test_data = b"A" * 100000
    with open(test_file, "wb") as f:
        f.write(test_data)

    original_size = len(test_data)

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_repetitive{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(
                    archive, level=9, implementation=impl
                )
                start = time.time()
                comp.compress_file(test_file, archive)
                comp_time = time.time() - start

                archive_size = os.path.getsize(archive)
                ratio = (1 - archive_size / original_size) * 100

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_repetitive_out{fmt.replace('.', '_')}_{impl}.bin"
                start = time.time()
                decomp.decompress_file(archive, output)
                decomp_time = time.time() - start

                with open(output, "rb") as f:
                    data = f.read()

                if data == test_data:
                    print_success(
                        f"{impl} {fmt}: {format_size(original_size)} -> {format_size(archive_size)} "
                        f"({ratio:.1f}% сжатие, {comp_time*1000:.1f}мс/{decomp_time*1000:.1f}мс)"
                    )
                else:
                    print_error(f"{impl} {fmt}: Данные не совпадают")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_random_data():
    print_test("Сжатие случайных данных (несжимаемых)")

    test_file = "test_random.bin"
    test_data = os.urandom(10000)
    with open(test_file, "wb") as f:
        f.write(test_data)

    original_size = len(test_data)

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_random{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(
                    archive, level=9, implementation=impl
                )
                comp.compress_file(test_file, archive)

                archive_size = os.path.getsize(archive)
                expansion = (archive_size / original_size - 1) * 100

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_random_out{fmt.replace('.', '_')}_{impl}.bin"
                decomp.decompress_file(archive, output)

                with open(output, "rb") as f:
                    data = f.read()

                if data == test_data:
                    if expansion > 0:
                        print_success(
                            f"{impl} {fmt}: Случайные данные (+{expansion:.1f}% расширение)"
                        )
                    else:
                        print_success(f"{impl} {fmt}: Данные восстановлены")
                else:
                    print_error(f"{impl} {fmt}: Данные не совпадают")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_mixed_content():
    print_test("Сжатие смешанного контента (текст + бинарные данные)")

    test_file = "test_mixed.bin"
    text_part = "Hello World! " * 100
    binary_part = bytes(range(256)) * 10
    test_data = text_part.encode() + binary_part

    with open(test_file, "wb") as f:
        f.write(test_data)

    original_size = len(test_data)

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_mixed{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(
                    archive, level=9, implementation=impl
                )
                comp.compress_file(test_file, archive)

                archive_size = os.path.getsize(archive)
                ratio = (1 - archive_size / original_size) * 100

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_mixed_out{fmt.replace('.', '_')}_{impl}.bin"
                decomp.decompress_file(archive, output)

                with open(output, "rb") as f:
                    data = f.read()

                if data == test_data:
                    print_success(
                        f"{impl} {fmt}: {format_size(original_size)} -> {format_size(archive_size)} ({ratio:.1f}%)"
                    )
                else:
                    print_error(f"{impl} {fmt}: Данные не совпадают")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_unicode_text():
    print_test("Сжатие Unicode текста (кириллица)")

    test_file = "test_unicode.txt"
    test_text = "Привет мир! " * 100 + "Тест на русском языке " * 50
    test_data = test_text.encode("utf-8")

    with open(test_file, "wb") as f:
        f.write(test_data)

    original_size = len(test_data)

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_unicode{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(
                    archive, level=9, implementation=impl
                )
                comp.compress_file(test_file, archive)

                archive_size = os.path.getsize(archive)
                ratio = (1 - archive_size / original_size) * 100

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_unicode_out{fmt.replace('.', '_')}_{impl}.txt"
                decomp.decompress_file(archive, output)

                with open(output, "rb") as f:
                    data = f.read()

                if data == test_data:
                    decoded = data.decode("utf-8")
                    if decoded == test_text:
                        print_success(
                            f"{impl} {fmt}: Unicode корректно ({ratio:.1f}% сжатие)"
                        )
                    else:
                        print_error(f"{impl} {fmt}: Текст изменился после распаковки")
                else:
                    print_error(f"{impl} {fmt}: Бинарные данные не совпадают")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_large_file():
    print_test("Сжатие большого файла (1 МБ)")

    test_file = "test_large.bin"
    chunks = []
    for i in range(100):
        chunks.append(f"Chunk {i}: " + "data " * 200)
    test_data = "".join(chunks).encode()

    with open(test_file, "wb") as f:
        f.write(test_data)

    original_size = len(test_data)

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_large{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(
                    archive, level=9, implementation=impl
                )
                start = time.time()
                comp.compress_file(test_file, archive)
                comp_time = time.time() - start

                archive_size = os.path.getsize(archive)
                ratio = (1 - archive_size / original_size) * 100

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_large_out{fmt.replace('.', '_')}_{impl}.bin"
                start = time.time()
                decomp.decompress_file(archive, output)
                decomp_time = time.time() - start

                with open(output, "rb") as f:
                    data = f.read()

                if data == test_data:
                    print_success(
                        f"{impl} {fmt}: {format_size(original_size)} -> {format_size(archive_size)} "
                        f"({ratio:.1f}%, {comp_time:.2f}с/{decomp_time:.2f}с)"
                    )
                else:
                    print_error(f"{impl} {fmt}: Данные не совпадают")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_all_bytes():
    print_test("Сжатие файла со всеми возможными байтами (0-255)")

    test_file = "test_allbytes.bin"
    test_data = bytes(range(256)) * 100

    with open(test_file, "wb") as f:
        f.write(test_data)

    original_size = len(test_data)

    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            archive = f"test_allbytes{fmt}"
            try:
                comp = ArchiveFactory.get_compressor(
                    archive, level=9, implementation=impl
                )
                comp.compress_file(test_file, archive)

                archive_size = os.path.getsize(archive)
                ratio = (1 - archive_size / original_size) * 100

                decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
                output = f"test_allbytes_out{fmt.replace('.', '_')}_{impl}.bin"
                decomp.decompress_file(archive, output)

                with open(output, "rb") as f:
                    data = f.read()

                if data == test_data:
                    print_success(
                        f"{impl} {fmt}: Все 256 байт-значений ({ratio:.1f}% сжатие)"
                    )
                else:
                    print_error(f"{impl} {fmt}: Данные не совпадают")

                os.remove(archive)
                os.remove(output)
            except Exception as e:
                print_error(f"{impl} {fmt}: {e}")

    os.remove(test_file)


def test_compression_levels():
    print_test("Сравнение уровней сжатия (1, 5, 9)")

    test_file = "test_levels.txt"
    test_data = ("compress " * 1000).encode()

    with open(test_file, "wb") as f:
        f.write(test_data)

    original_size = len(test_data)

    for impl in ["custom", "stdlib"]:
        print(f"\n  {impl.upper()}:")
        for fmt in [".zst", ".bz2"]:
            results = []
            for level in [1, 5, 9]:
                archive = f"test_level_{level}{fmt}"
                try:
                    comp = ArchiveFactory.get_compressor(
                        archive, level=level, implementation=impl
                    )
                    start = time.time()
                    comp.compress_file(test_file, archive)
                    comp_time = time.time() - start

                    archive_size = os.path.getsize(archive)
                    ratio = (1 - archive_size / original_size) * 100
                    results.append(
                        f"L{level}: {format_size(archive_size)} ({ratio:.1f}%, {comp_time*1000:.0f}мс)"
                    )

                    os.remove(archive)
                except Exception as e:
                    results.append(f"L{level}: Ошибка")

            print(f"    {fmt}: " + " | ".join(results))

    os.remove(test_file)


def main():
    print_header("РАСШИРЕННОЕ ТЕСТИРОВАНИЕ АРХИВАТОРА")
    print(f"Python версия: {sys.version.split()[0]}")

    try:
        from compression import zstd

        print(f"compression.zstd: {Colors.GREEN}Доступен{Colors.RESET}")
    except ImportError:
        print(
            f"compression.zstd: {Colors.YELLOW}Не найден (Python 3.14+){Colors.RESET}"
        )

    tests = [
        (
            "Граничные случаи",
            [
                test_empty_file,
                test_single_byte,
            ],
        ),
        (
            "Типы данных",
            [
                test_repetitive_data,
                test_random_data,
                test_mixed_content,
                test_unicode_text,
                test_all_bytes,
            ],
        ),
        (
            "Производительность",
            [
                test_large_file,
                test_compression_levels,
            ],
        ),
    ]

    total_tests = sum(len(group[1]) for group in tests)
    current_test = 0

    for group_name, test_funcs in tests:
        print_header(group_name)
        for test_func in test_funcs:
            current_test += 1
            print(f"\n[{current_test}/{total_tests}]", end=" ")
            try:
                test_func()
            except Exception as e:
                print_error(f"Критическая ошибка: {e}")

    print_header("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")


if __name__ == "__main__":
    main()
