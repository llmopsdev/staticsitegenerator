from enum import Enum
from leafnode import LeafNode
from extract_markdown_image_link import extract_markdown_links, extract_markdown_images
from blocktype import block_to_block_type, BlockType
from parentnode import ParentNode

class TextType(Enum):
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"
    PARAGRAPH = "paragraph"

class TextNode():
    def __init__(self,text, text_type, url=None):
        self.text = text
        self.text_type = TextType(text_type)
        self.url = url
    def __eq__(self,other):
        return True if self.__dict__ == other.__dict__ else False
    def __repr__(self):
        return f"{self.__class__.__name__}({self.text}, {self.text_type.value}, {self.url})"

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None, value=text_node.text)
        case TextType.BOLD:
            return LeafNode(tag="b", value=text_node.text)
        case TextType.ITALIC:
            return LeafNode(tag="i", value=text_node.text)
        case TextType.CODE:
            return LeafNode(tag="code", value=text_node.text)
        case TextType.LINK:
            return LeafNode(tag="a", value=text_node.text)
        case TextType.PARAGRAPH:
            return LeafNode(tag="p", value=text_node.text)
        case TextType.IMAGE:
            return LeafNode(tag="img", value=None, props={"src":text_node.url, "alt":text_node.text})
        case TextType.LINK:
            return LeafNode(tag="a", value=text_node.text,
                            props={"href": text_node.url})


def split_nodes_delimiter(old_nodes, delimiter, inside_type):
    result = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue

        parts = node.text.split(delimiter)

        if len(parts) % 2 == 0:
            raise ValueError(f"Unmatched delimiter {delimiter!r} in {node.text!r}")

        for i, part in enumerate(parts):
            if not part:
                continue
            node_type = inside_type if i % 2 else TextType.TEXT
            result.append(TextNode(part, node_type))

    return result

def split_nodes_images(old_nodes):
    result = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue
        text_or_image = extract_markdown_images(node.text)
        if not text_or_image and ("![" in node.text):
            raise ValueError("Malformed image markdown")
        if not text_or_image:
            result.append(node)
            continue
        working_text = node.text
        for alt, url in text_or_image:
            token = f"![{alt}]({url})"

            before, after = working_text.split(token, 1)

            if before:
                result.append(TextNode(before, TextType.TEXT))

            result.append(TextNode(alt, TextType.IMAGE, url))

            working_text = after
        if working_text:
            result.append(TextNode(working_text, TextType.TEXT))
    return result

def split_nodes_links(old_nodes):
    result = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue

        link_tuples = extract_markdown_links(node.text)

        if not link_tuples and ("[" in node.text and "](" in node.text):
            raise ValueError("Malformed link markdown")

        if not link_tuples: 
            result.append(node)
            continue

        working_text = node.text
        for label, url in link_tuples:
            token = f"[{label}]({url})"

            before, working_text = working_text.split(token, 1)

            if before:
                result.append(TextNode(before, TextType.TEXT))

            result.append(TextNode(label, TextType.LINK, url))

        if working_text: 
            result.append(TextNode(working_text, TextType.TEXT))

    return result


def text_to_textnodes(text):
    nodes: list[TextNode] = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_images(nodes)
    nodes = split_nodes_links(nodes)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    return [n for n in nodes if n.text != ""]

def markdown_to_blocks(text):
    res = []
    res = text.strip().split("\n\n")
    for r in res:
        if r is None:
            del r
        r.strip()
    res = [r for r in res if r]
    return res


def _dedent(text: str) -> str:
    lines = text.splitlines()
    non_empty = [len(l) - len(l.lstrip()) for l in lines if l.strip()]
    if not non_empty:
        return text
    pad = min(non_empty)
    return "\n".join(l[pad:] if len(l) >= pad else l for l in lines)

def markdown_to_blocks(text: str) -> list[str]:
    text = _dedent(text).strip("\n")
    return [b.strip() for b in text.split("\n\n") if b.strip()]

def _paragraph(block: str) -> ParentNode:
    plain = " ".join(l.strip() for l in block.splitlines())
    return ParentNode("p", [text_node_to_html_node(n) for n in text_to_textnodes(plain)])

def _heading(block: str) -> ParentNode:
    level, txt = block.split(" ", 1)
    tag = f"h{len(level)}"
    return ParentNode(tag, [text_node_to_html_node(n) for n in text_to_textnodes(txt.strip())])

def _code(block: str) -> ParentNode:
    lines = block.splitlines()[1:-1]  
    body  = "\n".join(lines)
    body  = _dedent(body)            
    if not body.endswith("\n"):     
        body += "\n"
    return ParentNode("pre", [LeafNode("code", body)])

def _quote(block: str) -> ParentNode:
    inner_lines = []
    for line in block.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(">"):
            stripped = stripped[1:]
            if stripped.startswith(" "):
                stripped = stripped[1:]
        inner_lines.append(stripped)
    inner = "\n".join(inner_lines)
    children = [text_node_to_html_node(n) for n in text_to_textnodes(inner)]
    return ParentNode("blockquote", children)

def _ul(block: str) -> ParentNode:
    items = []
    for l in block.splitlines():
        txt = l.lstrip().lstrip("- ").rstrip()
        items.append(ParentNode("li", [text_node_to_html_node(n) for n in text_to_textnodes(txt)]))
    return ParentNode("ul", items)

def _ol(block: str) -> ParentNode:
    items = []
    for l in block.splitlines():
        txt = l.lstrip().split(". ", 1)[1]
        items.append(ParentNode("li", [text_node_to_html_node(n) for n in text_to_textnodes(txt)]))
    return ParentNode("ol", items)

_DISPATCH = {
    BlockType.PARAGRAPH: _paragraph,
    BlockType.HEADING: _heading,
    BlockType.CODE: _code,
    BlockType.QUOTE: _quote,
    BlockType.UNORDERED_LIST: _ul,
    BlockType.ORDERED_LIST: _ol,
}

def markdown_to_html_node(markdown: str) -> ParentNode:
    nodes = []
    for block in markdown_to_blocks(markdown):
        nodes.append(_DISPATCH[block_to_block_type(block)](block))
    return ParentNode("div", nodes)
