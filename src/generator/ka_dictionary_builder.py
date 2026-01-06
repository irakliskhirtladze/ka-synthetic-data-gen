import requests
import re
from pathlib import Path


def build_ka_dict(output_path: Path):
    # Fetch a few Georgian Wikipedia pages
    urls = [
        "https://ka.wikipedia.org/wiki/საქართველო",
        "https://ka.wikipedia.org/wiki/საქართველოს_ისტორია",
        "https://ka.wikipedia.org/wiki/ფიზიოლოგია",
        "https://ka.wikipedia.org/wiki/მარქსიზმი",
        "https://ka.wikipedia.org/wiki/გეოლოგია",
        "https://ka.wikipedia.org/wiki/ფიზიკა",
    ]
    
    words = set()
    for url in urls:
        response = requests.get(url)
        # Extract only Georgian characters
        found = re.findall(r'[ა-ჰ]+', response.text)
        words.update(found)
    
    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(list(words))))
    
    print(f"Dictionary built with {len(words)} unique words.")


def get_random_word():
    """Get random word from the dict file"""
    with open("ka-dict", "r") as f:
        pass


def get_random_sequence():
    """Generate random sequence of georgian characters"""
    import random
    chars = "აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ1234567890"
    return "".join(random.choice(chars) for _ in range(random.randint(3, 10)))
