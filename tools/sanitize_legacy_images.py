"""把 _legacy_images/ 下所有图转成 Anthropic vision API 友好的格式：
   - RGB JPEG（去 indexed-color colormap）
   - 长边 ≤ 1024px
   - 输出到镜像目录 _legacy_images_safe/

   背景：原 _legacy_images 含 8-bit colormap PNG 和大尺寸图（>1500px），
   实测 API 会 400 'Could not process image'。统一转 RGB JPEG ≤1024px
   能让 API 100% 接受（已对 091204.png 单点实测确证）。

   用法：
       python tools/sanitize_legacy_images.py

   依赖：macOS 自带 sips（命令行 / scriptable image processing）。
"""

import subprocess
import sys
from pathlib import Path

SRC_ROOT = Path("_legacy_images")
DST_ROOT = Path("_legacy_images_safe")
MAX_DIM = 1024
JPEG_QUALITY = 80
EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def sanitize_one(src: Path, dst: Path) -> tuple[bool, str]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            [
                "sips",
                "-s", "format", "jpeg",
                "-s", "formatOptions", str(JPEG_QUALITY),
                "-Z", str(MAX_DIM),
                str(src),
                "--out", str(dst),
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or "sips returncode != 0"
        return True, ""
    except subprocess.TimeoutExpired:
        return False, "timeout 30s"
    except Exception as e:
        return False, str(e)


def main() -> int:
    if not SRC_ROOT.exists():
        print(f"源目录不存在：{SRC_ROOT}", file=sys.stderr)
        return 1

    files = sorted(p for p in SRC_ROOT.rglob("*") if p.is_file() and p.suffix.lower() in EXTS)
    print(f"待处理图片数：{len(files)}\n")

    ok = 0
    fail = 0
    failures: list[tuple[Path, str]] = []

    for src in files:
        rel = src.relative_to(SRC_ROOT)
        dst = DST_ROOT / rel.with_suffix(".jpg")
        success, err = sanitize_one(src, dst)
        if success:
            ok += 1
            print(f"OK   {rel}")
        else:
            fail += 1
            failures.append((rel, err))
            print(f"FAIL {rel}  ::  {err}", file=sys.stderr)

    print(f"\n完成：{ok} 成功 / {fail} 失败")
    if failures:
        print("\n失败明细：")
        for rel, err in failures:
            print(f"  {rel}  ::  {err}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
