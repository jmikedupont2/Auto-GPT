import atexit
import time

import yappi
from scalene import scalene_profiler

USE_SCALENE = False

def stop_profiler_before_exit():
    current_timestamp = int(time.time())
    if USE_SCALENE:
        scalene_profiler.stop()
        scalene_profiler.dump_stats(
            f"./logs/func_wall_stats_{current_timestamp}.profile"
        )
    else:
        yappi.stop()
        yappi.get_func_stats().save(
            f"./logs/func_wall_stats_{current_timestamp}.profile", type="pstat"
        )


def start_profiler():
    atexit.register(stop_profiler_before_exit)
    if USE_SCALENE:
        scalene_profiler.start()
    else:
        yappi.set_clock_type("wall")
        yappi.start()

