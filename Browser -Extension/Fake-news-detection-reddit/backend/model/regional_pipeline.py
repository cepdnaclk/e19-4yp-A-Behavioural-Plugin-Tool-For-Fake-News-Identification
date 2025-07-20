import pandas as pd
from geotext import GeoText

# Load the demonym and continent mappings once at import time
demonym_df = pd.read_csv('data/demonyms.csv', header=None, names=['demonym', 'country'])
continent_df = pd.read_csv('data/continents-map.csv', encoding='ISO-8859-1')

demonym_map = dict(zip(demonym_df['demonym'].str.lower(), demonym_df['country']))
continent_map = dict(zip(continent_df['name'], continent_df['sub-region']))

def classify_region(title: str) -> str:
    """
    Classify the sub-region of a news title using GeoText, demonym mapping, and continent mapping.

    Parameters:
        title (str): The title of the post or news.

    Returns:
        str: The sub-region (e.g., 'Southern Asia', 'Northern America') or 'Unknown'.
    """
    if not title or not isinstance(title, str):
        return "Unknown"

    places = GeoText(title)

    # Step 1: GeoText detection (cities, countries)
    for place in places.cities + places.countries:
        country = demonym_map.get(place.lower(), place)
        subregion = continent_map.get(country)
        if subregion:
            return subregion

    # Step 2: Fallback - check for demonyms in the title
    for word in title.lower().split():
        country = demonym_map.get(word)
        if country:
            subregion = continent_map.get(country)
            if subregion:
                return subregion

    return "Unknown"
