import unittest
from textnode import TextNode, TextType
from md_handler import split_nodes_delimiter

class TestMdHandler(unittest.TestCase):
    def test_valid_split(self):
        """Tests splitting a valid Markdown-style text node."""
        nodes = [TextNode("This is **bold** text", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_multiple_occurrences(self):
        """Tests that only the first Markdown occurrence is processed."""
        nodes = [TextNode("This is **bold** and this is **also bold**.", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and this is **also bold**.", TextType.TEXT)  # Left untouched
        ]
        self.assertEqual(result, expected)

    def test_missing_second_delimiter_raises_error(self):
        """Tests that missing a second delimiter raises a ValueError."""
        nodes = [TextNode("This is **bold text", TextType.TEXT)]
        with self.assertRaises(ValueError) as context:
            split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(str(context.exception), "Invalid Markdown: missing or unmatched delimiters")

    def test_non_text_nodes_untouched(self):
        """Tests that non-TEXT nodes remain unchanged."""
        nodes = [TextNode("This is bold", TextType.BOLD)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(result, nodes)  # Should be unchanged

    def test_nested_calls(self):
        """Tests processing text that requires multiple split calls."""
        nodes = [TextNode("This is **bold** and *italic*.", TextType.TEXT)]
        
        # First, extract bold
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and *italic*.", TextType.TEXT)
        ]
        self.assertEqual(nodes, expected)

        # Then, extract italic from remaining text
        nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(".", TextType.TEXT)
        ]
        self.assertEqual(nodes, expected)

    def test_adjacent_delimiters(self):
        """Tests adjacent delimiters that should be treated as empty content."""
        nodes = [TextNode("**bold**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("", TextType.TEXT)
        ]
        self.assertEqual(result, expected)

    def test_edge_case_trailing_delimiter(self):
        """Tests when the delimiter appears at the end of the string."""
        nodes = [TextNode("Starts **bold**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Starts ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("", TextType.TEXT)  # Ensures trailing part is preserved
        ]
        self.assertEqual(result, expected)
    
    def test_edge_case_leading_delimiter(self):
        """Tests handling of a leading delimiter in the text."""
        nodes = [TextNode("*italic* text", TextType.TEXT)]  # Leading *
        result = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        expected = [
            TextNode("", TextType.TEXT),  # Before the delimiter (empty)
            TextNode("italic", TextType.ITALIC),  # Inside the delimiter
            TextNode(" text", TextType.TEXT)   # After the delimiter
        ]

        self.assertEqual(result, expected)

    def test_multiple_different_delimiters(self):
        """Tests handling multiple different delimiters in sequence."""
        nodes = [TextNode("This is **bold** and *italic*.", TextType.TEXT)]
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)  # Extract bold
        nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)  # Extract italic
        
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(".", TextType.TEXT)
        ]
        self.assertEqual(nodes, expected)

    def test_invalid_text_type(self):
        """Ensures the function only processes TextType.TEXT nodes."""
        nodes = [TextNode("Some text", TextType.CODE)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        self.assertEqual(result, nodes)  # Should be unchanged
        
    def test_empty_content_between_delimiters(self):
        """Tests handling of empty content between delimiters."""
        nodes = [TextNode("**", TextType.TEXT)]  # Text is just the delimiter itself
        result = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        expected = [
            TextNode("", TextType.TEXT),  # Before the delimiter (empty)
            TextNode("", TextType.ITALIC),  # Inside the delimiter (empty content)
            TextNode("", TextType.TEXT)   # After the delimiter (empty)
        ]

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
