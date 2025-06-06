import shutil
import sys
from pathlib import Path
from generator import generate_page

SRC_STATIC = Path("static")
DEST_PUBLIC = Path("public")

def _clear_destination(dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True, exist_ok=True)

def _copy_recursive(src: Path, dest: Path) -> None:
    for item in src.iterdir():
        src_path = item
        dest_path = dest / item.name
        if item.is_dir():
            dest_path.mkdir(exist_ok=True)
            _copy_recursive(src_path, dest_path)
        else:
            shutil.copy2(src_path, dest_path)
            print(f"Copied {src_path} -> {dest_path}")

def main() -> None:
    _clear_destination(DEST_PUBLIC)
    _copy_recursive(SRC_STATIC, DEST_PUBLIC)
    generate_page(
        from_path="content/index.md",
        template_path="template.html",
        dest_path=DEST_PUBLIC / "index.html",
    )

if __name__ == "__main__":
    main()
