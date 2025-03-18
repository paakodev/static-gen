import unittest

from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    """
    CLASS FUNCTIONALITY TESTS
    """
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)
        
    def test_neq_different_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is another text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_neq_different_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        node2 = TextNode("Click here", TextType.LINK, "https://example.com")
        self.assertEqual(node, node2)

    def test_neq_different_url(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        node2 = TextNode("Click here", TextType.LINK, "https://another.com")
        self.assertNotEqual(node, node2)

    def test_neq_url_vs_no_url(self):
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        node2 = TextNode("Click here", TextType.LINK)
        self.assertNotEqual(node, node2)

    def test_neq_different_types_but_same_text(self):
        node = TextNode("Same text", TextType.TEXT)
        node2 = TextNode("Same text", TextType.CODE)
        self.assertNotEqual(node, node2)

    def test_empty_text_nodes(self):
        node = TextNode("", TextType.TEXT)
        node2 = TextNode("", TextType.TEXT)
        self.assertEqual(node, node2)

    def test_repr_output(self):
        node = TextNode("Test", TextType.BOLD, "https://example.com")
        expected_repr = "TextNode(Test, bold, https://example.com)"
        self.assertEqual(repr(node), expected_repr)
        
    """
    text_node_to_html_node FUNCTIONALITY TESTS
    """
        
    def test_text(self):
        """Tests conversion of a TEXT type TextNode to a LeafNode with no tag."""
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_bold(self):
        """Tests conversion of a BOLD TextNode to a <b> tag LeafNode."""
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold text")

    def test_italic(self):
        """Tests conversion of an ITALIC TextNode to an <i> tag LeafNode."""
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic text")

    def test_code(self):
        """Tests conversion of a CODE TextNode to a <code> tag LeafNode."""
        node = TextNode("print('Hello')", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "print('Hello')")

    def test_link(self):
        """Tests conversion of a LINK TextNode to an <a> tag LeafNode with href."""
        node = TextNode("Click here", TextType.LINK, "https://example.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://example.com"})

    def test_link_missing_url(self):
        """Tests LINK TextNode with no URL, expecting an error."""
        node = TextNode("Click here", TextType.LINK)
        with self.assertRaises(TypeError):
            text_node_to_html_node(node)

    def test_image(self):
        """Tests conversion of an IMAGE TextNode to an <img> tag LeafNode with src and alt."""
        node = TextNode("An image", TextType.IMAGE, "https://example.com/image.jpg")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")  # Image nodes should have an empty value
        self.assertEqual(html_node.props, {"src": "https://example.com/image.jpg", "alt": "An image"})

    def test_image_missing_url(self):
        """Tests IMAGE TextNode with no URL, expecting an error."""
        node = TextNode("An image", TextType.IMAGE)
        with self.assertRaises(TypeError):
            text_node_to_html_node(node)

    def test_unknown_text_type(self):
        """Tests that an unknown TextType raises a TypeError."""
        node = TextNode("Unknown type", "UNKNOWN")
        with self.assertRaises(TypeError):
            text_node_to_html_node(node)

    def test_none_text(self):
        """Tests that a None text value raises a TypeError."""
        with self.assertRaises(TypeError) as context:
            text_node_to_html_node(TextNode(None, TextType.TEXT))
        self.assertEqual(str(context.exception), "Text types need text")  # Ensure correct error message

    def test_empty_text_raises_error(self):
        """Tests that an empty text string raises a TypeError for TEXT types."""
        node = TextNode("", TextType.TEXT)
        with self.assertRaises(TypeError) as context:
            text_node_to_html_node(node)
        self.assertEqual(str(context.exception), "Text types need text")



if __name__ == "__main__":
    unittest.main()