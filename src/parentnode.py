from htmlnode import *

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props = None):
        super().__init__(tag = tag, children=children, props=props)
    
    def to_html(self):
        if self.tag is None:
            raise ValueError("no tag")
        if self.children is None:
            raise ValueError("no children")

        return f"<{self.tag}>{''.join(map(lambda child: child.to_html(), self.children))}</{self.tag}>"

