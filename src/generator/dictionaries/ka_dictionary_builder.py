import requests
import re
from pathlib import Path
from collections import Counter
import random
import json
from utils import BASE_DIR


class GeorgianDictionaryBuilder:
    """Build a comprehensive Georgian word dictionary from Wikipedia"""

    def __init__(self):
        self.georgian_chars = "აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ"
        self.min_word_length = 2
        self.max_word_length = 20
        self.headers = {
            'User-Agent': 'GeorgianDictionaryBot/1.0 (Educational project; contact@example.com)'
        }

    def fetch_wikipedia_pages(self, num_pages: int = 100) -> list[str]:
        """Fetch random Georgian Wikipedia pages using the API"""
        all_text = []

        # Start with curated important pages
        seed_titles = [
            "საქართველო", "თბილისი", "საქართველოს_ისტორია",
            "ფიზიკა", "მათემატიკა", "ქიმია", "ბიოლოგია",
            "ლიტერატურა", "ხელოვნება", "მუსიკა", "სპორტი",
            "ეკონომიკა", "პოლიტიკა", "გეოგრაფია", "ფილოსოფია"
        ]

        print(f"Fetching {len(seed_titles)} seed pages...")
        for title in seed_titles:
            text = self._fetch_page_content(title)
            if text:
                all_text.append(text)

        # Fetch additional random pages
        remaining = num_pages - len(seed_titles)
        if remaining > 0:
            print(f"Fetching {remaining} random pages...")
            for i in range(remaining):
                text = self._fetch_random_page()
                if text:
                    all_text.append(text)
                if (i + 1) % 10 == 0:
                    print(f"  Fetched {i + 1}/{remaining} random pages...")

        return all_text

    def _fetch_page_content(self, title: str) -> str:
        """Fetch a specific Wikipedia page content"""
        url = "https://ka.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "titles": title,
            "prop": "extracts",
            "explaintext": True,
            "exlimit": 1
        }

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            for page_id, page_data in pages.items():
                if "extract" in page_data:
                    return page_data["extract"]
        except Exception as e:
            print(f"Error fetching page '{title}': {e}")

        return ""

    def _fetch_random_page(self) -> str:
        """Fetch a random Wikipedia page"""
        url = "https://ka.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "random",
            "rnnamespace": 0,
            "rnlimit": 1
        }

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            data = response.json()
            random_pages = data.get("query", {}).get("random", [])

            if random_pages:
                title = random_pages[0]["title"]
                return self._fetch_page_content(title)
        except Exception as e:
            print(f"Error fetching random page: {e}")

        return ""

    def extract_words(self, texts: list[str]) -> Counter:
        """Extract Georgian words and count their frequency"""
        word_counter = Counter()

        for text in texts:
            # Extract sequences of Georgian characters
            words = re.findall(r'[ა-ჰ]+', text)

            # Filter by length
            valid_words = [
                w for w in words
                if self.min_word_length <= len(w) <= self.max_word_length
            ]

            word_counter.update(valid_words)

        return word_counter

    def build_dictionary(self, num_pages: int = 100, min_frequency: int = 2) -> dict:
        """Build the complete dictionary with metadata"""
        print("Starting dictionary build...")

        # Fetch pages
        texts = self.fetch_wikipedia_pages(num_pages)
        print(f"Fetched {len(texts)} pages successfully")

        # Extract and count words
        word_counter = self.extract_words(texts)
        print(f"Found {len(word_counter)} unique words")

        # Filter by frequency
        filtered_words = {
            word: count for word, count in word_counter.items()
            if count >= min_frequency
        }
        print(f"After frequency filter (>={min_frequency}): {len(filtered_words)} words")

        # Categorize by frequency for weighted sampling
        total_count = sum(filtered_words.values())
        word_list = []

        for word, count in filtered_words.items():
            word_list.append({
                "word": word,
                "frequency": count,
                "weight": count / total_count,
                "length": len(word)
            })

        # Sort by frequency (most common first)
        word_list.sort(key=lambda x: x["frequency"], reverse=True)

        return {
            "words": word_list,
            "total_unique": len(word_list),
            "total_occurrences": total_count,
            "metadata": {
                "pages_scraped": len(texts),
                "min_frequency": min_frequency,
                "min_length": self.min_word_length,
                "max_length": self.max_word_length
            }
        }

    def save_dictionary(self, dictionary: dict, output_dir: Path):
        """Save dictionary in multiple formats"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save as JSON (with metadata)
        json_path = output_dir / "ka_dictionary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
        print(f"Saved JSON dictionary to {json_path}")

        # Save as plain text (just words, for quick loading)
        txt_path = output_dir / "ka_dictionary.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            for item in dictionary["words"]:
                f.write(f"{item['word']}\n")
        print(f"Saved text dictionary to {txt_path}")

        # Save frequency-weighted list (for sampling)
        weighted_path = output_dir / "ka_dictionary_weighted.txt"
        with open(weighted_path, "w", encoding="utf-8") as f:
            for item in dictionary["words"]:
                f.write(f"{item['word']}\t{item['frequency']}\n")
        print(f"Saved weighted dictionary to {weighted_path}")


if __name__ == "__main__":
    builder = GeorgianDictionaryBuilder()

    # Build dictionary from 100 Wikipedia pages
    dictionary = builder.build_dictionary(num_pages=1000, min_frequency=2)

    # Save to dictionaries folder
    output_dir = BASE_DIR / "src" / "generator" / "dictionaries"
    builder.save_dictionary(dictionary, output_dir)

    print("\n=== Dictionary Statistics ===")
    print(f"Total unique words: {dictionary['total_unique']}")
    print(f"Total occurrences: {dictionary['total_occurrences']}")
    print(f"\nTop 20 most common words:")
    for i, item in enumerate(dictionary['words'][:20], 1):
        print(f"  {i}. {item['word']} (frequency: {item['frequency']})")

