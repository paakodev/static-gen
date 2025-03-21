
from typing import List, Self


class HTMLNode:
    def __init__(self, tag: str = None, value: str = None, children: List[Self] = None, props: dict = None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props or {}
    
    def to_html(self):
        raise NotImplementedError

    def props_to_html(self) -> str:
        if not self.props:
            return ""
        # Serialize props into key="value" format
        return " " + " ".join(f'{key}="{value}"' for key, value in self.props.items())
    
    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"