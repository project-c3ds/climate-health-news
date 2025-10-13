import json
import os
from pathlib import Path
from typing import Dict, List, Set

# ISO 639-2/T (3-letter) codes mapping from ISO 639-1 (2-letter) codes
ISO_2_TO_3 = {
    'en': 'eng',
    'cs': 'ces',
    'da': 'dan',
    'de': 'deu',
    'el': 'ell',
    'es': 'spa',
    'et': 'est',
    'fi': 'fin',
    'fr': 'fra',
    'ga': 'gle',
    'hr': 'hrv',
    'it': 'ita',
    'lt': 'lit',
    'lv': 'lav',
    'nl': 'nld',
    'pl': 'pol',
    'pt': 'por',
    'ro': 'ron',
    'sl': 'slv',
    'sv': 'swe',
    'sk': 'slk',
    'hu': 'hun',
    'bg': 'bul',
    'mt': 'mlt',
}


def collect_keywords_from_file(file_path: Path) -> Dict[str, List[str]]:
    """
    Read a JSON file and extract non-deprecated keywords.
    
    Args:
        file_path: Path to the JSON translation file
        
    Returns:
        Dictionary mapping language codes to lists of keywords
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = {}
    for lang_code, translations in data.items():
        keywords = []
        
        # Collect keywords from all non-deprecated categories
        for category, terms in translations.items():
            if category != 'deprecated' and isinstance(terms, list):
                keywords.extend(terms)
        
        result[lang_code] = keywords
    
    return result


def combine_translations_from_directory(
    directory: Path,
    output_file: Path
) -> None:
    """
    Combine all translation files from a single directory.
    
    Args:
        directory: Directory containing translation files
        output_file: Path to output combined JSON file
    """
    if not directory.exists():
        print(f"Warning: Directory {directory} does not exist")
        return
    
    # Dictionary to accumulate all keywords by language code
    combined: Dict[str, Set[str]] = {}
    
    json_files = sorted(directory.glob('*.json'))
    print(f"\nProcessing {len(json_files)} files from {directory.name}...")
    
    for json_file in json_files:
        print(f"  - {json_file.name}")
        file_keywords = collect_keywords_from_file(json_file)
        
        # Add keywords to combined dictionary
        for lang_code, keywords in file_keywords.items():
            if lang_code not in combined:
                combined[lang_code] = set()
            combined[lang_code].update(keywords)
    
    # Convert to 3-digit ISO codes and create final output
    output_data = {}
    for lang_2, keywords in combined.items():
        # Convert 2-letter to 3-letter code
        lang_3 = ISO_2_TO_3.get(lang_2, lang_2)
        
        # Convert set to sorted list for consistent output
        output_data[lang_3] = sorted(list(keywords))
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"Combined translations written to {output_file}")
    print(f"Total languages: {len(output_data)}")
    for lang, keywords in sorted(output_data.items()):
        print(f"  {lang}: {len(keywords)} keywords")


def main():
    """Main function to combine translation files."""
    # Define paths
    base_dir = Path(__file__).parent
    climate_dir = base_dir / 'data' / 'translations' / 'climate_official'
    health_dir = base_dir / 'data' / 'translations' / 'health_official'
    
    climate_output = base_dir / 'data' / 'translations' / 'climate_official_translations.json'
    health_output = base_dir / 'data' / 'translations' / 'health_official_translations.json'
    
    # Ensure output directory exists
    climate_output.parent.mkdir(parents=True, exist_ok=True)
    
    # Combine translations separately for climate and health
    combine_translations_from_directory(climate_dir, climate_output)
    combine_translations_from_directory(health_dir, health_output)


if __name__ == '__main__':
    main()

