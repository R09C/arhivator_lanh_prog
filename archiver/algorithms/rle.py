
class RLE:

    @staticmethod
    def encode(data) -> list:
        
        if not data:
            return []

        result = []
        i = 0

        while i < len(data):
            curr_byte = data[i]
            count = 1

            while (
                i + count < len(data)
                and data[i + count] == curr_byte
                and count < 255
            ):
                count += 1

            result.append((curr_byte, count))
            i += count

        return result

    @staticmethod
    def decode(enc_data: list) -> bytearray:
        result = bytearray()

        for byte, count in enc_data:
            result.extend([byte] * count)

        return result


    @staticmethod
    def encode_bytes(data):
        
        if not data:
            return b""

        encoded_list = RLE.encode(data)
        result = bytearray()

        for byte, count in encoded_list:
            result.append(byte)
            result.append(count)

        return bytes(result)

    @staticmethod
    def decode_bytes(enc_data):        
        if not enc_data or len(enc_data) % 2 != 0:
            return b""

        encoded_list = []
        for i in range(0, len(enc_data), 2):
            byte = enc_data[i]
            count = enc_data[i + 1]
            encoded_list.append((byte, count))

        return bytes(RLE.decode(encoded_list))


def apply_rle(data):
    return RLE.encode_bytes(data)

def reverse_rle(encoded: bytes):
    return RLE.decode_bytes(encoded)

