import atexit
import time

import yappi


def stop_profiler_before_exit():
    current_timestamp = int(time.time())
    yappi.stop()
    yappi.get_func_stats().save(
        f"./logs/func_wall_stats_{current_timestamp}.profile", type="pstat"
    )


def start_profiler():
    atexit.register(stop_profiler_before_exit)
    yappi.set_clock_type("wall")
    yappi.start()
