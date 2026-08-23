"""本地最小类型 stub：matplotlib.figure.Figure。"""

from pathlib import Path
from typing import Any


class Figure:
    def savefig(self, fname: str | Path, **kwargs: Any) -> None: ...
