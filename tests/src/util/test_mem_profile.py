from src.util.mem_profile import memory_usage_psutil


def test_memory_usage_psutil_positive():
    assert memory_usage_psutil() > 0
