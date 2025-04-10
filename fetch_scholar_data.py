import requests
import json
import os
from datetime import datetime

# 配置参数
SERPAPI_KEY = os.getenv('SERPAPI_KEY')
AUTHOR_ID = 'UsixouIAAAAJ'  # 替换为您的用户 ID
OUTPUT_FILE = 'data/scholar_data.json'

# 构建 SerpApi 请求 URL
url = f'https://serpapi.com/search?engine=google_scholar_author&author_id={AUTHOR_ID}&api_key={SERPAPI_KEY}'

# 发送请求并获取数据
response = requests.get(url)
data = response.json()

# 提取所需信息
author_info = data.get('author', {})
citation_info = author_info.get('cited_by', {})
citation_graph = data.get('cited_by_graph', [])
publications = data.get('articles', [])

# 构建输出数据
output_data = {
    'last_updated': datetime.utcnow().isoformat() + 'Z',  # UTC 时间，ISO 格式
    'author': {
        'name': author_info.get('name'),
        'affiliations': author_info.get('affiliations'),
        'email': author_info.get('email'),
        'cited_by': {
            'total': citation_info.get('value'),
            'h_index': citation_info.get('h_index'),
            'i10_index': citation_info.get('i10_index'),
        },
    },
    'citation_graph': [
        {'year': point['year'], 'citations': point['citations']}
        for point in citation_graph
    ],
    'publications': [
        {
            'title': pub.get('title'),
            'link': pub.get('link'),
            'year': pub.get('year'),
            'citations': pub.get('cited_by', {}).get('value', 0),
            'authors': pub.get('authors', []),
            'publication': pub.get('publication', '')
        }
        for pub in publications
    ],

}

# 确保输出目录存在
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

# 保存数据到 JSON 文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=4)

print(f'Data successfully fetched and saved to {OUTPUT_FILE}')
