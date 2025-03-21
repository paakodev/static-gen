import unittest

from htmlnode import HTMLNode


class TestTextNode(unittest.TestCase):
    def test_default_initialization(self):
        node = HTMLNode()
        self.assertIsNone(node.tag)
        self.assertIsNone(node.value)
        self.assertIsNone(node.children)
        self.assertIsNotNone(node.props)

    def test_initialization_with_values(self):
        node = HTMLNode("div", "Hello", ["child1", "child2"], {"class": "container"})
        self.assertEqual(node.tag, "div")
        self.assertEqual(node.value, "Hello")
        self.assertEqual(node.children, ["child1", "child2"])
        self.assertEqual(node.props, {"class": "container"})

    def test_to_html_raises_not_implemented(self):
        node = HTMLNode("div", "Hello")
        with self.assertRaises(NotImplementedError):
            node.to_html()

    def test_props_to_html_empty(self):
        node = HTMLNode("div", "Hello", props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single_prop(self):
        node = HTMLNode("div", "Hello", props={"class": "container"})
        self.assertEqual(node.props_to_html(), ' class="container"')

    def test_props_to_html_multiple_props(self):
        node = HTMLNode("span", "Text", props={"id": "my-span", "data-value": "123"})
        props_html = node.props_to_html()
        # Order of dictionary keys is not guaranteed, so we check both possible orderings
        expected1 = ' id="my-span" data-value="123"'
        expected2 = ' data-value="123" id="my-span"'
        self.assertIn(props_html, [expected1, expected2])

    def test_props_to_html_with_numeric_values(self):
        node = HTMLNode("p", "Paragraph", props={"data-index": 5})
        self.assertEqual(node.props_to_html(), ' data-index="5"')

    def test_repr_output(self):
        node = HTMLNode("h1", "Title", ["child1"], {"class": "header"})
        expected_repr = "HTMLNode(h1, Title, ['child1'], {'class': 'header'})"
        self.assertEqual(repr(node), expected_repr)



if __name__ == "__main__":
    unittest.main()