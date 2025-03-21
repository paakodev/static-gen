from htmlnode import HTMLNode

# These tags are void elements in HTML, meaning they do not have inner content (`value`)
# and must rely on attributes like `src` (for `<img>`) or their mere presence (like `<hr>`, `<br>`).
ALLOWED_EMPTY_VALUE_TAGS = {"img", "hr", "br", "input", "meta", "link", "source", "track", "area", "embed"}

# Specific subset of tags with required properties
MD_REQUIRED_PROPERTIES = {
    "img": {"src"},  # `alt` might be optional, depending on your requirements.
    "a": {"href"},   # Links should always have an `href`.
}

class LeafNode(HTMLNode):
    def __init__(self, tag: str, value: str, props: dict = None):
        super().__init__(tag, value, None, props)
        # Only apply validation to relevant tags
        required_props = MD_REQUIRED_PROPERTIES.get(self.tag, set())
        for prop in required_props:
            if prop not in self.props:
                raise ValueError(f"'{self.tag}' must have '{prop}' property in markdown-to-HTML.")
        
        # Validate value on creation instead of in to_html
        if not self.value and self.tag not in ALLOWED_EMPTY_VALUE_TAGS:
            raise ValueError(f"'{self.tag}' cannot have an empty value.")

    
    def to_html(self) -> str:
        if self.tag is None:
            return self.value
        
        props_string = self.props_to_html()
        if self.tag in ALLOWED_EMPTY_VALUE_TAGS:
            return f"<{self.tag}{props_string} />"

        return f"<{self.tag}{props_string}>{self.value}</{self.tag}>"