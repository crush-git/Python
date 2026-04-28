"""扫描全仓库剩余的 ![](http*) 图片引用，输出按文件分组的报告。"""

import re
import sys
from collections import defaultdict
from pathlib import Path

IMG_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")


def main() -> int:
    root = Path("Article")
    by_file: dict[Path, list[str]] = defaultdict(list)
    for md in sorted(root.rglob("*.md")):
        for m in IMG_RE.finditer(md.read_text(encoding="utf-8")):
            by_file[md].append(m.group(1))

    if not by_file:
        print("无剩余 http(s) 图片引用 ✓")
        return 0

    total = sum(len(v) for v in by_file.values())
    print(f"剩余 {total} 个 http(s) 图片引用，分布在 {len(by_file)} 个文件：\n")
    for path, urls in sorted(by_file.items(), key=lambda kv: -len(kv[1])):
        print(f"  {len(urls):>3}  {path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
