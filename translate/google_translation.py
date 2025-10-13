import pandas as pd
import os
import json
import glob
import re
from dotenv import load_dotenv
import google.generativeai as genai
from constants import keywords_climate_eng

load_dotenv()

language_to_iso639_3 = {
    'english': 'eng',
    'hungarian': 'hun',
    'french': 'fra',
    'estonian': 'est',
    'serbian': 'srp',
    'polish': 'pol',
    'lithuanian': 'lit',
    'albanian': 'sqi',
    'bulgarian': 'bul',
    'finnish': 'fin',
    'croatian': 'hrv',
    'turkish': 'tur',
    'slovenian': 'slv',
    'latvian': 'lav',
    'german': 'deu',
    'spanish': 'spa',
    'portuguese': 'por',
    'romanian': 'ron',
    'russian': 'rus',
    'slovak': 'slk',
    'ukrainian': 'ukr',
    'swedish': 'swe',
    'icelandic': 'isl',
    'macedonian': 'mkd',
    'dutch': 'nld',
    'greek': 'ell',
    'czech': 'ces',
    'italian': 'ita',
    'danish': 'dan'
}

def expand_translation_with_parentheses(translation):
    """
    Splits translations like 'IPCC (Milliríkjanefnd um loftslagsbreytingar)' 
    into ['IPCC', 'Milliríkjanefnd um loftslagsbreytingar'].
    
    Args:
        translation (str): Translation string that may contain parentheses
    
    Returns:
        list: List of translations (expanded if parentheses found)
    """
    # Pattern to match text with parentheses: "text (more text)"
    pattern = r'^(.+?)\s*\((.+?)\)\s*$'
    match = re.match(pattern, translation)
    
    if match:
        # Split into the part before parentheses and the part inside
        before = match.group(1).strip()
        inside = match.group(2).strip()
        return [before, inside]
    else:
        # No parentheses found, return as single-item list
        return [translation]

def save_translations_to_csv(translations, language):
    """
    Saves translations to a CSV file using pandas.
    
    Args:
        translations (dict): Dictionary of English to translated keywords
        language (str): Language code/name for the translations
    """
    # Define the output directory and filename
    output_dir = 'data/translations/checks'
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f'climate_keywords_{language.lower()}.csv')

    # Create DataFrame from translations
    df = pd.DataFrame({
        'English': list(translations.keys()),
        language: list(translations.values())
    })
    
    # Write to CSV using pandas
    df.to_csv(output_file, index=False, encoding='utf-8')

    print(f"\nTranslations saved to: {output_file}")


def save_translations_to_json(translations, language):
    """
    Saves translations to a JSON file in data/translations/json directory.
    
    Args:
        translations (dict): Dictionary of English to translated keywords
        language (str): Language code/name for the translations
    """
    # Define output directory and create if needed
    output_dir = 'data/translations/json'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create DataFrame from translations
    df = pd.DataFrame([
        {"english": eng, "translation": trans}
        for eng, trans in translations.items()
    ])
    
    # Define output file path
    output_file = os.path.join(output_dir, f'{language.lower()}.json')
    
    # Write to JSON file using pandas
    df.to_json(output_file, orient='records', force_ascii=False, indent=2)
    
    print(f"JSON translations saved to: {output_file}")


def translate_climate_keywords(language_name):
    """
    Translates climate keywords from English to the target language using Gemini 2.5 Flash Pro.
    
    Args:
        language_name (str): Full language name (e.g., 'Spanish', 'French', 'German')
    
    Returns:
        dict: Dictionary mapping English keywords to their translations
    """
    # Configure Gemini API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please add it to your .env file.")
    
    genai.configure(api_key=api_key)
    
    # Use Gemini 2.5 Flash Pro model
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    # Create a comprehensive prompt for batch translation
    keywords_list = "\n".join([f"{i+1}. {kw}" for i, kw in enumerate(keywords_climate_eng)])
    
    prompt = f"""Translate the following climate-related keywords from English to {language_name}.
Please maintain the exact same format with numbered lines. Preserve capitalization style and hyphenation where appropriate.
For acronyms (like GHG, EV, IPCC, NDC), provide the translated full form if applicable, otherwise keep the acronym.

{keywords_list}

Provide ONLY the translations in the same numbered format, nothing else."""

    try:
        print(f"Translating {len(keywords_climate_eng)} keywords to {language_name}...")
        response = model.generate_content(prompt)
        
        # Parse the response
        translations = {}
        translated_lines = response.text.strip().split('\n')
        
        for i, keyword in enumerate(keywords_climate_eng):
            if i < len(translated_lines):
                # Extract translation (remove numbering)
                translated_line = translated_lines[i].strip()
                # Remove number prefix (e.g., "1. " or "1) ")
                if '. ' in translated_line:
                    translation = translated_line.split('. ', 1)[1].strip()
                elif ') ' in translated_line:
                    translation = translated_line.split(') ', 1)[1].strip()
                else:
                    translation = translated_line
                
                translations[keyword] = translation
            else:
                translations[keyword] = keyword  # Fallback to original
        
        print(f"Successfully translated {len(translations)} keywords")
        return translations
        
    except Exception as e:
        print(f"Error during translation: {e}")
        raise


def translate_keywords_by_batches(language_name, batch_size=20):
    """
    Translates climate keywords in smaller batches for better reliability.
    
    Args:
        language_name (str): Full language name (e.g., 'Spanish', 'French', 'German')
        batch_size (int): Number of keywords per batch
    
    Returns:
        dict: Dictionary mapping English keywords to their translations
    """
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    all_translations = {}
    
    # Process in batches
    for i in range(0, len(keywords_climate_eng), batch_size):
        batch = keywords_climate_eng[i:i+batch_size]
        keywords_list = "\n".join([f"{j+1}. {kw}" for j, kw in enumerate(batch)])
        
        prompt = f"""Translate these climate keywords from English to {language_name}.
Maintain the numbered format. For acronyms, translate the full form if applicable.

{keywords_list}

Provide ONLY the translations in numbered format."""

        try:
            print(f"Translating batch {i//batch_size + 1} ({len(batch)} keywords)...")
            response = model.generate_content(prompt)
            
            translated_lines = response.text.strip().split('\n')
            
            for j, keyword in enumerate(batch):
                if j < len(translated_lines):
                    translated_line = translated_lines[j].strip()
                    if '. ' in translated_line:
                        translation = translated_line.split('. ', 1)[1].strip()
                    elif ') ' in translated_line:
                        translation = translated_line.split(') ', 1)[1].strip()
                    else:
                        translation = translated_line
                    
                    all_translations[keyword] = translation
                else:
                    all_translations[keyword] = keyword
                    
        except Exception as e:
            print(f"Error in batch {i//batch_size + 1}: {e}")
            # Add original keywords as fallback
            for keyword in batch:
                all_translations[keyword] = keyword
    
    return all_translations


if __name__ == "__main__":
    df = pd.read_csv('data/sources/sources.csv')

    # Filter for successful sources only
    df = df[df['status'] == 'success']

    # Keep unique languages
    languages = df['dominant_language'].unique().tolist()

    translations_dict = {'english': keywords_climate_eng}

    for language in languages:
        print(f"Translating to {language}")
        translations = translate_climate_keywords(language)
        # Convert translations dict to list in the same order as keywords_climate_eng
        translations_dict[language] = [translations.get(kw, kw) for kw in keywords_climate_eng]
        save_translations_to_json(translations, language)
        print(f"Translations saved to {language}.json")


translations_dict = {'eng': keywords_climate_eng}
json_files = glob.glob('data/translations/json/*.json')

# Read JSON files using json library and expand parentheses
for file in json_files:
    language_name = file.split('/')[-1].split('.')[0]
    # Convert language name to ISO 639-3 code
    iso_code = language_to_iso639_3.get(language_name, language_name)
    
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # Extract translation values and expand those with parentheses
        expanded_translations = []
        for item in data:
            translation = item['translation']
            # Expand translations with parentheses
            expanded = expand_translation_with_parentheses(translation)
            expanded_translations.extend(expanded)
        translations_dict[iso_code] = expanded_translations
    print(f"Loaded and expanded translations from {language_name}.json -> {iso_code}")


# Print statistics about expanded translations
print("\nTranslation statistics after expansion:")
for lang, translations in translations_dict.items():
    print(f"  {lang}: {len(translations)} keywords (original: {len(keywords_climate_eng)})")

# Save combined translations as a dictionary with language keys
# Each language has its own list of keywords (variable length)
output_data = {
    lang: translations 
    for lang, translations in translations_dict.items()
}

# Save combined translations to JSON using json library
with open('data/keywords_climate.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)
print(f"\nSaved combined translations to keywords_climate.json")

# Loop over json_files and save to CSV using pandas
for file in json_files:
    language = file.split('/')[-1].split('.')[0]
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.columns = ['english', language]
    df.to_csv(f'data/translations/checks/climate_keywords_{language}.csv', index=False)
    print(f"Saved {language} to CSV")