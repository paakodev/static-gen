from textnode import TextNode, TextType

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