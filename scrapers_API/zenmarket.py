import requests
from bs4 import BeautifulSoup

class ZenMarketScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        self.base_url = "https://zenmarket.jp/es/marketplace.aspx"
        self.base_domain = "https://zenmarket.jp"

    def search_figure(self, keyword):
        print(f"Fetching data from ZenMarket for: '{keyword}'...")

        params = {"q": keyword, "p": 1}

        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            products = soup.find_all('div', class_='product')
            results = []

            for item in products:
                link_tag = item.find('a', class_='product-link')
                if not link_tag:
                    continue

                product_link = self.base_domain + link_tag['href'] if 'href' in link_tag.attrs else "No Link"

                title_tag = item.find('h3', class_='item-title')
                title = title_tag['title'] if title_tag and 'title' in title_tag.attrs else title_tag.text.strip() if title_tag else "Unknown Title"

                price_tag = item.find('div', class_='price')
                if price_tag:
                    raw_price = price_tag.get_text(separator="\n").strip()
                    price = raw_price.splitlines()[0].strip()
                else:
                    price = "No Price"

                img_wrap = item.find('div', class_='img-wrap')
                img_tag = img_wrap.find('img') if img_wrap else None
                image_url = img_tag.get('data-src') or img_tag.get('src') or "No Image" if img_tag else "No Image"

                figure_data = {
                    "store": "ZenMarket",
                    "title": title,
                    "price": price,
                    "image_url": image_url,
                    "product_link": product_link
                }
                results.append(figure_data)

            return results

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from ZenMarket: {e}")
            return []