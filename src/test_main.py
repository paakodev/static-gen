import os
import shutil
import unittest
from pathlib import Path
from main import copy_files, clean_dir, publish

TEST_ROOT = Path(__file__).parent / "test_data"
INPUT_DIR = TEST_ROOT / "input"
OUTPUT_DIR = TEST_ROOT / "output"
STATIC_DIR = TEST_ROOT / "static"

class TestStaticSiteBuilder(unittest.TestCase):
    def setUp(self):
        os.makedirs(INPUT_DIR, exist_ok=True)
        os.makedirs(STATIC_DIR, exist_ok=True)
        with open(INPUT_DIR / "sample.txt", "w") as f:
            f.write("Sample content")
        with open(STATIC_DIR / "style.css", "w") as f:
            f.write("body { background: #fff; }")

    def tearDown(self):
        shutil.rmtree(TEST_ROOT, ignore_errors=True)

    def test_copy_files(self):
        copy_files(str(INPUT_DIR), str(OUTPUT_DIR))
        output_file = OUTPUT_DIR / "sample.txt"
        self.assertTrue(output_file.exists())
        with open(output_file) as f:
            self.assertEqual(f.read(), "Sample content")

    def test_clean_dir(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_DIR / "temp.txt", "w") as f:
            f.write("temp")
        self.assertTrue((OUTPUT_DIR / "temp.txt").exists())

        clean_dir(str(OUTPUT_DIR))
        self.assertFalse(OUTPUT_DIR.exists())

    def test_publish_runs_without_error(self):
        # This mostly just verifies integration flow
        content_dir = INPUT_DIR
        static_dir = STATIC_DIR
        output_dir = OUTPUT_DIR

        # Create content_dir and simulate that it's needed
        os.makedirs(content_dir, exist_ok=True)
        with open(content_dir / "index.md", "w") as f:
            f.write("# Hello World")

        # Debug can be enabled to track down errors. Will print a lot to the console, though.
        publish(str(content_dir), str(static_dir), str(output_dir), debug=False)

        self.assertTrue((OUTPUT_DIR / "style.css").exists())

if __name__ == "__main__":
    unittest.main()
