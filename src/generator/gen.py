from trdg.generators import GeneratorFromStrings
from utils import BASE_DIR
from pathlib import Path
import csv
import random


def generate_imgs():
    ka_font_dir = BASE_DIR / "src" / "generator" / "fonts" / "ka"
    output_dir = BASE_DIR / "data" / "raw"

    fonts = [str(f) for f in ka_font_dir.glob("*.ttf")]
    if not fonts:
        print(f"No .ttf fonts found in {ka_font_dir}")
        return

    metadata = []
    print(f"Generating images for {len(fonts)} fonts...")

    # Generation Loop
    for font_path in fonts:
        font_name = Path(font_path).stem

        source_type = random.random()
        if source_type < 0.75:  # Use real word - 75%
            text = random.choice(build_ka_dict)
        elif source_type < 0.95:  # Use random character sequence - 20%
            text = get_random_sequence(random.randint(5, 10))
        else:  # Use a number or date - 5%
            text = str(random.randint(1000, 999999))
        
        # Initialize the generator for this specific font
        generator = GeneratorFromStrings(
            strings=strings,
            count=len(strings), # One image per string per font
            fonts=[font_path],
            language="ka",
            size=64,            # Ideal height for TrOCR
            distorsion_type=3,  # 3 = Random Sine/Cosine waves
            blur=1,             # Slight blur for realism
            random_blur=True
        )

        for i, (img, lbl) in enumerate(generator):
            if img is None:
                print(f"Warning: Generator returned None for font {font_name} and text '{lbl}'. Skipping...")
                continue

            file_name = f"{font_name}_{i}.png"
            img_save_path = output_dir / file_name
            
            # Save Image
            img.save(img_save_path)
            
            # Save Metadata (Image name and the Georgian text)
            metadata.append({"file_name": file_name, "text": lbl})

    # Write Labels to CSV
    csv_path = BASE_DIR / "data" / "labels.csv"
    with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["file_name", "text"])
        writer.writeheader()
        writer.writerows(metadata)

    print(f"Finished! {len(metadata)} images saved to {output_dir}")
    print(f"Labels saved to {csv_path}")
