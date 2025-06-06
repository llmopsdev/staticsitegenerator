from htmlnode import HTMLNode

class LeafNode(HTMLNode):
    def __init__(self, tag, value, props=None):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self):
        if self.tag == "img":
            attrs = self.props_to_html() or ""
            return f"<img{attrs}/>"
        if self.tag is None:
            if self.value is None:
                raise ValueError("value is none")
            return self.value
        if self.value is None:
            raise ValueError("value is none")
        return f"<{self.tag}>{self.value}</{self.tag}>"
