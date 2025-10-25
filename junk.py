import pandas as pd
from utils import load_sources

df = pd.read_json('data/database/lancet_europe_database.jsonl', lines=True)

sources = load_sources()

uris = sources[sources['country_name'] == 'United Kingdom']['source_uri'].unique().tolist()

# Extract the 'uri' from the source dictionary
df['source_uri'] = df['source'].apply(lambda x: x.get('uri') if isinstance(x, dict) else None)

df_uk = df[df['source_uri'].isin(uris)]

df_uk.to_parquet('data/database/lancet_europe_articles_uk.parquet')