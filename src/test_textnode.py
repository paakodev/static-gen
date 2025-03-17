import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
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
        node = TextNode("Same text", TextType.NORMAL)
        node2 = TextNode("Same text", TextType.CODE)
        self.assertNotEqual(node, node2)

    def test_empty_text_nodes(self):
        node = TextNode("", TextType.NORMAL)
        node2 = TextNode("", TextType.NORMAL)
        self.assertEqual(node, node2)

    def test_repr_output(self):
        node = TextNode("Test", TextType.BOLD, "https://example.com")
        expected_repr = "TextNode(Test, bold, https://example.com)"
        self.assertEqual(repr(node), expected_repr)


if __name__ == "__main__":
    unittest.main()