import requests
import json
import os
from datetime import datetime

SERPAPI_KEY = os.getenv('SERPAPI_KEY')
AUTHOR_ID = 'UsixouIAAAAJ'
OUTPUT_FILE = 'data/scholar_data.json'

url = f"https://serpapi.com/search.json?engine=google_scholar_author&author_id={AUTHOR_ID}&api_key={SERPAPI_KEY}&hl=en&output=json&no_cache=true"

response = requests.get(url)
data = response.json()

author_info = data.get('author', {})
cited_by_info = data.get('cited_by', {})
table_data = cited_by_info.get('table', [])
graph_data = cited_by_info.get('graph', [])

# 提取 citations、h-index、i10-index（all & recent）
citations = table_data[0].get('citations', {}) if len(table_data) > 0 else {}
h_index = table_data[1].get('h_index', {}) if len(table_data) > 1 else {}
i10_index = table_data[2].get('i10_index', {}) if len(table_data) > 2 else {}

output_data = {
    'last_updated': datetime.utcnow().isoformat() + 'Z',
    'author': {
        'name': author_info.get('name'),
        'affiliations': author_info.get('affiliations'),
        'email': author_info.get('email'),
        'cited_by': {
            'citations': {
                'all': citations.get('all'),
                'since_2019': citations.get('since_2019') or citations.get('since_2020')
            },
            'h_index': {
                'all': h_index.get('all'),
                'since_2019': h_index.get('since_2019') or h_index.get('since_2020')
            },
            'i10_index': {
                'all': i10_index.get('all'),
                'since_2019': i10_index.get('since_2019') or i10_index.get('since_2020')
            }
        }
    },
    'citation_graph': [
        {'year': g.get('year'), 'citations': g.get('citations')}
        for g in graph_data
    ],
    'publications': [
        {
            'title': p.get('title'),
            'link': p.get('link'),
            'citation_id': p.get('citation_id'),
            'authors': p.get('authors'),
            'publication': p.get('publication'),
            'cited_by': {
                'value': p.get('cited_by', {}).get('value', 0),
                'link': p.get('cited_by', {}).get('link', '')
            },
            'year': p.get('year')
        }
        for p in data.get('articles', [])
    ]

}

os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f'Data updated and saved to {OUTPUT_FILE}')
