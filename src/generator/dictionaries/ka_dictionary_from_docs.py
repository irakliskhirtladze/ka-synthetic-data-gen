import re
import json
from pathlib import Path
from collections import Counter
import pymupdf as fitz
from docx import Document
from utils import BASE_DIR


class DocumentDictionaryBuilder:
    """Extract Georgian words from PDF and DOCX documents and merge with existing dictionary"""
    
    def __init__(self):
        self.georgian_chars = "აბგდევზთიკლმნოპჟრსტუფქღყშჩცძწჭხჯჰ"
        self.min_word_length = 2
        self.max_word_length = 30
        
    def extract_text_from_pdf(self, pdf_path: Path):
        """Extract text from PDF file using PyMuPDF"""
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error reading PDF {pdf_path.name}: {e}")
        return text
    
    def extract_text_from_docx(self, docx_path: Path):
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(docx_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {docx_path.name}: {e}")
        return text
    
    def extract_words(self, text):
        """Extract Georgian words with enhanced pattern matching"""
        word_counter = Counter()
        
        # Enhanced pattern to capture:
        # 1. Georgian words with hyphens: ნაწილ-ნაწილ
        # 2. Ordinals with numbers: მე-5, მე-10
        # 3. Georgian words with apostrophes: მ'ეუბნება
        # 4. Roman numerals: I, II, III, IV, V, VI, VII, VIII, IX, X, XI, XII, etc.
        # 5. Regular Georgian words
        patterns = [
            r'[ა-ჰ]+(?:-[ა-ჰ]+)+',  # Hyphenated Georgian words
            r'მე-\d+',                # Ordinals like მე-5
            r'[ა-ჰ]+-\d+',            # Georgian + number like საუკუნე-5
            r'[IVXLCDMivxlcdm]+(?=\s|$|[^\w])',  # Roman numerals (standalone)
            r'[ა-ჰ]+',                # Regular Georgian words
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            
            for word in matches:
                # Clean up: remove trailing punctuation but keep internal hyphens
                word = word.rstrip('.,;:!?»"\')')
                word = word.lstrip('«"\'(')
                
                # Validate it's not empty and within length bounds
                if word and self.min_word_length <= len(word) <= self.max_word_length:
                    # Ensure UTF-8 compatible (Georgian characters)
                    try:
                        word.encode('utf-8')
                        word_counter[word] += 1
                    except UnicodeEncodeError:
                        continue
        
        return word_counter
    
    def process_documents(self, docs_dir: Path):
        """Process all PDF and DOCX files in directory"""
        all_text = []
        
        pdf_files = list(docs_dir.glob("*.pdf"))
        docx_files = list(docs_dir.glob("*.docx"))
        
        total_files = len(pdf_files) + len(docx_files)
        print(f"Found {len(pdf_files)} PDF files and {len(docx_files)} DOCX files")
        print(f"Processing {total_files} documents...")
        
        processed = 0
        
        # Process PDFs
        for pdf_path in pdf_files:
            print(f"  [{processed+1}/{total_files}] Processing PDF: {pdf_path.name}")
            text = self.extract_text_from_pdf(pdf_path)
            if text:
                all_text.append(text)
            processed += 1
        
        # Process DOCX files
        for docx_path in docx_files:
            print(f"  [{processed+1}/{total_files}] Processing DOCX: {docx_path.name}")
            text = self.extract_text_from_docx(docx_path)
            if text:
                all_text.append(text)
            processed += 1
        
        print(f"Successfully extracted text from {len(all_text)} documents")
        return all_text
    
    def extract_words_from_documents(self, docs_dir: Path, min_frequency: int = 1):
        """Extract words from all documents with frequency counting"""
        texts = self.process_documents(docs_dir)
        
        print("\nExtracting Georgian words...")
        word_counter = Counter()
        
        for text in texts:
            words = self.extract_words(text)
            word_counter.update(words)
        
        print(f"Found {len(word_counter)} unique words from documents")
        
        # Filter by minimum frequency
        filtered_words = {
            word: count for word, count in word_counter.items()
            if count >= min_frequency
        }
        
        print(f"After frequency filter (>={min_frequency}): {len(filtered_words)} words")
        return filtered_words
    
    def load_existing_dictionary(self, dict_path: Path):
        """Load existing Wikipedia-based dictionary"""
        with open(dict_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def merge_dictionaries(self, existing_dict, new_words):
        """Merge new words from documents with existing Wikipedia dictionary"""
        print("\nMerging dictionaries...")
        
        # Create a lookup map for existing words
        existing_words_map = {item["word"]: item for item in existing_dict["words"]}
        
        # Track statistics
        updated_count = 0
        new_count = 0
        
        # Merge new words
        for word, frequency in new_words.items():
            if word in existing_words_map:
                # Update existing word frequency
                existing_words_map[word]["frequency"] += frequency
                updated_count += 1
            else:
                # Add new word
                existing_words_map[word] = {
                    "word": word,
                    "frequency": frequency,
                    "length": len(word)
                }
                new_count += 1
        
        print(f"  Updated {updated_count} existing words")
        print(f"  Added {new_count} new words")
        
        # Recalculate weights and total occurrences
        total_occurrences = sum(item["frequency"] for item in existing_words_map.values())
        
        for item in existing_words_map.values():
            item["weight"] = item["frequency"] / total_occurrences
        
        # Sort by frequency (descending)
        word_list = sorted(existing_words_map.values(), key=lambda x: x["frequency"], reverse=True)
        
        # Update metadata
        merged_dict = {
            "words": word_list,
            "total_unique": len(word_list),
            "total_occurrences": total_occurrences,
            "metadata": {
                **existing_dict["metadata"],
                "documents_processed": True,
                "total_sources": "Wikipedia + Documents"
            }
        }
        
        return merged_dict
    
    def save_dictionary(self, dictionary, output_dir: Path):
        """Save merged dictionary in multiple formats"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON (with metadata)
        json_path = output_dir / "ka_dictionary.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=4)
        print(f"\nSaved JSON dictionary to {json_path}")
        
        # Save as plain text (just words)
        txt_path = output_dir / "ka_dictionary.txt"
        with open(txt_path, "w", encoding="utf-8") as f:
            for item in dictionary["words"]:
                f.write(f"{item['word']}\n")
        print(f"Saved text dictionary to {txt_path}")
        
        # Save frequency-weighted list
        weighted_path = output_dir / "ka_dictionary_weighted.txt"
        with open(weighted_path, "w", encoding="utf-8") as f:
            for item in dictionary["words"]:
                f.write(f"{item['word']}\t{item['frequency']}\n")
        print(f"Saved weighted dictionary to {weighted_path}")


if __name__ == "__main__":
    builder = DocumentDictionaryBuilder()
    
    # Paths
    docs_dir = BASE_DIR / "data" / "docs"
    dict_dir = BASE_DIR / "src" / "generator" / "dictionaries"
    existing_dict_path = dict_dir / "ka_dictionary.json"
    
    print("=== Georgian Dictionary Builder from Documents ===\n")
    
    # Load existing Wikipedia dictionary
    print(f"Loading existing dictionary from {existing_dict_path}")
    existing_dict = builder.load_existing_dictionary(existing_dict_path)
    print(f"Loaded dictionary with {existing_dict['total_unique']} words")
    print(f"Total occurrences: {existing_dict['total_occurrences']}\n")
    
    # Extract words from documents (min_frequency=1)
    new_words = builder.extract_words_from_documents(docs_dir, min_frequency=1)
    
    # Merge dictionaries
    merged_dict = builder.merge_dictionaries(existing_dict, new_words)
    
    # Save merged dictionary
    builder.save_dictionary(merged_dict, dict_dir)
    
    print("\n=== Final Dictionary Statistics ===")
    print(f"Total unique words: {merged_dict['total_unique']}")
    print(f"Total occurrences: {merged_dict['total_occurrences']}")
    print(f"Increase: +{merged_dict['total_unique'] - existing_dict['total_unique']} words")
    
    print("\n=== Top 30 most common words ===")
    for i, item in enumerate(merged_dict['words'][:30], 1):
        print(f"  {i}. {item['word']} (frequency: {item['frequency']}, length: {item['length']})")
    
    print("\n=== Sample of new/rare words (last 20) ===")
    for item in merged_dict['words'][-20:]:
        print(f"  - {item['word']} (frequency: {item['frequency']})")
    
    print("\n✓ Dictionary successfully updated!")
