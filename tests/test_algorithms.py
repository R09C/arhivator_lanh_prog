import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from archiver.algorithms.huffman import HuffmanEncoder, HuffmanDecoder
from archiver.algorithms.lz77 import LZ77Compressor, LZ77Decompressor
from archiver.algorithms.bwt import BWT
from archiver.algorithms.mtf import MTF
from archiver.algorithms.rle import RLE


def test_huffman():
    print("\n>>> Huffman кодирование")
    
    data = b"abracadabra " * 10
    print(f"  {len(data)} байт")
    
    encoder = HuffmanEncoder()
    encoded, metadata = encoder.encode(data)
    print(f"  сжато до {len(encoded)} байт ({len(data) / len(encoded):.1f}x)")
    
    decoder = HuffmanDecoder()
    decoded = decoder.decode(encoded, metadata)
    
    if bytes(decoded) == data:
        print("  OK: работает")
        return True
    print("  FAIL: не совпадает")
    return False


def test_lz77():
    print("\n>>> LZ77 компрессия")
    
    data = b"abracadabra " * 100
    print(f"  {len(data)} байт")
    
    compressor = LZ77Compressor()
    compressed = compressor.compress(data)
    print(f"  {len(compressed)} элементов после LZ77")
    
    decompressed = LZ77Decompressor.decompress(compressed)
    
    if decompressed == data:
        print("  OK: работает")
        return True
    print("  FAIL: не совпадает")
    return False


def test_bwt():
    print("\n>>> BWT (Burrows-Wheeler)")
    
    data = b"banana"
    transformed, idx = BWT.transform(data)
    print(f"  {data} -> {transformed} (индекс {idx})")
    
    restored = BWT.inverse_transform(transformed, idx)
    
    if restored == data:
        print("  OK: работает")
        return True
    print("  FAIL: не совпадает")
    return False


def test_mtf():
    print("\n>>> MTF (Move-to-Front)")
    
    data = b"bananaaa"
    encoded = MTF.encode(data)
    print(f"  {data} -> {list(encoded)}")
    
    decoded = MTF.decode(encoded)
    
    if bytes(decoded) == data:
        print("  OK: работает")
        return True
    print("  FAIL: не совпадает")
    return False


def test_rle():
    print("\n>>> RLE (Run-Length Encoding)")
    
    data = b"aaabbbccccdddddeeeeeee"
    encoded = RLE.encode(data)
    print(f"  {len(data)} байт -> {len(encoded)} пар")
    
    decoded = RLE.decode(encoded)
    
    if bytes(decoded) == data:
        print("  OK: работает")
        return True
    print("  FAIL: не совпадает")
    return False


def test_bz2_pipeline():
    print("\n>>> BZ2 пайплайн (BWT->MTF->RLE->Huffman)")
    
    import pickle
    
    data = b"abracadabra " * 50
    print(f"  {len(data)} байт")
    
    bwt_data, bwt_idx = BWT.transform(data)
    mtf_data = MTF.encode(bwt_data)
    rle_data = RLE.encode(bytes(mtf_data))
    
    rle_bytes = pickle.dumps(rle_data)
    encoder = HuffmanEncoder()
    final, meta = encoder.encode(rle_bytes)
    print(f"  сжато до {len(final)} байт ({len(data) / len(final):.1f}x)")
    
    decoder = HuffmanDecoder()
    rle_bytes_back = decoder.decode(final, meta)
    rle_back = pickle.loads(bytes(rle_bytes_back))
    mtf_back = RLE.decode(rle_back)
    bwt_back = MTF.decode(bytes(mtf_back))
    result = BWT.inverse_transform(bytes(bwt_back), bwt_idx)
    
    if result == data:
        print("  OK: работает")
        return True
    print("  FAIL: не совпадает")
    return False


def test_zstd_pipeline():
    print("\n>>> ZSTD пайплайн (LZ77->Huffman)")
    
    import pickle
    
    data = b"abracadabra " * 100
    print(f"  {len(data)} байт")
    
    
    lz77 = LZ77Compressor(wnd_size=16384)
    lz77_out = lz77.compress(data)
    
    lz77_bytes = pickle.dumps(lz77_out)
    encoder = HuffmanEncoder()
    final, meta = encoder.encode(lz77_bytes)
    print(f"  сжато до {len(final)} байт ({len(data) / len(final):.1f}x)")
    
    
    decoder = HuffmanDecoder()
    lz77_bytes_back = decoder.decode(final, meta)
    lz77_back = pickle.loads(bytes(lz77_bytes_back))
    result = LZ77Decompressor.decompress(lz77_back)
    
    if result == data:
        print("  OK: работает")
        return True
    print("  FAIL: не совпадает")
    return False


def main():
    print("\n" + "="*50)
    print("Тесты алгоритмов сжатия")
    print("="*50)
    
    tests = {
        "Huffman": test_huffman(),
        "LZ77": test_lz77(),
        "BWT": test_bwt(),
        "MTF": test_mtf(),
        "RLE": test_rle(),
        "BZ2 полный": test_bz2_pipeline(),
        "ZSTD полный": test_zstd_pipeline(),
    }
    
    print("\n" + "-"*50)
    passed = sum(tests.values())
    total = len(tests)
    
    for name, ok in tests.items():
        status = "OK" if ok else "FAIL"
        print(f"  [{status}] {name}")
    
    print(f"\nИтого: {passed}/{total}")
    print("="*50)


if __name__ == "__main__":
    main()
