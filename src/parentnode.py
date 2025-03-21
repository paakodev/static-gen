from typing import List
from htmlnode import HTMLNode

class ParentNode(HTMLNode):
    def __init__(self, tag: str, children: List[HTMLNode], props: dict = None):
        super().__init__(tag, None, children, props)
        if not self.tag:
            raise ValueError("ParentNode must have a tag")
        if not self.children:
            raise ValueError("ParentNode must have child nodes")
    
    def to_html(self) -> str:        
        children = ''.join([child.to_html() for child in self.children])
        # Serialize properties
        props_string = self.props_to_html()
        
        return f"<{self.tag}{props_string}>{children}</{self.tag}>"