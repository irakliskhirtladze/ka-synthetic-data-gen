# Georgian Text-on-Image Synthetic Dataset Generator

Generate synthetic Georgian text images for OCR training.

## Setup
Using Python 3.10 and UV (not pip) is strongly recommended to avoid dependency hell.

1. **Install dependencies:**
   ```bash
   uv sync
   ```

2. **Create `.env` file** in project root:
   ```
   HF_TOKEN=your_huggingface_token
   HF_DATASET_REPO=your_username/your_dataset_name
   ```

   Get your HF token from: https://huggingface.co/settings/tokens

## Usage

### Generate Dataset

Edit `src/main.py` to set the number of images per font:

```python
from generator.gen import generate_imgs, dataset_to_hf

if __name__ == "__main__":
    generate_imgs(100)  # Generate 100 images per font
    dataset_to_hf()
```

Then run:

```bash
python src/main.py
```

### What Happens

1. **Generation**: Creates synthetic images in `data/raw/` with metadata in `data/metadata.csv`
   - Uses 67 Georgian fonts
   - 90% real Georgian words (from 100k+ word dictionary)
   - 7% random character sequences
   - 3% numbers/dates (except 4 fonts that do not support them)

2. **Upload to HF** (optional): 
   - Prompts you to zip and upload to Hugging Face
   - Creates `data/ka-ocr.zip` with all images and metadata
   - Uploads to your HF dataset repo
   - Overwrites existing zip file if present

## Dataset Structure

```
data/
├── raw/              # Generated images (gitignored)
│   ├── font1_0000.png
│   ├── font1_0001.png
│   └── ...
├── metadata.csv      # Image labels (gitignored)
└── ka-ocr.zip        # Zipped dataset for HF (gitignored)
```

## Notes

- Entire `data/` directory is gitignored
- Model training should be done separately on Kaggle
- This repo is for dataset generation only
