from pathlib import Path
from textnode import markdown_to_html_node
from title import extract_title

def generate_page(from_path: str, template_path: str, dest_path: str) -> None:
    print(f"Generating page from {from_path} → {dest_path} using {template_path}")
    markdown = Path(from_path).read_text(encoding="utf-8")
    template = Path(template_path).read_text(encoding="utf-8")
    content_html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    page_html = (
        template
        .replace("{{ Title }}", title)
        .replace("{{ Content }}", content_html)
    )
    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page_html, encoding="utf-8")
