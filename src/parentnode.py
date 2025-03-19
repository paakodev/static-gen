from htmlnode import HTMLNode

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag, None, children, props)
    
    def to_html(self) -> str:
        if not self.tag:
            raise ValueError("ParentNode must have a tag")
        if not self.children:
            raise ValueError("ParentNode must have child nodes")
        
        children = ''.join([child.to_html() for child in self.children])
        if self.props:
            attributes = " ".join(f'{key}="{value}"' for key, value in self.props.items())
            attributes = f" {attributes}"
        else:
            attributes = ""
        return f"<{self.tag}{attributes}>{children}</{self.tag}>"