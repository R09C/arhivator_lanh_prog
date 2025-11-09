

import time
from functools import wraps
from typing import Callable, Any, Tuple

class Benchmark:
    

    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.elapsed = None

    def start(self):
        self.start_time = time.time()
        self.end_time = None
        self.elapsed = None

    def stop(self):
        
        if self.start_time is None:
            raise RuntimeError("Бенчмарк не был запущен")

        self.end_time = time.time()
        self.elapsed = self.end_time - self.start_time
        return self.elapsed

    def get_elapsed(self) -> float:
        
        if self.elapsed is None:
            raise RuntimeError("Бенчмарк не был остановлен")
        
        return self.elapsed

    def format_elapsed(self) -> str:
        elapsed = self.get_elapsed()
        return format_time(elapsed)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        return False

def benchmark(func: Callable) -> Callable:

    @wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[Any, float]:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed

    return wrapper

def format_time(seconds: float) -> str:
    
    if seconds < 0.001:
        return f"{seconds * 1000000:.2f} мкс"
    
    elif seconds < 1:
        return f"{seconds * 1000:.2f} мс"
    
    elif seconds < 60:
        return f"{seconds:.2f} с"
        
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = seconds % 60
        return f"{minutes} мин {secs:.2f} с"
    
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        secs = seconds % 60
        return f"{hours} ч {minutes} мин {secs:.0f} с"

def measure_operation(operation_name: str, func: Callable, *args, **kwargs) -> Any:
    print(f"\n{'='*60}")
    print(f"Начало: {operation_name}")
    print(f"{'='*60}")

    with Benchmark() as bench:
        result = func(*args, **kwargs)

    print(f"\n{'='*60}")
    print(f"Завершено: {operation_name}")
    print(f"Затраченное время: {bench.format_elapsed()}")
    print(f"{'='*60}\n")
    return result
