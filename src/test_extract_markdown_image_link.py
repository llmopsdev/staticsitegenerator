import unittest
from extract_markdown_image_link import extract_markdown_images, extract_markdown_links
from textnode import TextNode, TextType, split_nodes_links, split_nodes_images

class TestMarkdownImageExtraction(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    def test_split_images(self):
        # ── 1. two images in the middle ──────────────────────────────────────────
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_images([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

        # ── 2. image at the very beginning ───────────────────────────────────────
        node = TextNode(
            "![start](https://example.com/start.png) then more text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_images([node])
        self.assertListEqual(
            [
                TextNode("start", TextType.IMAGE, "https://example.com/start.png"),
                TextNode(" then more text", TextType.TEXT),
            ],
            new_nodes,
        )

        # ── 3. image at the very end ─────────────────────────────────────────────
        node = TextNode(
            "Text before ![end](https://example.com/end.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_images([node])
        self.assertListEqual(
            [
                TextNode("Text before ", TextType.TEXT),
                TextNode("end", TextType.IMAGE, "https://example.com/end.png"),
            ],
            new_nodes,
        )

        # ── 4. adjacent images with no text between ──────────────────────────────
        node = TextNode(
            "Pics: ![one](https://a.com/1.png)![two](https://b.com/2.png) done.",
            TextType.TEXT,
        )
        new_nodes = split_nodes_images([node])
        self.assertListEqual(
            [
                TextNode("Pics: ", TextType.TEXT),
                TextNode("one", TextType.IMAGE, "https://a.com/1.png"),
                TextNode("two", TextType.IMAGE, "https://b.com/2.png"),
                TextNode(" done.", TextType.TEXT),
            ],
            new_nodes,
        )

        # ── 5. no images at all  – should return the original node ───────────────
        node = TextNode("Just plain text, nothing to split.", TextType.TEXT)
        self.assertListEqual([node], split_nodes_images([node]))

        # ── 6. malformed image (missing “)”) must raise ValueError ───────────────
        node = TextNode("Broken ![bad](https://example.com/no‑close", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_images([node])
