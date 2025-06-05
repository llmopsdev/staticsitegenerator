from enum import Enum
from leafnode import LeafNode
from extract_markdown_image_link import extract_markdown_links, extract_markdown_images

class TextType(Enum):
    NORMAL = "normal"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"
    TEXT = "text"

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
        case TextType.IMAGE:
            return LeafNode(tag="img", value=None, props={"src":text_node.url, "alt":text_node.text})


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
