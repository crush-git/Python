"""扫描 Article/**/*.md 提取所有图片 URL，下载到 _legacy_images/<相对路径>/<文件名>。

用法：
    python tools/download_legacy_images.py
"""

import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

IMG_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")


def main() -> int:
    root = Path("Article")
    out_root = Path("_legacy_images")
    out_root.mkdir(exist_ok=True)

    seen: dict[str, Path] = {}
    failed: list[tuple[str, str]] = []

    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root).with_suffix("")
        for m in IMG_RE.finditer(md.read_text(encoding="utf-8")):
            url = m.group(1)
            if url in seen:
                continue
            parsed = urlparse(url)
            fname = unquote(Path(parsed.path).name) or "untitled.png"
            local = out_root / rel / fname
            local.parent.mkdir(parents=True, exist_ok=True)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    local.write_bytes(resp.read())
                seen[url] = local
                print(f"OK   {url} -> {local}")
            except Exception as e:
                failed.append((url, str(e)))
                print(f"FAIL {url} ({e})", file=sys.stderr)

    print(f"\n下载完成：{len(seen)} 成功，{len(failed)} 失败")
    if failed:
        print("\n失败明细：")
        for url, err in failed:
            print(f"  {url}  ::  {err}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
