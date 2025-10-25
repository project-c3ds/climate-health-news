"""Utility functions to use across the package"""
import os
import json
import requests
import pandas as pd


def flatten(list_of_lists):
    '''
    Takes a list of lists and returns the flattned version.

    Args:
        list_of_lists: 
            A list of lists to flatten
    
    Returns: 
        The flattened list
    '''

    return [item for sublist in list_of_lists for item in sublist]


def load_sources(sources_file: str = 'data/sources/sources.csv') -> pd.DataFrame:
    """
    Load source URIs from a CSV file.
    
    Args:
        sources_file (str): Path to the sources CSV file
        
    Returns:
        pd.DataFrame: DataFrame containing source information
    """
    return pd.read_csv(sources_file)


def filter_sources_by_languages(sources_df: pd.DataFrame, languages: list, status: str = 'success') -> pd.DataFrame:
    """
    Filter sources by dominant languages and status.
    
    Args:
        sources_df (pd.DataFrame): DataFrame containing source information
        languages (list): List of language codes to filter by (e.g., ['eng', 'fra', 'deu'])
        status (str): Status to filter by (default: 'success')
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    return sources_df[
        (sources_df['status'] == status) & 
        (sources_df['dominant_language'].isin(languages))
    ]


def filter_sources_by_countries(sources_df: pd.DataFrame, countries: list, status: str = 'success') -> pd.DataFrame:
    """
    Filter sources by country names and status.
    
    Args:
        sources_df (pd.DataFrame): DataFrame containing source information
        countries (list): List of country names to filter by
        status (str): Status to filter by (default: 'success')
        
    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    return sources_df[
        (sources_df['status'] == status) & 
        (sources_df['country_name'].isin(countries))
    ]


def load_keywords(language: str, keywords_file: str = 'data/translations/climate_official_translations.json') -> list:
    """
    Load keywords from the translations JSON file for a specific language.
    Returns a list of normalized keywords (lowercase except for acronyms).
    
    Args:
        language (str): ISO 639-3 language code to load keywords for (e.g., 'eng', 'spa', 'deu')
        keywords_file (str): Path to the keywords JSON file (default: 'data/translations/climate_official_translations.json')
        
    Returns:
        list: List of normalized keywords for the specified language
    """
    import json
    
    def normalize_keyword(keyword: str) -> str:
        """
        Normalize keyword to lowercase, except for acronyms (all caps) which stay as is.
        
        Args:
            keyword (str): The keyword to normalize
            
        Returns:
            str: Normalized keyword
        """
        # Check if it's an acronym (all uppercase letters, length > 1)
        if keyword.isupper() and len(keyword) > 1:
            return keyword  # Keep acronyms as is
        else:
            return keyword.lower()  # Convert everything else to lowercase
    
    try:
        with open(keywords_file, 'r', encoding='utf-8') as f:
            keywords_dict = json.load(f)
        
        # Get keywords for the specified language
        if language not in keywords_dict:
            print(f"WARNING: Language '{language}' not found in {keywords_file}")
            print(f"Available languages: {', '.join(keywords_dict.keys())}")
            return []
        
        keywords = keywords_dict[language]
        
        if not keywords:
            print(f"WARNING: No keywords found for language '{language}'")
            return []
        
        # Normalize keywords (lowercase except for acronyms)
        normalized_keywords = [normalize_keyword(kw) for kw in keywords]
        
        print(f"Loaded {len(normalized_keywords)} keywords for {language}")
        
        return normalized_keywords
        
    except FileNotFoundError:
        print(f"Keywords file {keywords_file} not found")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file {keywords_file}: {e}")
        return []
    except Exception as e:
        print(f"Error loading keywords: {e}")
        return []


def download_image(url, save_path, timeout=10):
    """
    Downloads an image from a URL and saves it to a specified path.
    
    Args:
        url (str): The URL of the image to download.
        save_path (str): The path to save the image to.
        timeout (int): The number of seconds to wait before timing out.
    
    Returns:
        bool: Returns True if the image was downloaded successfully, False otherwise.
    """
    success = False
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                file.write(response.content)
            success = True
        else:
            print("Failed to download the image")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
    
    return success


def save_article_as_json(article: dict, articles_dir: str = 'data/articles') -> str:
    '''
    Save an article as a JSON file using its URI as the filename.

    Args:
        article (dict): Article data to save
        articles_dir (str): Directory to save the article JSON file

    Returns:
        str: Path to the saved file, or None if failed
    '''
    try:
        # Create articles directory if it doesn't exist
        os.makedirs(articles_dir, exist_ok=True)
        
        # Use article URI as filename
        if 'uri' not in article:
            print("WARNING: Article missing 'uri' field, cannot save")
            return None
            
        # Clean URI to make it filesystem-safe
        uri = article['uri']
        # Replace problematic characters with underscores
        safe_uri = uri.replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = f'{safe_uri}.json'
        filepath = os.path.join(articles_dir, filename)
        
        # Save article as JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(article, f, indent=2, ensure_ascii=False, default=str)
        
        return filepath
        
    except Exception as e:
        print(f"Error saving article to JSON: {e}")
        return None


def get_eea38_plus_uk_countries():
    """
    Load the list of EEA38 plus UK countries from constants.
    
    Returns:
        list: List of country names in the EEA38 plus UK region
    """
    return ["Albania", "Austria", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg", "Macedonia", "Malta", "Moldova", "Montenegro", "Netherlands", "Norway", "Poland", "Portugal", "Romania", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Turkey", "Ukraine", "United Kingdom"]
