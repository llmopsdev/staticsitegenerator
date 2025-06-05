class HTMLNode():
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        raise NotImplementedError

    def props_to_html(self):
        if self.props:
            res = ""
            for k, v in self.props.items():
                res += f" {k}=\"{v}\""
            return res
        return None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.tag}, {self.value}, children: {self.children}, {self.props})"

    def __eq__(self, other):
        return True if self.__dict__ == other.__dict__ else False
