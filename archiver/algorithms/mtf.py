

class MTF:
    

    @staticmethod
    def encode(data) -> bytearray:

        if not data:
            return bytearray()

        symbols = list(range(256))
        result = bytearray()

        for byte in data:
            index = symbols.index(byte)
            result.append(index)
            symbols.pop(index)
            symbols.insert(0, byte)

        return result

    @staticmethod
    def decode(enc_data) -> bytearray:
        
        if not enc_data:
            return bytearray()

        symbols = list(range(256))
        result = bytearray()

        for index in enc_data:
            byte = symbols[index]
            result.append(byte)
            symbols.pop(index)
            symbols.insert(0, byte)

        return result

def apply_mtf(data):
    return bytes(MTF.encode(data))

def reverse_mtf(encoded: bytes):
    return bytes(MTF.decode(encoded))

