import time

class SolveLogger:
    def __init__(self):
        self.lines = []
        self.t0 = time.perf_counter()

    def _ts(self):
        return f"{(time.perf_counter() - self.t0):8.3f}s"

    def info(self, msg: str):
        self.lines.append(f"[{self._ts()}] {msg}")

    def section(self, title: str):
        self.lines.append("")
        self.lines.append(f"[{self._ts()}] === {title} ===")

    def dump_text(self) -> str:
        return "\n".join(self.lines) + "\n"
