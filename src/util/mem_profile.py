import os

import psutil


def memory_usage_psutil():
    """
    Get the current process memory usage in megabytes.

    Uses `psutil` to retrieve the resident set size (RSS) of the current process.

    Returns:
        float: Memory usage in MB.
    """
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 ** 2)
    return mem
