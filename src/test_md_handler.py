import unittest
from textnode import TextNode, TextType
from md_handler import split_nodes_delimiter, extract_markdown_images, extract_markdown_links

class TestMdHandler(unittest.TestCase):
    #region split_nodes_delimiter
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
        
    #endregion

    #region extract_markdown_images
    def test_single_image(self):
        """Tests extracting a single markdown image."""
        text = "This is an image: ![Alt text](https://example.com/image.jpg)"
        result = extract_markdown_images(text)
        expected = [("Alt text", "https://example.com/image.jpg")]
        self.assertEqual(result, expected)

    def test_multiple_images(self):
        """Tests extracting multiple markdown images in one string."""
        text = (
            "Here is an image ![Image1](https://example.com/1.jpg) "
            "and another ![Image2](https://example.com/2.png)."
        )
        result = extract_markdown_images(text)
        expected = [
            ("Image1", "https://example.com/1.jpg"),
            ("Image2", "https://example.com/2.png")
        ]
        self.assertEqual(result, expected)

    def test_image_without_alt_text(self):
        """Tests extracting an image that has no alt text."""
        text = "Look at this ![](https://example.com/image.jpg)."
        result = extract_markdown_images(text)
        expected = [("", "https://example.com/image.jpg")]  # Empty alt text should still be extracted
        self.assertEqual(result, expected)

    def test_image_with_special_characters(self):
        """Tests extracting an image with special characters in the alt text and URL."""
        text = "Special ![🚀 Rocket & Code](https://example.com/special%20chars.png)"
        result = extract_markdown_images(text)
        expected = [("🚀 Rocket & Code", "https://example.com/special%20chars.png")]
        self.assertEqual(result, expected)

    def test_image_with_relative_url(self):
        """Tests extracting an image with a relative URL."""
        text = "Here is a local image: ![Local](./images/photo.jpg)"
        result = extract_markdown_images(text)
        expected = [("Local", "./images/photo.jpg")]
        self.assertEqual(result, expected)

    def test_image_surrounded_by_text(self):
        """Tests extracting an image in the middle of text."""
        text = "Here is an image ![Alt](https://example.com/image.jpg) inside a sentence."
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/image.jpg")]
        self.assertEqual(result, expected)

    def test_image_with_markdown_inline_code(self):
        """Tests extracting an image with inline code in alt text."""
        text = "This is an image with `code`: ![`Inline code`](https://example.com/code.png)"
        result = extract_markdown_images(text)
        expected = [("`Inline code`", "https://example.com/code.png")]
        self.assertEqual(result, expected)

    def test_no_images(self):
        """Tests when no markdown image syntax is present."""
        text = "This text has no images."
        result = extract_markdown_images(text)
        expected = []
        self.assertEqual(result, expected)

    def test_malformed_image_missing_parentheses(self):
        """Tests handling a malformed image missing parentheses."""
        text = "This is an invalid image ![Alt text]https://example.com/image.jpg"
        result = extract_markdown_images(text)
        expected = []  # Should not match because it's missing `()` around the URL
        self.assertEqual(result, expected)

    def test_malformed_image_missing_brackets(self):
        """Tests handling a malformed image missing brackets."""
        text = "This is an invalid image (https://example.com/image.jpg)"
        result = extract_markdown_images(text)
        expected = []  # Should not match because it's missing `[]` for the alt text
        self.assertEqual(result, expected)

    def test_malformed_image_missing_both(self):
        """Tests handling a malformed image missing both brackets and parentheses."""
        text = "This is an invalid image Alt text https://example.com/image.jpg"
        result = extract_markdown_images(text)
        expected = []  # No proper markdown syntax for an image
        self.assertEqual(result, expected)

    def test_escaped_image_syntax(self):
        """Tests escaped image syntax. Markdown typically does NOT ignore these."""
        text = "This should still be an image: \\![Alt](https://example.com/escaped.jpg)"
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/escaped.jpg")]  # CommonMark keeps escaped images
        self.assertEqual(result, expected)

    def test_image_with_absolute_url(self):
        """Tests extracting an image with an absolute URL."""
        text = "![Alt](https://example.com/image.jpg)"
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/image.jpg")]
        self.assertEqual(result, expected)

    def test_image_with_relative_url(self):
        """Tests extracting an image with a relative URL."""
        text = "![Alt](./images/photo.jpg)"
        result = extract_markdown_images(text)
        expected = [("Alt", "./images/photo.jpg")]
        self.assertEqual(result, expected)

    def test_image_with_nested_parentheses(self):
        """Tests extracting an image where the URL contains parentheses."""
        text = "![Alt](https://example.com/image_(1).jpg)"
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/image_(1).jpg")]
        self.assertEqual(result, expected)
        
    def test_image_with_nested_sequential_parentheses(self):
        """Tests extracting an image where the URL contains several sequential parentheses."""
        text = "![Alt](https://example.com/image_(1)(2).jpg)"
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/image_(1)(2).jpg")]
        self.assertEqual(result, expected)

    def test_image_with_nested_parentheses_and_query(self):
        """Tests extracting an image where the URL contains nested parentheses and query parameters."""
        text = "![Alt](https://example.com/image_(1).jpg?size=large)"
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/image_(1).jpg?size=large")]
        self.assertEqual(result, expected)

    def test_image_with_query_parameters(self):
        """Tests extracting an image with query parameters in the URL."""
        text = "![Alt](https://example.com/image.jpg?size=large)"
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/image.jpg?size=large")]
        self.assertEqual(result, expected)
    
    def test_image_with_markdown_inline_link(self):
        """Tests when an image is part of a markdown link."""
        text = "[This is a link](https://example.com) and an image ![Alt](https://example.com/img.jpg)."
        result = extract_markdown_images(text)
        expected = [("Alt", "https://example.com/img.jpg")]
        self.assertEqual(result, expected)
    
    #endregion
        
    #region extract_markdown_links
    def test_single_link(self):
        """Tests extracting a single markdown link."""
        text = "This is a [link](https://example.com)."
        result = extract_markdown_links(text)
        expected = [("link", "https://example.com")]
        self.assertEqual(result, expected)

    def test_multiple_links(self):
        """Tests extracting multiple markdown links in one string."""
        text = (
            "Here is a [Link1](https://example.com/1) "
            "and another [Link2](https://example.com/2)."
        )
        result = extract_markdown_links(text)
        expected = [
            ("Link1", "https://example.com/1"),
            ("Link2", "https://example.com/2")
        ]
        self.assertEqual(result, expected)

    def test_link_without_text(self):
        """Tests extracting a link where the anchor text is a space."""
        text = "Look at this [ ](https://example.com)."
        result = extract_markdown_links(text)
        expected = [(" ", "https://example.com")]  # ✅ Correct if space is preserved
        self.assertEqual(result, expected)

    def test_empty_link_text(self):
        """Tests extracting a link where the anchor text is completely empty."""
        text = "Check this link: [](https://example.com)."
        result = extract_markdown_links(text)
        expected = [("", "https://example.com")]  # ✅ Empty string for text
        self.assertEqual(result, expected)

    def test_link_with_special_characters(self):
        """Tests extracting a link with special characters in the text and URL."""
        text = "Special [🚀 Rocket & Code](https://example.com/special%20chars)"
        result = extract_markdown_links(text)
        expected = [("🚀 Rocket & Code", "https://example.com/special%20chars")]
        self.assertEqual(result, expected)

    def test_link_with_relative_url(self):
        """Tests extracting a link with a relative URL."""
        text = "Here is a local link: [Local](./docs/index.html)"
        result = extract_markdown_links(text)
        expected = [("Local", "./docs/index.html")]
        self.assertEqual(result, expected)

    def test_link_surrounded_by_text(self):
        """Tests extracting a link in the middle of text."""
        text = "Here is a [link](https://example.com) inside a sentence."
        result = extract_markdown_links(text)
        expected = [("link", "https://example.com")]
        self.assertEqual(result, expected)

    def test_link_with_markdown_inline_code(self):
        """Tests extracting a link with inline code in anchor text."""
        text = "This is a [`code link`](https://example.com/code)."
        result = extract_markdown_links(text)
        expected = [("`code link`", "https://example.com/code")]
        self.assertEqual(result, expected)

    def test_no_links(self):
        """Tests when no markdown link syntax is present."""
        text = "This text has no links."
        result = extract_markdown_links(text)
        expected = []
        self.assertEqual(result, expected)

    def test_malformed_link_missing_parentheses(self):
        """Tests handling a malformed link missing parentheses."""
        text = "This is an invalid link [Text]https://example.com"
        result = extract_markdown_links(text)
        expected = []  # Should not match because it's missing `()` around the URL
        self.assertEqual(result, expected)

    def test_malformed_link_missing_brackets(self):
        """Tests handling a malformed link missing brackets."""
        text = "This is an invalid link (https://example.com)"
        result = extract_markdown_links(text)
        expected = []  # Should not match because it's missing `[]` for the anchor text
        self.assertEqual(result, expected)

    def test_malformed_link_missing_both(self):
        """Tests handling a malformed link missing both brackets and parentheses."""
        text = "This is an invalid link Text https://example.com"
        result = extract_markdown_links(text)
        expected = []  # No proper markdown syntax for a link
        self.assertEqual(result, expected)

    def test_escaped_link_syntax(self):
        """Tests that an escaped bracket does NOT prevent link detection."""
        text = "This should still be a link: \\[Alt](https://example.com/escaped)"
        result = extract_markdown_links(text)
        expected = [("Alt", "https://example.com/escaped")]  # ✅ CommonMark extracts this
        self.assertEqual(result, expected)

    def test_link_with_nested_parentheses_in_url(self):
        """Tests extracting a link where the URL contains parentheses."""
        text = "Here is a [link](https://example.com/path_(with_parens).html)"
        result = extract_markdown_links(text)
        expected = [("link", "https://example.com/path_(with_parens).html")]
        self.assertEqual(result, expected)

    def test_link_with_nested_sequential_parentheses_in_url(self):
        """Tests extracting a link where the URL contains parentheses."""
        text = "Here is a [link](https://example.com/path_(with)_(parens).html)"
        result = extract_markdown_links(text)
        expected = [("link", "https://example.com/path_(with)_(parens).html")]
        self.assertEqual(result, expected)

    def test_link_with_nested_parentheses_and_query(self):
        """Tests extracting a link where the URL contains nested parentheses and query parameters."""
        text = "Visit [this](https://example.com/path_(1).html?ref=home)"
        result = extract_markdown_links(text)
        expected = [("this", "https://example.com/path_(1).html?ref=home")]
        self.assertEqual(result, expected)

    def test_link_with_markdown_inline_image(self):
        """Tests when a markdown image is inside a link."""
        text = "[![Image](https://example.com/image.jpg)](https://example.com)"
        result = extract_markdown_links(text)
        expected = [("![Image](https://example.com/image.jpg)", "https://example.com")]
        self.assertEqual(result, expected)
        
    #endregion
    

if __name__ == "__main__":
    unittest.main()
