import time
def retry_call(fn, max_attempts=3, delay=1.0):
    last_error = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            last_error = e
            if attempt < max_attempts - 1:
                time.sleep(delay * (attempt + 1))
    raise last_error
