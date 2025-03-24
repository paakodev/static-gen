import shutil
import traceback
from textnode import *
import argparse
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")

def publish(content_dir: str, static_dir: str, output_dir: str, debug: bool = False) -> None:
    clean_dir(output_dir, debug)
    copy_files(static_dir, output_dir, debug)

def clean_dir(dir_to_clean: str, debug: bool = False) -> None:
    if not dir_to_clean.startswith(PROJECT_ROOT):
        raise ValueError("Refusing to delete outside of the project")
    if not os.path.exists(dir_to_clean):
        if debug: print(f"Path '{dir_to_clean}' does not exist. Nothing to delete.")
        return
    try:
        if debug: print(f"Deleting {dir_to_clean}...")
        shutil.rmtree(dir_to_clean)
    except Exception as e:
        print(f"Could not delete: {e}")
        if debug: traceback.print_exc()

def copy_files(input_dir: str, output_dir: str, debug: bool = False) -> None:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if debug: print(f"Created output directory: {output_dir}")
    with os.scandir(input_dir) as entries:
        for entry in entries:
            if entry.is_file():
                output_file = os.path.join(output_dir, entry.name)
                if debug: print(f"Copying file: {entry.path} -> {output_file}")
                shutil.copy2(entry.path, output_file)
            elif entry.is_dir():
                new_input = os.path.join(input_dir, entry.name)
                new_output = os.path.join(output_dir, entry.name)
                if debug: print(f"Entering {new_input}...")
                copy_files(new_input, new_output, debug)

def main():
    parser = argparse.ArgumentParser(description='Generate static site from MarkDown')  
    parser.add_argument(  
        '--debug', '-d',
        action='store_true',
        help='print debugging information')  
    args = parser.parse_args()
    publish(CONTENT_DIR, STATIC_DIR, PUBLIC_DIR, args.debug)

if __name__ == "__main__":
    main()