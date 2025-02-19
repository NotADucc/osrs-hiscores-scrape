from time import sleep


def retry(callback, *args, max_retries=3, delay=10, out_file="error_log"):
    retries = 0
    while retries < max_retries:
        try:
            return callback(*args)
        except Exception as err:
            retries += 1
            if retries < max_retries:
                print(f"Attempt {retries} failed: {err}")
                sleep(delay)
            else:
                with open(out_file + '.err', "a") as f:
                    f.write(f"{','.join(args)}\n")
                print("Max retries reached. Error logged.")
                return None
