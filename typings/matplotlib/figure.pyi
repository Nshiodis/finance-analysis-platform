"""本地最小类型 stub：matplotlib.figure.Figure（只覆盖项目用到的 savefig）。

savefig 的 dpi / bbox_inches 是项目实际使用的参数，写成真实类型；
其余属性参数（transparent / facecolor / format…）为动态属性 API，
保留 **kwargs: Any。
"""

from pathlib import Path
from typing import Any


class Figure:
    def savefig(
        self,
        fname: str | Path,
        dpi: float | None = None,
        bbox_inches: str | None = None,
        **kwargs: Any,
    ) -> None: ...
