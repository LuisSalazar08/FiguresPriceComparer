from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

class HLJScraper:
    def __init__(self):
        self.base_url = "https://www.hlj.com/search/"
        self.base_domain = "https://www.hlj.com"

    def search_figure(self, keyword):
        print(f"Fetching data from HobbyLink Japan for: '{keyword}'...")

        url = f"{self.base_url}?Word={keyword}"

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(url)
                page.wait_for_selector('div.price span.bold', timeout=10000)

                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')

                products = soup.find_all('div', class_='search-widget-block')
                results = []

                for item in products:
                    link_tag = item.find('a', class_='item-img-wrapper')
                    if not link_tag:
                        continue

                    product_link = self.base_domain + link_tag['href'] if 'href' in link_tag.attrs else "No Link"

                    img_tag = link_tag.find('img') if link_tag else None
                    image_url = "No Image"
                    if img_tag and 'src' in img_tag.attrs:
                        raw_src = img_tag['src']
                        image_url = f"https:{raw_src}" if raw_src.startswith('//') else raw_src

                    title_tag = item.find('p', class_='product-item-name')
                    title = title_tag.text.strip() if title_tag else (img_tag['alt'] if img_tag and 'alt' in img_tag.attrs else "Unknown Title")

                    price_container = item.find('div', class_='price')
                    if price_container:
                        exact_price_tag = price_container.find('span', class_='bold')
                        price = exact_price_tag.text.strip() if exact_price_tag else "No Price"
                    else:
                        price = "No Price"

                    figure_data = {
                        "store": "HobbyLink Japan",
                        "title": title,
                        "price": price,
                        "image_url": image_url,
                        "product_link": product_link
                    }
                    results.append(figure_data)

                return results

            except Exception as e:
                print(f"Error fetching data from HLJ: {e}")
                return []
            finally:
                browser.close()