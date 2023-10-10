import time

def timing(func):
    def wrapper(*args, **kwargs):
        start_time  = time.time()
        result      = func(*args, **kwargs)
        end_time    = time.time()
        return ( result , (end_time - start_time) * 1000 )
    return wrapper
