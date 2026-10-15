"""Generate the profile's single banner using Python's standard library."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
FONT = "-apple-system, BlinkMacSystemFont, 'Helvetica Neue', Arial, sans-serif"


def text(x, y, value, size, color, weight=400):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" font-weight="{weight}">{escape(value)}</text>')


def main():
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="240" viewBox="0 0 1200 240" role="img" aria-labelledby="title desc">',
        '<title id="title">Prabal Pratap Singh — Software Engineer</title>',
        '<desc id="desc">London-based software engineer. First Class MEng in Computer Science, University of Birmingham. Applications, backend systems, desktop software, and machine learning.</desc>',
        '<rect width="1200" height="240" rx="18" fill="#f5f5f7"/>',
        text(48, 88, 'Prabal Pratap Singh', 48, '#1d1d1f', 600),
        text(48, 136, 'Software Engineer', 25, '#0071e3', 500),
        text(48, 181, 'Applications · Backend systems · Desktop software · Machine learning', 18, '#6e6e73'),
        text(48, 216, 'MEng Computer Science · First Class · University of Birmingham', 15, '#6e6e73'),
        text(1070, 43, 'London', 14, '#6e6e73'),
        '</svg>',
    ]
    svg = '\n'.join(parts) + '\n'
    ET.fromstring(svg)
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / 'profile-hero.svg').write_text(svg)


if __name__ == '__main__':
    main()
