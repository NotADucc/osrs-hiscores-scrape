import os

import psutil


def memory_usage_psutil():
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 ** 2)
    return mem
