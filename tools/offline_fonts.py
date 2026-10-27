"""Remove optional remote-font links from generated offline HTML only."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


class FontLinks(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.offsets = [0]
        for line in text.splitlines(keepends=True):
            self.offsets.append(self.offsets[-1] + len(line))
        self.ranges = []

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag != "link" or urlsplit(values.get("href", "")).hostname not in {"fonts.googleapis.com", "fonts.gstatic.com"}:
            return
        line, column = self.getpos()
        start = self.offsets[line - 1] + column
        self.ranges.append((start, start + len(self.get_starttag_text())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html", type=Path)
    path = parser.parse_args().html
    text = path.read_text()
    links = FontLinks(text)
    links.feed(text)
    for start, end in reversed(links.ranges):
        text = text[:start] + text[end:]
    path.write_text(text)
    print(f"PASS: removed {len(links.ranges)} optional remote font links from offline output")


if __name__ == "__main__":
    main()
