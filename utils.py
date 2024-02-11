import math


def formatBytes(bytes, decimals=2):
    if bytes == 0:
        return "0B"

    bytes = int(bytes)

    byte_factor = 1024
    dm = decimals if decimals >= 0 else 0
    sizes = ["B", "KB", "MB", "GB", "TB"]

    size_index = math.floor(math.log(bytes, byte_factor))

    return f"{round(bytes / math.pow(byte_factor, size_index), dm)} {sizes[size_index]}"
