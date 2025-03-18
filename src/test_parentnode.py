import unittest

from parentnode import ParentNode
from leafnode import LeafNode


class TestTextNode(unittest.TestCase):
    def test_to_html_with_children(self):
        """Tests ParentNode with a single LeafNode child."""
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_multiple_children(self):
        """Tests ParentNode with multiple LeafNode children."""
        child1 = LeafNode("p", "First paragraph")
        child2 = LeafNode("p", "Second paragraph")
        parent_node = ParentNode("div", [child1, child2])
        self.assertEqual(parent_node.to_html(), "<div><p>First paragraph</p><p>Second paragraph</p></div>")

    def test_to_html_with_grandchildren(self):
        """Tests ParentNode containing another ParentNode as a child."""
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span><b>grandchild</b></span></div>")

    def test_to_html_with_deep_nesting(self):
        """Tests deeply nested ParentNodes."""
        deep_nested = ParentNode("section", [
            ParentNode("article", [
                ParentNode("div", [
                    LeafNode("p", "Deep text")
                ])
            ])
        ])
        self.assertEqual(deep_nested.to_html(), "<section><article><div><p>Deep text</p></div></article></section>")

    def test_to_html_with_sibling_parent_nodes(self):
        """Tests multiple ParentNode siblings within a ParentNode."""
        child1 = ParentNode("ul", [
            LeafNode("li", "Item 1"),
            LeafNode("li", "Item 2")
        ])
        child2 = ParentNode("ul", [
            LeafNode("li", "Item A"),
            LeafNode("li", "Item B")
        ])
        parent = ParentNode("section", [child1, child2])
        self.assertEqual(
            parent.to_html(),
            "<section><ul><li>Item 1</li><li>Item 2</li></ul><ul><li>Item A</li><li>Item B</li></ul></section>"
        )

    def test_to_html_with_no_children_raises_error(self):
        """Tests that ParentNode without children raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            ParentNode("div", []).to_html()
        self.assertEqual(str(context.exception), "ParentNode must have child nodes")

    def test_to_html_with_no_tag_raises_error(self):
        """Tests that ParentNode without a tag raises a ValueError."""
        child_node = LeafNode("p", "Content")
        with self.assertRaises(ValueError) as context:
            ParentNode(None, [child_node]).to_html()
        self.assertEqual(str(context.exception), "ParentNode must have a tag")

    def test_to_html_with_attributes(self):
        """Tests ParentNode with attributes."""
        child = LeafNode("p", "Text")
        parent = ParentNode("div", [child], {"class": "container"})
        self.assertEqual(parent.to_html(), '<div class="container"><p>Text</p></div>')

    def test_to_html_with_multiple_attributes(self):
        """Tests ParentNode with multiple attributes."""
        child = LeafNode("p", "Text")
        parent = ParentNode("section", [child], {"id": "main", "class": "wrapper"})
        result = parent.to_html()
        expected1 = '<section id="main" class="wrapper"><p>Text</p></section>'
        expected2 = '<section class="wrapper" id="main"><p>Text</p></section>'
        self.assertIn(result, [expected1, expected2])  # Account for unordered dictionary keys
        
    def test_to_html_with_mixed_leaf_and_parent_nodes(self):
        """Tests ParentNode with both LeafNode and ParentNode children."""
        leaf1 = LeafNode("p", "Paragraph 1")
        nested_parent = ParentNode("div", [
            LeafNode("span", "Inside div")
        ])
        leaf2 = LeafNode("p", "Paragraph 2")
        parent = ParentNode("section", [leaf1, nested_parent, leaf2])

        self.assertEqual(
            parent.to_html(),
            "<section><p>Paragraph 1</p><div><span>Inside div</span></div><p>Paragraph 2</p></section>"
        )


if __name__ == "__main__":
    unittest.main()