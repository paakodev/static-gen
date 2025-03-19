from textnode import TextNode, TextType
import re

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if node.text_type is not TextType.TEXT:
            new_nodes.append(node)
            continue
        
        chunks = node.text.split(delimiter, maxsplit=2)
         # If no split occurred, the delimiter was not found, so add the node unchanged
        if len(chunks) == 1:
            new_nodes.append(node)
            continue

        # If we don't have exactly 3 parts, it's an invalid Markdown case
        if len(chunks) != 3:
            raise ValueError("Invalid Markdown: missing or unmatched delimiters")
        
        new_nodes.append(TextNode(chunks[0], TextType.TEXT))
        new_nodes.append(TextNode(chunks[1], text_type))
        new_nodes.append(TextNode(chunks[2], TextType.TEXT))
        
    return new_nodes

def extract_markdown_images(text):
    # Verbose regex for images with comments
    pattern = re.compile(
        r"""
        !\[         # Image marker and opening bracket for alt text
        (.*?)       # Capture group 1: Alt text (non-greedy)
        \]          # Closing bracket for alt text
        \(          # Opening parenthesis for URL
        \s*         # Optional whitespace
        ([^()\s]+   # Start of capture group 2: URL - non-parenthesis, non-whitespace chars
        (?:\([^()\s]+\)[^()\s]*)*  # Handle URLs with parentheses
        )           # End of capture group 2
        \s*         # Optional whitespace
        \)          # Closing parenthesis for URL
        """, 
        re.VERBOSE
    )
    images = re.findall(pattern, text)
    return images

def extract_markdown_links(text):
    # Verbose regex for markdown links with comments
    pattern = re.compile(
        r"""
        \[              # Opening bracket for link text
        (
            !?\[.*?\]   # Handle image markdown within link text (non-greedy)
            \(.*?\)     # Handle image URL within link text (non-greedy)
            |           # OR
            .*?         # Regular link text (non-greedy)
        )               # End of capture group 1: link text
        \]              # Closing bracket for link text
        \(              # Opening parenthesis for URL
        \s*             # Optional whitespace
        (
            [^()\s]+    # Start of capture group 2: URL - non-parenthesis, non-whitespace chars
            (?:         # Non-capturing group for handling nested parentheses
                \([^()\s]+\)  # Match content within parentheses
                [^()\s]*      # Followed by more URL characters
            )*          # Zero or more occurrences of nested parentheses
        )               # End of capture group 2
        \s*             # Optional whitespace
        \)              # Closing parenthesis for URL
        """, 
        re.VERBOSE
    )
    links = re.findall(pattern, text)
    return links