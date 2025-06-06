import re
from enum import Enum


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered list"
    ORDERED_LIST = "ordered list"

    
def block_to_block_type(text: str) -> BlockType:
    if re.match(r'^#{1,6}\s', text):
        return BlockType.HEADING
    if text.startswith('```') and text.endswith('```'):
        return BlockType.CODE
    if all(line.startswith('> ') for line in text.splitlines()):
        return BlockType.QUOTE
    if all(line.strip().startswith('- ') for line in text.splitlines()):
        return BlockType.UNORDERED_LIST
    if re.match(r'^\d+\.\s', text) and all(re.match(r'^\d+\.\s', line.strip()) for line in text.splitlines()):
        return BlockType.ORDERED_LIST
    if all(
            (not line.strip()) or line.lstrip().startswith(">")
            for line in text.splitlines()
        ):
            return BlockType.QUOTE
    
    return BlockType.PARAGRAPH
