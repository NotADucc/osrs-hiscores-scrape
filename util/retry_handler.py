import threading

from time import sleep

file_lock = threading.Lock()
def retry(callback, *args, max_retries=5, initial_delay=10, out_file="error_log"):
    retries = 1
    while retries <= max_retries:
        try:
            return callback(*args)
        except Exception as err:
            print(f"Attempt {retries} failed: {err}")
            sleep(retries * initial_delay)
            retries += 1

    with file_lock:
        with open(out_file + '.err', "a") as f:
            f.write(f"{','.join(map(str, args))} - {callback}\n")
    print(f"Max retries reached for {callback}. Error logged.")
    return None
