class LZ77Compressor:

    def __init__(self, wnd_size=32768, lookahead=258):
        self.wnd_size = wnd_size
        self.lookahead = lookahead
        self.minlen = 3

    def compress(self, data):
        if len(data) == 0:
            return []

        data = bytearray(data)
        result = []
        dictionary = (
            {}
        )  # добавлено для того  чтобы оптимизировать поиск по скользящему окну, потому что перебор по всему окну слишком долгий
        i = 0

        while i < len(data):
            if i + self.minlen > len(data):
                result.extend(data[i:])
                break

            sequence = bytes(data[i : i + self.minlen])
            match_pos = None
            match_len = 0

            if sequence in dictionary:
                for pos in dictionary[sequence]:

                    if i - pos > self.wnd_size:
                        continue # окно вообще здесь оставленно чтобы смещение не привышало вес самой последовательности 

                    length = self.minlen
                    max_length = min(self.lookahead, len(data) - i)

                    while (
                        length < max_length and data[i + length] == data[pos + length]
                    ):
                        length += 1

                    if length > match_len:
                        match_len = length
                        match_pos = pos

            if match_len >= self.minlen:
                offset = i - match_pos
                result.append((offset, match_len))

                for j in range(match_len):

                    if i + j + self.minlen <= len(data):
                        subseq = bytes(data[i + j : i + j + self.minlen])

                        if subseq not in dictionary:
                            dictionary[subseq] = []
                        dictionary[subseq].append(i + j)

                i += match_len

            else:
                result.append(data[i])

                if sequence not in dictionary:
                    dictionary[sequence] = []

                dictionary[sequence].append(i)
                i += 1

            if i % 1000 == 0: # тут в идеале надо имперически подбирать после какого количества итераций очищать словарь 
                self._cleanup_dictionary(dictionary, i)

        return result

    def _cleanup_dictionary(self, dictionary: dict, curr_pos: int):
        keys_to_remove = []
        for key, positions in dictionary.items():
            valid_positions = [
                pos for pos in positions if curr_pos - pos <= self.wnd_size
            ]

            if valid_positions:
                dictionary[key] = valid_positions

            else:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del dictionary[key]


class LZ77Decompressor:
    @staticmethod
    def decompress(data_data: list) -> bytearray:
        result = bytearray()

        for item in data_data:

            if isinstance(item, tuple):
                offset, length = item
                position = len(result) - offset

                for i in range(length):
                    result.append(result[position + i])

            else:
                result.append(item)

        return result


def compress_lz77(data, wnd_size=32768):
    compressor = LZ77Compressor(wnd_size=wnd_size)
    return compressor.compress(data)


def decompress_lz77(data: list) -> bytes:
    return bytes(LZ77Decompressor.decompress(data))
