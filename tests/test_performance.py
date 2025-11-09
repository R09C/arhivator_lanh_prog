import os
import sys
import time
import statistics

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from archiver.factory import ArchiveFactory


def kb(size):
    return f"{size / 1024:.1f} КБ"

def speed(bps):
    if bps < 1024 * 1024:
        return f"{bps / 1024:.0f} КБ/с"
    return f"{bps / (1024 * 1024):.1f} МБ/с"


def create_test_file(filename, size_kb, pattern="text"):
    if pattern == "text":
        data = (
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
        ).encode()
        data = (data * (size_kb * 1024 // len(data) + 1))[: size_kb * 1024]
    elif pattern == "repetitive":
        data = b"AAAA" * (size_kb * 256)
    elif pattern == "random":
        data = os.urandom(size_kb * 1024)
    elif pattern == "structured":
        chunks = []
        for i in range(size_kb):
            chunks.append(f"Block-{i:06d}:".encode() + b"X" * 1000)
        data = b"".join(chunks)
    elif pattern == "mixed":
        text = ("Text block " * 50).encode()
        binary = bytes(range(256))
        data = (text + binary) * (size_kb * 1024 // (len(text) + len(binary)) + 1)
        data = data[: size_kb * 1024]

    with open(filename, "wb") as f:
        f.write(data)

    return len(data)


def benchmark_compression(test_file, original_size, fmt, impl, level, iterations=3):
    results = {
        "compress_times": [],
        "decompress_times": [],
        "archive_sizes": [],
        "compress_speeds": [],
        "decompress_speeds": [],
    }

    archive = f"bench_temp{fmt}"
    output = f"bench_temp_out.bin"

    for i in range(iterations):
        try:

            comp = ArchiveFactory.get_compressor(
                archive, level=level, implementation=impl
            )
            start = time.perf_counter()
            comp.compress_file(test_file, archive)
            compress_time = time.perf_counter() - start

            archive_size = os.path.getsize(archive)
            compress_speed = original_size / compress_time if compress_time > 0 else 0

            decomp = ArchiveFactory.get_decompressor(archive, implementation=impl)
            start = time.perf_counter()
            decomp.decompress_file(archive, output)
            decompress_time = time.perf_counter() - start

            decompress_speed = (
                original_size / decompress_time if decompress_time > 0 else 0
            )

            results["compress_times"].append(compress_time)
            results["decompress_times"].append(decompress_time)
            results["archive_sizes"].append(archive_size)
            results["compress_speeds"].append(compress_speed)
            results["decompress_speeds"].append(decompress_speed)

            if os.path.exists(output):
                os.remove(output)
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
        finally:
            if os.path.exists(archive):
                os.remove(archive)

    return {
        "avg_compress_time": statistics.mean(results["compress_times"]),
        "avg_decompress_time": statistics.mean(results["decompress_times"]),
        "avg_compress_speed": statistics.mean(results["compress_speeds"]),
        "avg_decompress_speed": statistics.mean(results["decompress_speeds"]),
        "archive_size": results["archive_sizes"][0],
        "compression_ratio": (1 - results["archive_sizes"][0] / original_size) * 100,
        "min_compress_time": min(results["compress_times"]),
        "max_compress_time": max(results["compress_times"]),
        "std_compress_time": (
            statistics.stdev(results["compress_times"])
            if len(results["compress_times"]) > 1
            else 0
        ),
    }


def test_size_scaling():
    print("\n>>> Тест: как размер файла влияет на скорость")
    
    sizes = [10, 50, 100, 500] 
    
    for size in sizes:
        test_file = f"test_{size}kb.bin"
        original = create_test_file(test_file, size, "text")
        
        print(f"\n  Файл {kb(original)}:")
        
        for fmt in [".zst", ".bz2"]:
            for impl in ["custom", "stdlib"]:
                result = benchmark_compression(test_file, original, fmt, impl, 9, iterations=2)
                
                if result:
                    print(f"    {impl:7} {fmt}: {speed(result['avg_compress_speed']):>8} сжатие, "
                          f"{speed(result['avg_decompress_speed']):>8} распаковка, "
                          f"{result['compression_ratio']:.0f}% сжато")
        
        os.remove(test_file)


def test_compression_levels():
    print("\n>>> Тест: как уровень сжатия влияет на время")
    
    test_file = "test_levels.bin"
    original = create_test_file(test_file, 300, "text")
    
    for impl in ["custom", "stdlib"]:
        print(f"\n  {impl}:")
        for level in [1, 5, 9]:
            times = []
            for fmt in [".zst", ".bz2"]:
                r = benchmark_compression(test_file, original, fmt, impl, level, iterations=2)
                if r:
                    times.append(f"{fmt} {r['avg_compress_time']*1000:.0f}мс")
            print(f"    уровень {level}: {', '.join(times)}")
    
    os.remove(test_file)


def test_data_patterns():
    print("\n>>> Тест: разные типы данных")
    
    patterns = {
        "text": "текст",
        "repetitive": "повторы",
        "random": "случайное",
        "mixed": "смешанное"
    }
    
    for pattern, name in patterns.items():
        test_file = f"test_{pattern}.bin"
        original = create_test_file(test_file, 150, pattern)
        
        print(f"\n  {name} ({kb(original)}):")
        for fmt in [".zst", ".bz2"]:
            r_custom = benchmark_compression(test_file, original, fmt, "custom", 9, iterations=1)
            r_stdlib = benchmark_compression(test_file, original, fmt, "stdlib", 9, iterations=1)
            
            if r_custom and r_stdlib:
                print(f"    {fmt}: {r_custom['compression_ratio']:.0f}% сжатие, "
                      f"stdlib быстрее в {r_custom['avg_compress_time']/r_stdlib['avg_compress_time']:.1f}x")
        
        os.remove(test_file)


def test_big_file():
    print("\n>>> Тест: большой файл (1.5 МБ)")
    
    test_file = "test_big.bin"
    original = create_test_file(test_file, 1500, "mixed")
    
    print(f"\n  Сравнение скоростей:")
    for fmt in [".zst", ".bz2"]:
        for impl in ["custom", "stdlib"]:
            r = benchmark_compression(test_file, original, fmt, impl, 9, iterations=2)
            if r:
                print(f"    {impl:7} {fmt}: {speed(r['avg_compress_speed'])} -> {speed(r['avg_decompress_speed'])}")
    
    os.remove(test_file)


def test_stability():
    print("\n>>> Тест: стабильность времени (8 прогонов)")
    
    test_file = "test_stable.bin"
    original = create_test_file(test_file, 100, "text")
    
    for impl in ["custom", "stdlib"]:
        print(f"\n  {impl}:")
        for fmt in [".zst", ".bz2"]:
            times = []
            archive = f"temp{fmt}"
            
            for _ in range(8):
                comp = ArchiveFactory.get_compressor(archive, level=9, implementation=impl)
                start = time.perf_counter()
                comp.compress_file(test_file, archive)
                times.append((time.perf_counter() - start) * 1000)
                if os.path.exists(archive):
                    os.remove(archive)
            
            avg = statistics.mean(times)
            std = statistics.stdev(times) if len(times) > 1 else 0
            print(f"    {fmt}: {avg:.1f}мс ±{std:.1f}мс")
    
    os.remove(test_file)


def test_direct_comparison():
    print("\n>>> Тест: custom vs stdlib напрямую")
    
    test_file = "test_comp.bin"
    original = create_test_file(test_file, 400, "text")
    
    print(f"\n  Файл {kb(original)}, уровень 9, 3 прогона:")
    
    for fmt in [".zst", ".bz2"]:
        r_custom = benchmark_compression(test_file, original, fmt, "custom", 9, iterations=3)
        r_stdlib = benchmark_compression(test_file, original, fmt, "stdlib", 9, iterations=3)
        
        if r_custom and r_stdlib:
            speedup = r_custom['avg_compress_time'] / r_stdlib['avg_compress_time']
            print(f"\n    {fmt}:")
            print(f"      сжатие:    custom {r_custom['avg_compress_time']*1000:.0f}мс vs stdlib {r_stdlib['avg_compress_time']*1000:.0f}мс (stdlib в {speedup:.1f}x быстрее)")
            print(f"      размер:    {kb(r_custom['archive_size'])} vs {kb(r_stdlib['archive_size'])}")
            print(f"      степень:   {r_custom['compression_ratio']:.1f}% vs {r_stdlib['compression_ratio']:.1f}%")
    
    os.remove(test_file)


def main():
    print("\n" + "="*60)
    print("Тесты производительности архиватора")
    print("="*60)
    print(f"Python {sys.version.split()[0]}")
    
    try:
        from compression import zstd
        print("compression.zstd: есть")
    except ImportError:
        print("compression.zstd: нет")
    
    print("\n5 тестов:")
    
    tests = [
        test_size_scaling,
        test_compression_levels,
        test_data_patterns,
        test_big_file,
        test_stability,
        test_direct_comparison,
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"\n!!! Ошибка: {e}")
    
    print("\n" + "="*60)
    print("Готово")
    print("="*60)


if __name__ == "__main__":
    main()
