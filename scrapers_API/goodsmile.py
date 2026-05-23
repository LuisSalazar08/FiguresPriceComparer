import requests
import json
from bs4 import BeautifulSoup

class GoodSmileScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        self.api_url = "https://www.goodsmile.com/en/search/list"
        self.base_domain = "https://www.goodsmile.com"

    def search_figure(self, keyword):
        print(f"Fetching data from Good Smile for: '{keyword}'...")

        filter_data = {
            "search_keyword": keyword, "search_over18": False, "search_category": [],
            "search_maker": [], "search_title": [], "search_status": "0",
            "release_date_from": "", "release_date_to": "", "search_bonus": False,
            "search_exclusive": False, "search_sale": False, "search_sales_origin": False, "tag": []
        }

        params = {
            "filter": json.dumps(filter_data), "orderBy": 1, "limit": 60, "offset": 0, "couponId": "null", "searchIndex": -1
        }

        try:
            response = requests.get(self.api_url, headers=self.headers, params=params)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.find_all('div', class_='p-product-list__item')
            results = []

            for item in products:
                title_tag = item.find('h2', class_='c-title')
                title = title_tag.text.strip() if title_tag else "Unknown Title"

                price_tag = item.find('span', class_='c-price__main')
                price = price_tag.text.strip() if price_tag else "No Price / Unavailable"

                img_tag = item.find('img')
                image_url = self.base_domain + img_tag['src'] if img_tag and 'src' in img_tag.attrs else "No Image"

                link_tag = item.find('a', class_='p-product-list__link')
                product_link = self.base_domain + link_tag['href'] if link_tag and 'href' in link_tag.attrs else "No Link"

                figure_data = {
                    "store": "Good Smile",  # Added this so the UI knows the store!
                    "title": title,
                    "price": price,
                    "image_url": image_url,
                    "product_link": product_link
                }
                results.append(figure_data)

            return results

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Good Smile: {e}")
            return []