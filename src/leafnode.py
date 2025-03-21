from htmlnode import HTMLNode

class LeafNode(HTMLNode):
    def __init__(self, tag: str, value: str, props: dict = None):
        super().__init__(tag, value, None, props)
    
    def to_html(self) -> str:
        if not self.value:
            raise ValueError("LeafNode cannot have empty value.")
        if self.tag is None:
            return self.value
        
        if self.props:
            attributes = " ".join(f'{key}="{value}"' for key, value in self.props.items())
            attributes = f" {attributes}"
        else:
            attributes = ""
        
        return f"<{self.tag}{attributes}>{self.value}</{self.tag}>"