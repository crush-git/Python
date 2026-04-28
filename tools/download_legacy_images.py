"""扫描 Article/**/*.md 提取所有图片 URL，下载到 _legacy_images/<相对路径>/<文件名>。

特性：
- 下载完用 magic bytes 校验（PNG/JPEG/GIF/WebP），不通过的算失败
- 单 URL 失败重试 1 次
- 已存在且校验通过的跳过（断点续传）
- 失败 URL 列表写到 _legacy_images/_failed.txt
- --validate 模式：不下载，只校验现有 _legacy_images/ 中的所有图，损坏的列出来

用法：
    python tools/download_legacy_images.py            # 下载 + 校验
    python tools/download_legacy_images.py --validate # 只校验已下载的
    python tools/download_legacy_images.py --redo     # 删除现有重新下载
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import unquote, urlparse

IMG_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)]+)\)")


def detect_image_kind(path: Path) -> str | None:
    """返回 'png'/'jpeg'/'gif'/'webp' 或 None（不是合法图片）。"""
    try:
        head = path.read_bytes()[:16]
    except Exception:
        return None
    if len(head) < 12:
        return None
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head[:4] == b"GIF8":
        return "gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None


def download_one(url: str, local: Path, timeout: int = 15) -> tuple[bool, str]:
    """下载并校验。返回 (是否成功, 错误描述)。"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            local.write_bytes(resp.read())
    except Exception as e:
        return False, f"download failed: {e}"
    kind = detect_image_kind(local)
    if kind is None:
        local.unlink(missing_ok=True)
        return False, "downloaded file is not a valid image (magic bytes check failed)"
    return True, kind


def scan_urls() -> list[tuple[Path, str]]:
    """扫描所有 markdown，返回 [(目标本地路径, URL), ...]。"""
    root = Path("Article")
    out_root = Path("_legacy_images")
    out_root.mkdir(exist_ok=True)
    seen: dict[str, Path] = {}
    pairs: list[tuple[Path, str]] = []
    for md in sorted(root.rglob("*.md")):
        rel = md.relative_to(root).with_suffix("")
        for m in IMG_RE.finditer(md.read_text(encoding="utf-8")):
            url = m.group(1)
            if url in seen:
                continue
            parsed = urlparse(url)
            fname = unquote(Path(parsed.path).name) or "untitled.png"
            local = out_root / rel / fname
            seen[url] = local
            pairs.append((local, url))
    return pairs


def cmd_download(redo: bool = False) -> int:
    pairs = scan_urls()
    print(f"扫描到 {len(pairs)} 个 URL")
    skipped = 0
    succeeded = 0
    failed: list[tuple[str, str]] = []
    for local, url in pairs:
        local.parent.mkdir(parents=True, exist_ok=True)
        if local.exists() and not redo:
            if detect_image_kind(local):
                skipped += 1
                continue
            print(f"REDO {local}（旧文件不是合法图片，重新下载）")
        ok, info = download_one(url, local)
        if not ok:
            ok2, info2 = download_one(url, local)
            if not ok2:
                failed.append((url, f"{info}; retry: {info2}"))
                print(f"FAIL {url} -> {info2}", file=sys.stderr)
                continue
            info = info2
        succeeded += 1
        print(f"OK   {url} -> {local} ({info})")

    print(f"\n下载完成：跳过 {skipped}，新下载 {succeeded}，失败 {len(failed)}")
    if failed:
        out = Path("_legacy_images/_failed.txt")
        out.write_text("\n".join(f"{u}  ::  {e}" for u, e in failed), encoding="utf-8")
        print(f"失败明细已写到 {out}")
    return 1 if failed else 0


def cmd_validate() -> int:
    pairs = scan_urls()
    bad: list[Path] = []
    missing: list[Path] = []
    for local, url in pairs:
        if not local.exists():
            missing.append(local)
            continue
        if detect_image_kind(local) is None:
            bad.append(local)
    print(f"扫描到 {len(pairs)} 个 URL，缺失 {len(missing)}，损坏 {len(bad)}")
    for p in bad:
        print(f"  BAD     {p}")
    for p in missing[:20]:
        print(f"  MISSING {p}")
    if len(missing) > 20:
        print(f"  ... 共 {len(missing)} 个缺失")
    return 1 if bad or missing else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="只校验，不下载")
    parser.add_argument("--redo", action="store_true", help="无视已有文件重新下载")
    args = parser.parse_args()
    if args.validate:
        return cmd_validate()
    return cmd_download(redo=args.redo)


if __name__ == "__main__":
    sys.exit(main())
