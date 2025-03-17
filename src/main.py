from textnode import *

def main():
    tmp = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")
    print(tmp)

if __name__ == "__main__":
    main()