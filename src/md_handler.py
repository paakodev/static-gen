from enum import Enum
from typing import List
from leafnode import LeafNode
from parentnode import ParentNode
from textnode import TextNode, TextType, text_node_to_html_node
from htmlnode import HTMLNode
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

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

def markdown_to_blocks(markdown: str) -> List[str]:
    blocks = markdown.split("\n\n")
    blocks = [block.strip() for block in blocks]
    blocks = [block for block in blocks if block]
    return blocks

def block_to_block_type(block: str) -> BlockType:
    match block[0]:
        # Header, 1-6 # + plus space
        # We can skip counting, but it should have the space in position 1 to 6
        case "#":
            for i in range(1, 7):
                if block[i] == "#":
                    continue
                if block[i] == " ":
                    return BlockType.HEADING
            return BlockType.PARAGRAPH
        # Code, ``` + text + ```
        # Needs correct amounts of both sets
        case "`":
            if block[0:3] == "```" and block[-3:] == "```":
                return BlockType.CODE
            return BlockType.PARAGRAPH
        # Quote, all lines need this
        case ">":
            for line in block.split("\n"):
                if line[0] != ">":
                    return BlockType.PARAGRAPH
            return BlockType.QUOTE
        # Unordered list, all lines need this + space
        case "-":
            for line in block.split("\n"):
                if line[0:2] != "- ":
                    return BlockType.PARAGRAPH
            return BlockType.UNORDERED_LIST
        # Ordered list, has to start at 1, increase for following lines
        # Also requires '. ' after each number
        case "1":
            lines = block.split("\n")
            for i in range(0, len(lines)):
                if lines[i][:3] != f"{i+1}. ":
                    return BlockType.PARAGRAPH
            return BlockType.ORDERED_LIST
        # Normal paragraph
        case _:
            return BlockType.PARAGRAPH

def markdown_to_html_node(markdown: str) -> HTMLNode:
    new_children = []
    blocks = markdown_to_blocks(markdown)
    for block in blocks:
        md_type = block_to_block_type(block)
        match (md_type):
            case BlockType.HEADING:
                new_children.append(create_header_node(block))
            case BlockType.CODE:
                new_children.append(create_code_node(block))
            case BlockType.QUOTE:
                new_children.append(create_quote_node(block))
            case BlockType.UNORDERED_LIST:
                new_children.append(create_unordered_list(block))
            case BlockType.ORDERED_LIST:
                new_children.append(create_ordered_list(block))
            case BlockType.PARAGRAPH:
                new_children.append(create_paragraph(block))
            # This *really* *should* *not* happen. block_to_block_types will return PARAGRAPH
            # for unknown blocks, but leaving in a guard isn't a bad thing.
            case _:
                raise ValueError("unknown block type! help!")
    
    return ParentNode("div", new_children)

def create_header_node(block: str) -> HTMLNode:
    i = 0
    while i < len(block) and block[i] == "#":
        i += 1
    
    text = block[i:].strip()
    text_nodes = text_to_textnodes(text)
    html_nodes = [text_node_to_html_node(text_node) for text_node in text_nodes]
    node = ParentNode(f"h{i}", html_nodes)
    return node

def create_code_node(block: str) -> HTMLNode:
    block = block[3:-3] # Only strip leading/trailing backticks
    if block.startswith("\n"):
        block = block[1:] # But also remove opening newlines, if present
        
    node = LeafNode("code", block)
    parent = ParentNode("pre", [node])
    
    return parent


def create_quote_node(block: str) -> HTMLNode:
    block = "\n".join([line.lstrip(">").strip() for line in block.split("\n")])
    text_nodes = text_to_textnodes(block)
    html_nodes = [text_node_to_html_node(text_node) for text_node in text_nodes]
    node = ParentNode("blockquote", html_nodes)
    
    return node

def create_unordered_list(block: str) -> HTMLNode:
    pattern = re.compile(r"^-")
    list_items = []
    lines = block.split("\n")
    for line in lines:
        line = re.sub(pattern, "", line)
        text_nodes = text_to_textnodes(line.strip())
        html_nodes = [text_node_to_html_node(text_node) for text_node in text_nodes]
        ul_node = ParentNode("li", html_nodes)
        list_items.append(ul_node)
    parent = ParentNode("ul", list_items)
    
    return parent

def create_ordered_list(block: str) -> HTMLNode:
    pattern = re.compile(r"^\d+?\.")
    list_items = []
    lines = block.split("\n")
    for line in lines:
        line = re.sub(pattern, "", line)
        text_nodes = text_to_textnodes(line.strip())
        html_nodes = [text_node_to_html_node(text_node) for text_node in text_nodes]
        ol_node = ParentNode("li", html_nodes)
        list_items.append(ol_node)
    parent = ParentNode("ol", list_items)
    
    return parent

def create_paragraph(block: str) -> List[HTMLNode]:
    #  Normalize: Collapse single newlines into spaces
    block = block.replace("\n", " ")  # Only applies to paragraph blocks
    text_nodes = text_to_textnodes(block)
    children = [text_node_to_html_node(node) for node in text_nodes]
    node = ParentNode("p", children)
    
    return node

def extract_title(markdown: str) -> str:
    if not markdown:
        raise ValueError("Markdown document cannot be empty")
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:].strip()
    
    raise ValueError("No title in markdown document")