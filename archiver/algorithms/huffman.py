from typing import Dict, Tuple, Optional
from collections import Counter
import heapq
import pickle


class HuffmanNode:

    def __init__(self, char: Optional[int] = None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None


class HuffmanEncoder:

    def __init__(self):
        self.root: Optional[HuffmanNode] = None
        self.codes: dict = {}
        self.reverse_codes: dict = {}

    def build_frequency_table(self, data):
        return dict(Counter(data))

    def build_huffman_tree(self, freq) -> HuffmanNode:

        if not freq:
            return HuffmanNode()

        heap = [HuffmanNode(char=char, freq=freq) for char, freq in freq.items()]
        heapq.heapify(heap)

        if len(heap) == 1:
            node = heapq.heappop(heap)
            return HuffmanNode(freq=node.freq, left=node)

        while len(heap) > 1:
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            merged = HuffmanNode(freq=left.freq + right.freq, left=left, right=right)
            heapq.heappush(heap, merged)

        return heap[0]

    def generate_codes(self, node: HuffmanNode, code=""):

        if node is None:
            return

        if node.is_leaf():
            self.codes[node.char] = code if code else "0"
            self.reverse_codes[code if code else "0"] = node.char
            return

        self.generate_codes(node.left, code + "0")
        self.generate_codes(node.right, code + "1")

    def encode(self, data) -> Tuple[bytearray, Dict]:

        if len(data) == 0:
            return bytearray(), {}

        freq = self.build_frequency_table(data)
        self.root = self.build_huffman_tree(freq)
        self.codes = {}
        self.reverse_codes = {}
        self.generate_codes(self.root)
        bits = "".join(self.codes[byte] for byte in data)
        padding = (8 - len(bits) % 8) % 8
        bits += "0" * padding
        result = bytearray()

        for i in range(0, len(bits), 8):
            byte = bits[i : i + 8]
            result.append(int(byte, 2))

        meta = {
            "freq": freq,
            "padding": padding,
            "orig_size": len(data),
        }
        return result, meta


class HuffmanDecoder:

    def __init__(self):
        self.root: Optional[HuffmanNode] = None

    def build_tree_from_freq(self, freq) -> HuffmanNode:
        encoder = HuffmanEncoder()
        return encoder.build_huffman_tree(freq)

    def decode(self, enc_data, meta: Dict) -> bytearray:

        if not enc_data or not meta:
            return bytearray()

        freq = meta["freq"]
        padding = meta["padding"]
        orig_size = meta["orig_size"]
        self.root = self.build_tree_from_freq(freq)
        bits = "".join(format(byte, "08b") for byte in enc_data)

        if padding > 0:
            bits = bits[:-padding]

        dec = bytearray()
        node = self.root

        for bit in bits:

            if node.is_leaf():
                dec.append(node.char)

                if len(dec) >= orig_size:
                    break

                continue

            if bit == "0":
                node = node.left

            else:
                node = node.right

            if node.is_leaf():
                dec.append(node.char)
                node = self.root

                if len(dec) >= orig_size:
                    break

        return dec


def compress_with_huffman(data):
    encoder = HuffmanEncoder()
    enc_data, meta = encoder.encode(data)
    package = {"data": bytes(enc_data), "meta": meta}
    return pickle.dumps(package)


def decompress_with_huffman(data):
    package = pickle.loads(data)
    decoder = HuffmanDecoder()
    dec = decoder.decode(package["data"], package["meta"])
    return bytes(dec)
