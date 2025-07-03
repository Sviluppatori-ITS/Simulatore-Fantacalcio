import os

COUNTER_FILE = os.path.join(os.path.dirname(__file__), "data_files/test_run_counter.txt")


def increment_test_counter():
    os.makedirs(os.path.dirname(COUNTER_FILE), exist_ok=True)

    try:
        with open(COUNTER_FILE, "r") as f:
            value = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        value = 0

    value += 1

    with open(COUNTER_FILE, "w") as f:
        f.write(str(value))

    return value
