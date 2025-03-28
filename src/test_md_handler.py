import unittest
from textnode import TextNode, TextType
from md_handler import BlockType, extract_title, markdown_to_html_node, split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type

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
        """Tests that all coorences of Markdown is processed."""
        nodes = [TextNode("This is **bold** and this is **also bold**.", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and this is ", TextType.TEXT),
            TextNode("also bold", TextType.BOLD),
            TextNode(".", TextType.TEXT)
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
        nodes = [TextNode("This is **bold** and _italic_.", TextType.TEXT)]
        
        # First, extract bold
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and _italic_.", TextType.TEXT)
        ]
        self.assertEqual(nodes, expected)

        # Then, extract italic from remaining text
        nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
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
        nodes = [TextNode("Ends **bold**", TextType.TEXT)]
        result = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        expected = [
            TextNode("Ends ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode("", TextType.TEXT)  # Ensures trailing part is preserved
        ]
        self.assertEqual(result, expected)
    
    def test_edge_case_leading_delimiter(self):
        """Tests handling of a leading delimiter in the text."""
        nodes = [TextNode("_italic_ text", TextType.TEXT)]  # Leading *
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

        expected = [
            TextNode("", TextType.TEXT),  # Before the delimiter (empty)
            TextNode("italic", TextType.ITALIC),  # Inside the delimiter
            TextNode(" text", TextType.TEXT)   # After the delimiter
        ]

        self.assertEqual(result, expected)

    def test_multiple_different_delimiters(self):
        """Tests handling multiple different delimiters in sequence."""
        nodes = [TextNode("This is **bold** and _italic_.", TextType.TEXT)]
        nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)  # Extract bold
        nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)  # Extract italic
        
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
        nodes = [TextNode("__", TextType.TEXT)]  # Text is just the delimiter itself
        result = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

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
    
    #region split_nodes_image
    def test_split_single_image(self):
        """Tests splitting a text node with a single image."""
        node = TextNode(
            "Here is an ![image](https://example.com/image.png) in text.", TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Here is an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/image.png"),
            TextNode(" in text.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_multiple_sequential_images(self):
        """Tests splitting multiple images in the same text node."""
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("This is text with an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_image_at_start(self):
        """Tests splitting when the image is at the start of the text."""
        node = TextNode(
            "![Start](https://example.com/start.jpg) and some text.", TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Start", TextType.IMAGE, "https://example.com/start.jpg"),
            TextNode(" and some text.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_image_at_end(self):
        """Tests splitting when the image is at the end of the text."""
        node = TextNode(
            "Some text before an image ![End](https://example.com/end.jpg)", TextType.TEXT
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Some text before an image ", TextType.TEXT),
            TextNode("End", TextType.IMAGE, "https://example.com/end.jpg"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_no_images(self):
        """Tests when there are no images in the text."""
        node = TextNode("This is a text with no images.", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("This is a text with no images.", TextType.TEXT)]
        self.assertListEqual(new_nodes, expected)

    def test_non_text_nodes_untouched(self):
        """Tests that non-TEXT nodes remain unchanged."""
        node = TextNode("This is bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        expected = [TextNode("This is bold", TextType.BOLD)]
        self.assertListEqual(new_nodes, expected)

    def test_multiple_nodes(self):
        """Tests processing multiple text nodes at once."""
        nodes = [
            TextNode("First text.", TextType.TEXT),
            TextNode(
                "Second ![image](https://example.com/image.jpg) with more text.",
                TextType.TEXT,
            ),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("First text.", TextType.TEXT),
            TextNode("Second ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/image.jpg"),
            TextNode(" with more text.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_image_with_alt_text_containing_brackets(self):
        """Tests images with brackets in alt text."""
        node = TextNode(
            "Here is an image ![image [example]](https://example.com/image.jpg).",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Here is an image ", TextType.TEXT),
            TextNode("image [example]", TextType.IMAGE, "https://example.com/image.jpg"),
            TextNode(".", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_image_with_query_parameters(self):
        """Tests images where the URL has query parameters."""
        node = TextNode(
            "Check this ![query image](https://example.com/img.jpg?size=large).",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("Check this ", TextType.TEXT),
            TextNode("query image", TextType.IMAGE, "https://example.com/img.jpg?size=large"),
            TextNode(".", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_adjacent_images(self):
        """Tests handling when two images are directly next to each other."""
        node = TextNode(
            "![First](https://example.com/1.jpg)![Second](https://example.com/2.jpg)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        expected = [
            TextNode("First", TextType.IMAGE, "https://example.com/1.jpg"),
            TextNode("Second", TextType.IMAGE, "https://example.com/2.jpg"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_multiple_separate_text_nodes(self):
        """Tests processing a list of multiple separate text nodes."""
        nodes = [
            TextNode("First part.", TextType.TEXT),
            TextNode("Image here: ![Pic](https://example.com/pic.jpg)", TextType.TEXT),
            TextNode("Last part.", TextType.TEXT),
        ]
        new_nodes = split_nodes_image(nodes)
        expected = [
            TextNode("First part.", TextType.TEXT),
            TextNode("Image here: ", TextType.TEXT),
            TextNode("Pic", TextType.IMAGE, "https://example.com/pic.jpg"),
            TextNode("Last part.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)
    
    #endregion

    #region split_nodes_link
    def test_split_single_link(self):
        """Tests splitting a text node with a single link."""
        node = TextNode(
            "Here is a [link](https://example.com) in text.", TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Here is a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" in text.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_multiple_sequential_links(self):
        """Tests splitting multiple links in the same text node."""
        node = TextNode(
            "This is text with a [first link](https://example.com/1) and another [second link](https://example.com/2)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("first link", TextType.LINK, "https://example.com/1"),
            TextNode(" and another ", TextType.TEXT),
            TextNode("second link", TextType.LINK, "https://example.com/2"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_link_at_start(self):
        """Tests splitting when the link is at the start of the text."""
        node = TextNode(
            "[Start](https://example.com/start) and some text.", TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Start", TextType.LINK, "https://example.com/start"),
            TextNode(" and some text.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_link_at_end(self):
        """Tests splitting when the link is at the end of the text."""
        node = TextNode(
            "Some text before a [link](https://example.com/end)", TextType.TEXT
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Some text before a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com/end"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_split_no_links(self):
        """Tests when there are no links in the text."""
        node = TextNode("This is a text with no links.", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This is a text with no links.", TextType.TEXT)]
        self.assertListEqual(new_nodes, expected)

    def test_non_text_nodes_untouched(self):
        """Tests that non-TEXT nodes remain unchanged."""
        node = TextNode("This is bold", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        expected = [TextNode("This is bold", TextType.BOLD)]
        self.assertListEqual(new_nodes, expected)

    def test_multiple_nodes(self):
        """Tests processing multiple text nodes at once."""
        nodes = [
            TextNode("First text.", TextType.TEXT),
            TextNode(
                "Second [link](https://example.com) with more text.",
                TextType.TEXT,
            ),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("First text.", TextType.TEXT),
            TextNode("Second ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" with more text.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_link_with_text_containing_brackets(self):
        """Tests links with brackets in anchor text."""
        node = TextNode(
            "Here is a [link [example]](https://example.com).",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Here is a ", TextType.TEXT),
            TextNode("link [example]", TextType.LINK, "https://example.com"),
            TextNode(".", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_link_with_query_parameters(self):
        """Tests links where the URL has query parameters."""
        node = TextNode(
            "Check this [query link](https://example.com/page?size=large).",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("Check this ", TextType.TEXT),
            TextNode("query link", TextType.LINK, "https://example.com/page?size=large"),
            TextNode(".", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_adjacent_links(self):
        """Tests handling when two links are directly next to each other."""
        node = TextNode(
            "[First](https://example.com/1)[Second](https://example.com/2)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("First", TextType.LINK, "https://example.com/1"),
            TextNode("Second", TextType.LINK, "https://example.com/2"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_multiple_separate_text_nodes(self):
        """Tests processing a list of multiple separate text nodes."""
        nodes = [
            TextNode("First part.", TextType.TEXT),
            TextNode("Link here: [Pic](https://example.com)", TextType.TEXT),
            TextNode("Last part.", TextType.TEXT),
        ]
        new_nodes = split_nodes_link(nodes)
        expected = [
            TextNode("First part.", TextType.TEXT),
            TextNode("Link here: ", TextType.TEXT),
            TextNode("Pic", TextType.LINK, "https://example.com"),
            TextNode("Last part.", TextType.TEXT),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_link_with_markdown_inline_image(self):
        """Tests when a markdown image is inside a link."""
        text = "[![Image](https://example.com/image.jpg)](https://example.com)"
        node = TextNode(text, TextType.TEXT)
        new_nodes = split_nodes_link([node])
        expected = [
            TextNode("![Image](https://example.com/image.jpg)", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(new_nodes, expected)
    #endregion
    
    #region text_to_textnodes
    def test_starter(self):
        """Basic test covering all Markdown elements at least once."""
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_only_text(self):
        """Tests input with only plain text, no Markdown formatting."""
        text = "Just a simple text string."
        new_nodes = text_to_textnodes(text)
        expected = [TextNode("Just a simple text string.", TextType.TEXT)]
        self.assertListEqual(new_nodes, expected)

    def test_only_images(self):
        """Tests input containing only images."""
        text = "![First](https://example.com/1.jpg) ![Second](https://example.com/2.jpg)"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("First", TextType.IMAGE, "https://example.com/1.jpg"),
            TextNode(" ", TextType.TEXT),
            TextNode("Second", TextType.IMAGE, "https://example.com/2.jpg"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_only_links(self):
        """Tests input containing only links."""
        text = "[Link1](https://example.com) [Link2](https://example.com/2)"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("Link1", TextType.LINK, "https://example.com"),
            TextNode(" ", TextType.TEXT),
            TextNode("Link2", TextType.LINK, "https://example.com/2"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_mixed_formatting_order(self):
        """Tests varying order of different Markdown types."""
        text = "_italic_ before **bold**, then a `code block`, and an ![image](https://img.com/img.jpg) and a [link](https://example.com)"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("italic", TextType.ITALIC),
            TextNode(" before ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(", then a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(", and an ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://img.com/img.jpg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_chained_bold(self):
        """Tests multiple consecutive bold segments."""
        text = "**Bold1** **Bold2**"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("Bold1", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("Bold2", TextType.BOLD),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_chained_italics(self):
        """Tests multiple consecutive italic segments."""
        text = "_Italic1_ _Italic2_"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("Italic1", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("Italic2", TextType.ITALIC),
        ]
        self.assertListEqual(new_nodes, expected)

    # We should support this but we don't
    # def test_nested_formatting(self):
    #     """Tests nested bold and italic formatting."""
    #     text = "**This is _bold italic_ text**"
    #     new_nodes = text_to_textnodes(text)
    #     expected = [
    #         TextNode("This is ", TextType.BOLD),
    #         TextNode("bold italic", TextType.ITALIC),
    #         TextNode(" text", TextType.BOLD),
    #     ]
    #     self.assertListEqual(new_nodes, expected)

    def test_nested_links_and_bold(self):
        """Tests bold text inside a link."""
        text = "[**Bold Link**](https://example.com)"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("**Bold Link**", TextType.LINK, "https://example.com"),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_malformed_bold(self):
        """Tests malformed bold text where only one asterisk is present."""
        text = "This is **not bold"
        with self.assertRaises(ValueError) as context:
            text_to_textnodes(text)
        self.assertEqual(str(context.exception), "Invalid Markdown: missing or unmatched delimiters")

    def test_malformed_italics(self):
        """Tests malformed italics where only one underscore is present."""
        text = "This is _not italic"
        with self.assertRaises(ValueError) as context:
            text_to_textnodes(text)
        self.assertEqual(str(context.exception), "Invalid Markdown: missing or unmatched delimiters")

    def test_malformed_code_block(self):
        """Tests malformed code block where only one backtick is present."""
        text = "This is `not a valid code block"
        with self.assertRaises(ValueError) as context:
            text_to_textnodes(text)
        self.assertEqual(str(context.exception), "Invalid Markdown: missing or unmatched delimiters")

    def test_adjacent_markdown(self):
        """Tests handling when two Markdown elements are directly adjacent."""
        text = "**bold**_italic_`code`"
        new_nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode("code", TextType.CODE),
        ]
        self.assertListEqual(new_nodes, expected)

    def test_edge_case_empty_string(self):
        """Tests handling of an empty string."""
        text = ""
        new_nodes = text_to_textnodes(text)
        expected = []
        self.assertListEqual(new_nodes, expected)

    def test_edge_case_whitespace(self):
        """Tests handling of a string containing only whitespace."""
        text = " "
        new_nodes = text_to_textnodes(text)
        expected = [TextNode(" ", TextType.TEXT)]
        self.assertListEqual(new_nodes, expected)
    #endregion
    
    #region markdown_to_blocks
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
        """ 
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    def test_single_paragraph(self):
        """Tests a single paragraph as input."""
        markdown = "This is a single paragraph."
        result = markdown_to_blocks(markdown)
        expected = ["This is a single paragraph."]
        self.assertListEqual(result, expected)

    def test_multiple_paragraphs(self):
        """Tests multiple paragraphs separated by two newlines."""
        markdown = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = markdown_to_blocks(markdown)
        expected = [
            "First paragraph.",
            "Second paragraph.",
            "Third paragraph.",
        ]
        self.assertListEqual(result, expected)

    def test_leading_and_trailing_whitespace(self):
        """Tests handling of leading and trailing whitespace in blocks."""
        markdown = "   First paragraph.   \n\n   Second paragraph.   "
        result = markdown_to_blocks(markdown)
        expected = ["First paragraph.", "Second paragraph."]
        self.assertListEqual(result, expected)

    def test_extra_blank_lines(self):
        """Tests handling of extra blank lines between blocks."""
        markdown = "First paragraph.\n\n\n\nSecond paragraph."
        result = markdown_to_blocks(markdown)
        expected = ["First paragraph.", "Second paragraph."]
        self.assertListEqual(result, expected)

    def test_blocks_with_markdown_syntax(self):
        """Tests handling of blocks that contain Markdown formatting."""
        markdown = "# Header\n\n**Bold text**\n\n*Italic text*\n\n`Code block`"
        result = markdown_to_blocks(markdown)
        expected = [
            "# Header",
            "**Bold text**",
            "*Italic text*",
            "`Code block`",
        ]
        self.assertListEqual(result, expected)

    def test_mixed_block_types(self):
        """Tests handling of paragraphs, lists, and headers together."""
        markdown = "# Header\n\nParagraph text.\n\n- List item 1\n- List item 2"
        result = markdown_to_blocks(markdown)
        expected = [
            "# Header",
            "Paragraph text.",
            "- List item 1\n- List item 2",
        ]
        self.assertListEqual(result, expected)

    def test_code_block(self):
        """Tests that fenced code blocks are not split incorrectly."""
        markdown = "```\nCode block\nwith multiple lines\n```\n\nNext paragraph."
        result = markdown_to_blocks(markdown)
        expected = [
            "```\nCode block\nwith multiple lines\n```",
            "Next paragraph.",
        ]
        self.assertListEqual(result, expected)

    def test_blockquote(self):
        """Tests handling of blockquotes as a separate block."""
        markdown = "> This is a blockquote.\n\nThis is a paragraph."
        result = markdown_to_blocks(markdown)
        expected = [
            "> This is a blockquote.",
            "This is a paragraph.",
        ]
        self.assertListEqual(result, expected)

    def test_list_handling(self):
        """Tests that lists are kept together as a block."""
        markdown = "- Item 1\n- Item 2\n\nAnother paragraph."
        result = markdown_to_blocks(markdown)
        expected = [
            "- Item 1\n- Item 2",
            "Another paragraph.",
        ]
        self.assertListEqual(result, expected)

    def test_empty_input(self):
        """Tests handling of an empty string."""
        markdown = ""
        result = markdown_to_blocks(markdown)
        expected = []
        self.assertListEqual(result, expected)

    def test_only_whitespace(self):
        """Tests handling of a string with only whitespace."""
        markdown = "   \n   "
        result = markdown_to_blocks(markdown)
        expected = []
        self.assertListEqual(result, expected)

    def test_multiple_newlines_at_end(self):
        """Tests handling of extra newlines at the end of the document."""
        markdown = "First block.\n\nSecond block.\n\n"
        result = markdown_to_blocks(markdown)
        expected = ["First block.", "Second block."]
        self.assertListEqual(result, expected)
        
    def test_odd_number_of_consecutive_newlines(self):
        """Tests that an odd number of consecutive newlines is treated the same as an even number."""
        markdown = "First block.\n\n\nSecond block.\n\n\n\n\nThird block."
        result = markdown_to_blocks(markdown)
        expected = [
            "First block.",
            "Second block.",
            "Third block.",
        ]
        self.assertListEqual(result, expected)
    #endregion

    #region block_to_block_type
    def test_paragraph(self):
        """Tests that a normal block of text is recognized as a paragraph."""
        block = "This is a regular paragraph with no special formatting."
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.PARAGRAPH)

    def test_heading_level_1(self):
        """Tests that a level 1 heading (#) is recognized."""
        block = "# Heading 1"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.HEADING)

    def test_heading_level_3(self):
        """Tests that a level 3 heading (###) is recognized."""
        block = "### Heading 3"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.HEADING)

    def test_code_block(self):
        """Tests that a triple backtick block is recognized as code."""
        block = "```\nSome code here\n```"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.CODE)

    def test_quote(self):
        """Tests that a block starting with > is recognized as a quote."""
        block = "> This is a blockquote."
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.QUOTE)

    def test_unordered_list_dash(self):
        """Tests that a block starting with - is recognized as an unordered list."""
        block = "- Item 1\n- Item 2\n- Item 3"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.UNORDERED_LIST)

    # We don't support this syntax, but maybe we should?
    # def test_unordered_list_asterisk(self):
    #     """Tests that a block starting with * is recognized as an unordered list."""
    #     block = "* Item A\n* Item B\n* Item C"
    #     result = block_to_block_type(block)
    #     self.assertEqual(result, BlockType.UNORDERED_LIST)

    def test_ordered_list(self):
        """Tests that a block starting with a number and a dot is recognized as an ordered list."""
        block = "1. First item\n2. Second item\n3. Third item"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.ORDERED_LIST)

    def test_invalid_ordered_list(self):
        """Tests that a malformed ordered list is not misclassified."""
        block = "1 First item\n2 Second item\n3 Third item"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.PARAGRAPH)

    def test_malformed_unordered_list(self):
        """Tests that a malformed unordered list is not misclassified."""
        block = "*Item 1\n-Item 2\n*Item 3"
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.PARAGRAPH)
    
    def test_all_heading_levels(self):
        """Tests that all heading levels (# to ######) are recognized correctly."""
        for level in range(1, 7):
            with self.subTest(level=level):
                block = f"{'#' * level} Heading {level}"
                result = block_to_block_type(block)
                self.assertEqual(result, BlockType.HEADING)

    def test_multiline_quote(self):
        """Tests that a multiline blockquote is correctly recognized as a quote."""
        block = "> This is a blockquote.\n> It has multiple lines.\n> And keeps going."
        result = block_to_block_type(block)
        self.assertEqual(result, BlockType.QUOTE)
        
    #endregion

    #region markdown_to_html_node
    def test_paragraphs(self):
        """Tests multiple paragraphs with inline formatting."""
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here
    """
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = (
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p>"
            "<p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>"
        )
        self.assertEqual(html, expected)

    def test_codeblock(self):
        """Tests preservation of formatting inside a fenced code block."""
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
        """
        node = markdown_to_html_node(md)
        html = node.to_html()
        expected = (
            "<div><pre><code>This is text that _should_ remain\n"
            "the **same** even with inline stuff\n</code></pre></div>"
        )
        self.assertEqual(html, expected)

    def test_minimal_paragraph(self):
        """Tests a single short paragraph."""
        md = "Just one line."
        html = markdown_to_html_node(md).to_html()
        expected = "<div><p>Just one line.</p></div>"
        self.assertEqual(html, expected)

    def test_minimal_heading(self):
        """Tests a heading with a single character of content."""
        md = "# H"
        html = markdown_to_html_node(md).to_html()
        expected = "<div><h1>H</h1></div>"
        self.assertEqual(html, expected)

    def test_multiline_quote(self):
        """Tests blockquotes that span multiple lines."""
        md = "> line one\n> line two\n> line three"
        html = markdown_to_html_node(md).to_html()
        expected = "<div><blockquote>line one\nline two\nline three</blockquote></div>"
        self.assertEqual(html, expected)

    # We don't support nesting, though we probably should...
    # def test_nested_inline_formatting(self):
    #     """Tests bold containing italic inside a paragraph."""
    #     md = "This is **bold and _italic_** text"
    #     html = markdown_to_html_node(md).to_html()
    #     expected = "<div><p>This is <b>bold and <i>italic</i></b> text</p></div>"
    #     self.assertEqual(html, expected)

    def test_codeblock_preserves_all_content(self):
        """Tests that code blocks preserve content exactly."""
        md = "```\ndef func():\n    return '**bold** _italic_'\n```"
        html = markdown_to_html_node(md).to_html()
        expected = (
            "<div><pre><code>def func():\n    return '**bold** _italic_'\n</code></pre></div>"
        )
        self.assertEqual(html, expected)

    def test_ordered_list(self):
        """Tests parsing of a basic ordered list."""
        md = "1. One\n2. Two\n3. Three"
        html = markdown_to_html_node(md).to_html()
        expected = "<div><ol><li>One</li><li>Two</li><li>Three</li></ol></div>"
        self.assertEqual(html, expected)

    def test_unordered_list(self):
        """Tests parsing of a basic unordered list."""
        md = "- Apple\n- Banana\n- Cherry"
        html = markdown_to_html_node(md).to_html()
        expected = "<div><ul><li>Apple</li><li>Banana</li><li>Cherry</li></ul></div>"
        self.assertEqual(html, expected)

    def test_empty_string(self):
        """Tests that an empty markdown string raises a ValueError."""
        md = ""
        with self.assertRaises(ValueError) as context:
            markdown_to_html_node(md)
        self.assertEqual(str(context.exception), "ParentNode must have child nodes")


    def test_all_heading_levels(self):
        """Tests all heading levels from 1 to 6."""
        for i in range(1, 7):
            with self.subTest(level=i):
                md = f"{'#' * i} Heading {i}"
                html = markdown_to_html_node(md).to_html()
                expected = f"<div><h{i}>Heading {i}</h{i}></div>"
                self.assertEqual(html, expected)

    def test_unclosed_codeblock(self):
        """Tests that an unclosed code block raises a ValueError."""
        md = "```\nunclosed code block"
        with self.assertRaises(ValueError):
            markdown_to_html_node(md)

    def test_unclosed_bold(self):
        """Tests that unmatched bold delimiters raise a ValueError."""
        md = "This is **not closed"
        with self.assertRaises(ValueError):
            markdown_to_html_node(md)

    def test_paragraph_with_link_and_image(self):
        """Tests paragraphs that contain both a link and an image."""
        md = "A [link](https://example.com) and ![img](https://example.com/img.jpg) in text"
        html = markdown_to_html_node(md).to_html()
        expected = (
            "<div><p>A <a href=\"https://example.com\">link</a> and "
            "<img src=\"https://example.com/img.jpg\" alt=\"img\" /> in text</p></div>"
        )
        self.assertEqual(html, expected)

    def test_adjacent_blocks(self):
        """Tests several distinct block types used together."""
        md = "# Title\n\nSome text.\n\n- Item"
        html = markdown_to_html_node(md).to_html()
        expected = "<div><h1>Title</h1><p>Some text.</p><ul><li>Item</li></ul></div>"
        self.assertEqual(html, expected)
    
    #endregion

    #region extract_title
    def test_basic_title(self):
        """Tests extracting a basic title from the first line."""
        markdown = "# My Title\n\nSome content here."
        self.assertEqual(extract_title(markdown), "My Title")

    def test_empty_input_raises(self):
        """Tests that empty markdown input raises a ValueError."""
        with self.assertRaises(ValueError) as context:
            extract_title("")
        self.assertEqual(str(context.exception), "Markdown document cannot be empty")

    def test_missing_title_line_raises(self):
        """Tests that missing title line raises a ValueError."""
        markdown = "## Subtitle\nSome content"
        with self.assertRaises(ValueError) as context:
            extract_title(markdown)
        self.assertEqual(str(context.exception), "No title in markdown document")

    def test_multiple_title_lines_uses_first(self):
        """Tests that the first # title line is used."""
        markdown = "# First Title\n\n# Second Title\n\nSome text"
        self.assertEqual(extract_title(markdown), "First Title")

    def test_title_with_whitespace(self):
        """Tests that leading/trailing whitespace is stripped from the title."""
        markdown = "#    My Title With Spaces    \n\nContent"
        self.assertEqual(extract_title(markdown), "My Title With Spaces")

    def test_title_with_special_characters(self):
        """Tests that special characters in the title are preserved."""
        markdown = "# Hello @#$%^&*() World!"
        self.assertEqual(extract_title(markdown), "Hello @#$%^&*() World!")

    def test_title_not_on_first_line(self):
        """Tests that the function finds a title even if not on line 1."""
        markdown = "\n\n\n# Delayed Title\nContent"
        self.assertEqual(extract_title(markdown), "Delayed Title")

    def test_title_with_inline_formatting(self):
        """Tests that inline markdown formatting is preserved (not stripped)."""
        markdown = "# Welcome to **My Site**"
        self.assertEqual(extract_title(markdown), "Welcome to **My Site**")

    #endregion

if __name__ == "__main__":
    unittest.main()
