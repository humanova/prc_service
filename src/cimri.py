import json
import re
from itertools import islice

import requests
from duckduckgo_search import DDGS
from fuzzywuzzy import fuzz
from bs4 import BeautifulSoup


ddgs = DDGS()

cookies = {
    'cimri_device_id': 'd32abf0e-7e0b-460f-9326-1564408f0b8e',
    'CimriCookiePolicy': '1',
    'cimri_location': '',
    '__cf_bm': 'Qnbhdj1Neuhe1lwdxra8fXznnAEW8mZ0a9m7Orad7ro-1678481298-0-AatYQKZ9sw0fRQI3kr1S06OhDp9HsVFSVt5c2AIIEuE2p8QtyeMTBGViDvKQbKf6SExuudSjoeUQ3Du5FMRn7v+friP8s++88YvmpVKcbllYdsafJUQ/DEhXLoDBmdBzjg==',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0',
    'Accept': '*/*',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Referer': 'https://www.cimri.com/market/arama',
    'content-type': 'application/json',
    'credentials': 'same-origin',
    'Origin': 'https://www.cimri.com',
    'DNT': '1',
    'Alt-Used': 'www.cimri.com',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}


def scrape_offers(html: str):
    soup = BeautifulSoup(html, 'html.parser')
    script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
    data = json.loads(script_tag.contents[0])
    offers = data['props']['pageProps']['product']['offersOnline']

    results = []
    for offer in offers:
        results.append({
            'store': f"{offer['merchantData']['name']} - {offer['depot']['merchantSellerName']}",
            'price': offer['price']
        })

    return results

def get_search_suggestions(query:str, limit:int=5):
    json_data = {
        'operationName': 'productServiceSuggestion',
        'variables': {
            'keyword': query,
        },
        'query': f'query productServiceSuggestion($keyword: String!) {{\n productServiceSuggestionQuery(keyword: $keyword, limit: {limit}) {{\nsuccess {{\n numFound\n categories {{\n category {{\n id \n name\n slug\n}}\n}}\nproducts {{\n id\n  title\n imageIds\n path\n}}\n}}\n }}\n}}\n'
    }
    response = requests.post('https://www.cimri.com/api/market-api', cookies=cookies, headers=headers, json=json_data)
    if response.status_code == 200:
        data = response.json()['data']
        products = data['productServiceSuggestionQuery']['success']['products']
        num_products = data['productServiceSuggestionQuery']['success']['numFound']
        print(f'Found {num_products} products')
    else: 
        return None

    return {"products": products, "item_count": num_products}

def get_product_offers(product_url:str):
    response = requests.get(product_url)
    if response.status_code == 200:
        return scrape_offers(response.text)
    else:
        return None

def get_duckduckgo_search_results(query:str, threshold:int=50):
    results = ddgs.text(f"{query} site:cimri.com", region="tr-tr", safesearch="Off")
    if results is not None:
        titles_with_similarity = []
        for result in islice(results, 10):
            # remove suffixes like "- cimri.com"
            title = re.sub("\s-\s\w+\.\w+", "", result['title'])
            similarity = fuzz.token_set_ratio(title, query)
            titles_with_similarity.append((title, similarity))

        titles_with_similarity.sort(key=lambda x: x[1], reverse=True)
        filtered_titles = [title for title, similarity in titles_with_similarity if similarity >= threshold]
        return filtered_titles
    else:
        return None

def save_product_image(image_id:int, resolution:tuple):
    url = f"https://cdn.cimri.io/market/{resolution[0]}x{resolution[1]}/-_{image_id}.jpg"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"{image_id}.jpg", 'wb') as f:
            f.write(response.content)