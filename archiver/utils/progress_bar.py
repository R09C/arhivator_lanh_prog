

import sys
import time

class ProgressBar:
    

    def __init__(self, total: int = 100, width: int = 50, desc: str = "Progress"):
        self.total = total
        self.width = width
        self.desc = desc
        self.current = 0
        self.start_time = time.time()

    def update(self, current: int, total: int = None):

        if total is not None:
            self.total = total

        self.current = current
        self._display()

    def _display(self):
        
        if self.total == 0:
            percent = 0

        else:
            percent = min(100, (self.current / self.total) * 100)

        filled = int(self.width * self.current // max(1, self.total))
        bar = "#" * filled + "-" * (self.width - filled)
        elapsed = time.time() - self.start_time

        if self.current > 0 and self.total > 0:
            eta = elapsed * (self.total - self.current) / self.current
            eta_str = self._format_time(eta)

        else:
            eta_str = "?"

        elapsed_str = self._format_time(elapsed)
        current_size = self._format_size(self.current)
        total_size = self._format_size(self.total)
        sys.stdout.write(
            f"\r{self.desc}: |{bar}| {percent:>5.1f}% "
            f"[{current_size}/{total_size}] "
            f"Время: {elapsed_str} Осталось: {eta_str}"
        )
        sys.stdout.flush()

        if self.current >= self.total:
            sys.stdout.write("\n")
            sys.stdout.flush()

    @staticmethod
    def _format_time(seconds: float) -> str:
        
        if seconds < 60:
            return f"{seconds:.1f}s"
        
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"

    @staticmethod
    def _format_size(size: int) -> str:
        
        for unit in ["B", "KB", "MB", "GB", "TB"]:

            if size < 1024.0:
                return f"{size:.1f}{unit}"
            
            size /= 1024.0
            
        return f"{size:.1f}PB"

    def close(self):
        
        if self.current < self.total:
            self.current = self.total
            self._display()
