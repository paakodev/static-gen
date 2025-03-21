import unittest

from leafnode import LeafNode


class TestTextNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_no_tag(self):
        node = LeafNode(None, "Plain text")
        self.assertEqual(node.to_html(), "Plain text")

    def test_leaf_to_html_with_attributes(self):
        node = LeafNode("a", "Click here", {"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">Click here</a>')

    def test_leaf_to_html_with_multiple_attributes(self):
        node = LeafNode("span", "Styled text", {"class": "bold", "id": "text1"})
        html_output = node.to_html()
        expected1 = '<span class="bold" id="text1">Styled text</span>'
        expected2 = '<span id="text1" class="bold">Styled text</span>'
        self.assertIn(html_output, [expected1, expected2])  # Account for unordered dict

    def test_leaf_to_html_empty_value_raises_error(self):
        with self.assertRaises(ValueError) as context:
            node = LeafNode("p", "")
            node.to_html()
        self.assertEqual(str(context.exception), "'p' cannot have an empty value.")

    def test_leaf_to_html_none_value_raises_error(self):
        with self.assertRaises(ValueError) as context:
            node = LeafNode("p", None)
            node.to_html()
        self.assertEqual(str(context.exception), "'p' cannot have an empty value.")

    def test_leaf_to_html_empty_tag(self):
        node = LeafNode("", "Text")
        self.assertEqual(node.to_html(), "<>Text</>")

    def test_leaf_to_html_no_props(self):
        node = LeafNode("div", "Content", None)
        self.assertEqual(node.to_html(), "<div>Content</div>")

    def test_leaf_to_html_numeric_value(self):
        node = LeafNode("p", 123)
        self.assertEqual(node.to_html(), "<p>123</p>")

    def test_leaf_to_html_boolean_value(self):
        node = LeafNode("p", True)
        self.assertEqual(node.to_html(), "<p>True</p>")


if __name__ == "__main__":
    unittest.main()