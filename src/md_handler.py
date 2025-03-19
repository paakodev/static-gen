from typing import List
from textnode import TextNode, TextType
import re

def split_nodes_delimiter(old_nodes: List[TextNode], delimiter: str, text_type: TextType) -> List[TextNode]:
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
        
        # Process the remainder recursively
        remainder_node = TextNode(chunks[2], TextType.TEXT)
        new_nodes.extend(split_nodes_delimiter([remainder_node], delimiter, text_type)) 
        
    return new_nodes

def extract_markdown_images(text: str) -> List[tuple[str, str]]:
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

def extract_markdown_links(text:str) -> List[tuple[str, str]]:
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

def split_nodes_image(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes = []
    for node in old_nodes:
        # We're not processing anything but text nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        # If no images, add and continue
        images = extract_markdown_images(node.text)
        if len(images) == 0:
            new_nodes.append(node)
            continue
        
        remaining_text = node.text
        for text, link in images:
            chunks = remaining_text.split(f"![{text}]({link})", maxsplit=1)
            if chunks[0]:
                new_nodes.append(TextNode(chunks[0], TextType.TEXT))
            new_nodes.append(TextNode(text, TextType.IMAGE, link))
            remaining_text = chunks[1] if len(chunks) > 1 else ""
        
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
        
    return new_nodes

def split_nodes_link(old_nodes: List[TextNode]) -> List[TextNode]:
    new_nodes = []
    for node in old_nodes:
        # We're not processing anything but text nodes
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        
        # If no imagelinkss, add and continue
        links = extract_markdown_links(node.text)
        if len(links) == 0:
            new_nodes.append(node)
            continue
        
        remaining_text = node.text
        for text, link in links:
            chunks = remaining_text.split(f"[{text}]({link})", maxsplit=1)
            if chunks[0]:
                new_nodes.append(TextNode(chunks[0], TextType.TEXT))
            new_nodes.append(TextNode(text, TextType.LINK, link))
            remaining_text = chunks[1] if len(chunks) > 1 else ""
        
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
        
    return new_nodes

def text_to_textnodes(text: str) -> List[TextNode]:
    new_nodes = [TextNode(text, TextType.TEXT)]
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    # Adjusted empty-node cleaner, leaves single spaces alone
    new_nodes = [node for node in new_nodes if not (node.text_type == TextType.TEXT and (node.text.strip() == "" and node.text != " "))]
    return new_nodes