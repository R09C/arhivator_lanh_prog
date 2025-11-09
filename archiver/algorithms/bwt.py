class BWT:

    @staticmethod
    def transform(data):

        if len(data) == 0:
            return b"", 0

        n = len(data)
        rotations = []

        for i in range(n):
            rotations.append(data[i:] + data[:i])

        sorted_rot = sorted(enumerate(rotations), key=lambda x: x[1])
        result = bytearray()
        orig_idx = 0

        for i, (orig_i, rotation) in enumerate(sorted_rot):
            result.append(rotation[-1])
            if orig_i == 0:
                orig_idx = i

        return bytes(result), orig_idx

    @staticmethod
    def inverse_transform(bwt_data, orig_idx: int) -> bytes:

        if not bwt_data:
            return b""

        n = len(bwt_data)
        table = [(bwt_data[i], i) for i in range(n)]
        sorted_table = sorted(table)
        next_i = [0] * n

        for i in range(n):
            next_i[i] = sorted_table[i][1]

        result = bytearray()
        curr = orig_idx

        for _ in range(n):
            result.append(sorted_table[curr][0])
            curr = next_i[curr]

        return bytes(result)


def apply_bwt(data):
    return BWT.transform(data)


def reverse_bwt(bwt_data, index: int) -> bytes:
    return BWT.inverse_transform(bwt_data, index)
