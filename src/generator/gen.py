import json
from trdg.generators import GeneratorFromStrings
from utils import BASE_DIR
from pathlib import Path
import csv
import random
from PIL import ImageFont, ImageDraw, Image


def load_dictionary(dict_path: Path = None) -> tuple[list, list]:
    """Load dictionary once and return words with weights for efficient sampling"""
    if dict_path is None:
        dict_path = BASE_DIR / "src" / "generator" / "dictionaries" / "ka_dictionary.json"

    with open(dict_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    words = data["words"]
    word_list = [w["word"] for w in words]
    weights = [w["weight"] for w in words]
    return word_list, weights


def get_random_word(word_list: list, weights: list, exclude_special_chars: bool = False) -> str:
    """Get a random word from the dictionary with frequency weighting
    
    Args:
        word_list: List of words
        weights: Corresponding weights
        exclude_special_chars: If True, exclude words with hyphens or numbers
    """
    if exclude_special_chars:
        # Filter out words containing hyphens or numbers
        valid_indices = [i for i, word in enumerate(word_list) 
                        if '-' not in word and not any(c.isdigit() for c in word)]
        if valid_indices:
            filtered_words = [word_list[i] for i in valid_indices]
            filtered_weights = [weights[i] for i in valid_indices]
            chosen = random.choices(filtered_words, weights=filtered_weights, k=1)[0]
            return chosen
    
    chosen = random.choices(word_list, weights=weights, k=1)[0]
    return chosen


def get_random_sequence(length: int = None) -> str:
    """Generate random sequence of Georgian characters"""
    chars = "აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ"
    if length is None:
        length = random.randint(3, 12)
    return "".join(random.choice(chars) for _ in range(length))


def get_random_number() -> str:
    """Generate random number or date"""
    choice = random.random()

    if choice < 0.3:  # Simple number
        return str(random.randint(0, 9999))
    elif choice < 0.6:  # Date DD.MM.YYYY
        day = random.randint(1, 28)
        month = random.randint(1, 12)
        year = random.randint(1900, 2025)
        return f"{day:02d}.{month:02d}.{year}"
    elif choice < 0.8:  # Year only
        return str(random.randint(1800, 2025))
    else:  # Phone-like number
        return f"+995{random.randint(500000000, 599999999)}"


def font_not_supports_numbers(font_path: str) -> bool:
    """Check if font does NOT support Latin numerals (0-9)"""
    font_name = Path(font_path).stem.lower()
    # Known Georgian-only fonts without number support
    fonts_without_numbers = ['3d_unicode', 'notosansgeorgian', 'alkroundedmtav-medium', 'alkroundednusx-medium']
    return font_name in fonts_without_numbers


def generate_imgs(num_images_per_font):
    ka_font_dir = BASE_DIR / "src" / "generator" / "fonts" / "ka"
    output_dir = BASE_DIR / "data" / "raw"
    dict_path = BASE_DIR / "src" / "generator" / "dictionaries" / "ka_dictionary.json"

    # Get all font files (ttf and otf)
    fonts = [str(f) for f in ka_font_dir.glob("*") if f.suffix.lower() in ['.ttf', '.otf']]
    if not fonts:
        print(f"No font files (.ttf, .otf) found in {ka_font_dir}")
        return

    # Check which fonts don't support numbers
    fonts_without_number_support = {}
    for font_path in fonts:
        no_numbers = font_not_supports_numbers(font_path)
        fonts_without_number_support[font_path] = no_numbers
    
    fonts_no_nums = [Path(f).stem for f, no_support in fonts_without_number_support.items() if no_support]
    if fonts_no_nums:
        print(f"Fonts without number support: {', '.join(fonts_no_nums)}\n")

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = []
    
    print(f"Generating images for {len(fonts)} fonts...")
    print(f"Images per font: {num_images_per_font}")
    print(f"Total images to generate: {len(fonts) * num_images_per_font}")
    print(f"Distribution: 90% real words, 7% random sequences, 3% numbers (font-dependent)\n")

    # Load dictionary
    print("Loading dictionary...")
    word_list, weights = load_dictionary(dict_path)
    print(f"Loaded {len(word_list)} words with frequency weights\n")

    # Generation Loop
    for font_idx, font_path in enumerate(fonts):
        font_name = Path(font_path).stem
        print(f"[{font_idx+1}/{len(fonts)}] Processing font: {font_name}")
        
        # Check if this font does NOT support numbers
        no_number_support = fonts_without_number_support[font_path]
        
        # Generate text strings for this font
        strings = []
        for _ in range(num_images_per_font):
            source_type = random.random()
            
            # Adjust distribution based on font capabilities
            if no_number_support:
                # Georgian-only font: 90% real words, 10% random sequences
                # Exclude words with hyphens or numbers for these fonts
                if source_type < 0.9:
                    text = get_random_word(word_list, weights, exclude_special_chars=True)
                else:
                    text = get_random_sequence()
            else:
                # Font with number support: 90% real words, 7% random sequences, 3% numbers
                if source_type < 0.9:
                    text = get_random_word(word_list, weights)
                elif source_type < 0.97:
                    text = get_random_sequence()
                else:
                    text = get_random_number()
            
            strings.append(text)
        
        # Generate images one string at a time to control output
        for idx, text in enumerate(strings):
            generator = GeneratorFromStrings(
                strings=[text],  # Single string at a time
                fonts=[font_path],
                language="ka",
                size=64,  # Height of the generated image in pixels. Width is based on text length
                skewing_angle=5,  # Maximum angle for text skewing/rotation
                random_skew=True,  # Randomly applies skewing within the angle range
                blur=1,  # blur intensity: 0 - no blur, 3 - heavy blur
                random_blur=True,  # randomly applies blur 0 to specified blur value
                distorsion_type=3,  # Type of geometric distortion applied. 3 means mix of sine/cosine
                distorsion_orientation=2,  # Direction of distortion effect
                background_type=0,  # Background style: 0 - gaussian, 1 - white, 2 - Quasicrystal pattern, 3 - image
                text_color="#000000,#1a1a1a,#333333,#2b1a1a,#1a0f0f,#3d2b2b,#4a0000,#2d1f1f"
            )
            
            # Get the first (and should be only) image
            img = next(generator)
            
            if img is None:
                print(f"  Warning: Generator returned None for '{text}'. Skipping...")
                continue

            file_name = f"{font_name}_{idx:04d}.png"
            img_save_path = output_dir / file_name
            
            img.save(img_save_path)
            metadata.append({"file_name": file_name, "text": text})
        
        print(f"  Generated {len(strings)} images for {font_name}")

    # Write Labels to CSV
    csv_path = BASE_DIR / "data" / "metadata.csv"
    with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "text"])
        writer.writeheader()
        writer.writerows(metadata)

    print(f"\n✓ Finished! {len(metadata)} images saved to {output_dir}")
    print(f"✓ Labels saved to {csv_path}")


def dataset_to_hf():
    """allows user to automatically prepare dataset and push it to Hugging Face Hub."""
    user_response = input("\nWould you like to zip dataset and push to HF? (y/n) ")
    if user_response.lower() == "y":
        # create zip in data/, add images to it's root from raw/ and then add metadata.csv to it as well
        pass

        # Set up HF using access token and dataset address
        pass

        # Push zip file to HF
        pass

