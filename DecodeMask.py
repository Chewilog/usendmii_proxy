import time

def apply_mask(data, mask):

    size = len(data)
    decoded_data =bytearray(size)
    count = 0

    for i in range(size):
        dec_data_unit = data[i] ^ mask[i % 4]
        if dec_data_unit == 125:
            count += 1
            decoded_data[i] = dec_data_unit
            if count == 2:
                count = 0
                break

        else:
            decoded_data[i] = dec_data_unit

    return decoded_data