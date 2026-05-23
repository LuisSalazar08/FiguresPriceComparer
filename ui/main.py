import tkinter as tk
from tkinter import ttk, messagebox
import threading
import webbrowser
import requests
import io
import re
from PIL import Image, ImageTk
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers_API.goodsmile import GoodSmileScraper
from scrapers_API.zenmarket import ZenMarketScraper
from scrapers_API.hobbylinkjpn import HLJScraper


class PriceComparerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anime Best Prices")
        self.root.geometry("1150x850")  # Increased height for the table!
        self.root.configure(bg="#f4f4f9")

        self.scrapers = [
            GoodSmileScraper(),
            ZenMarketScraper(),
            HLJScraper()
        ]

        self.image_cache = []
        self.setup_ui()

    def setup_ui(self):
        header_frame = tk.Frame(self.root, bg="#2c3e50", pady=15)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="ANIME BEST PRICES", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white").pack()

        search_frame = tk.Frame(self.root, bg="#ecf0f1", pady=15)
        search_frame.pack(fill=tk.X)

        tk.Label(search_frame, text="Search:", font=("Arial", 12, "bold"), bg="#ecf0f1").pack(side=tk.LEFT, padx=20)

        self.search_entry = tk.Entry(search_frame, width=40, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=10)
        self.search_entry.bind("<Return>", lambda event: self.start_search())

        self.search_btn = tk.Button(search_frame, text="FIND BEST PRICES", command=self.start_search, bg="#e74c3c",
                                    fg="white", font=("Arial", 10, "bold"), padx=10)
        self.search_btn.pack(side=tk.LEFT, padx=10)

        self.status_label = tk.Label(search_frame, text="", bg="#ecf0f1", fg="#7f8c8d", font=("Arial", 10, "italic"))
        self.status_label.pack(side=tk.LEFT, padx=15)

        # 3. Top Grid Area (For the 3 Best Cards)
        self.cards_frame = tk.Frame(self.root, bg="#f4f4f9")
        self.cards_frame.pack(fill=tk.X, padx=20, pady=15)

        self.cards_frame.grid_columnconfigure(0, weight=1)
        self.cards_frame.grid_columnconfigure(1, weight=1)
        self.cards_frame.grid_columnconfigure(2, weight=1)

        table_container = tk.Frame(self.root, bg="#f4f4f9")
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        tk.Label(table_container, text="All Figures Found (Sorted by Price) - Double Click a Row to Open Link",
                 font=("Arial", 10, "bold", "italic"), bg="#f4f4f9", fg="#7f8c8d").pack(anchor="w", pady=(0, 5))

        columns = ("Store", "Title", "Price", "Link")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings")

        self.tree.heading("Store", text="Store")
        self.tree.heading("Title", text="Figure Title")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Link", text="Direct Link")

        self.tree.column("Store", width=120, anchor=tk.W)
        self.tree.column("Title", width=450, anchor=tk.W)
        self.tree.column("Price", width=120, anchor=tk.CENTER)
        self.tree.column("Link", width=400, anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.open_link_from_table)

    def start_search(self):
        keyword = self.search_entry.get().strip()
        if not keyword:
            messagebox.showwarning("Warning", "Please enter a figure to search!")
            return

        self.search_btn.config(state=tk.DISABLED)
        self.status_label.config(text=f"Hunting for deals...", fg="#2980b9")

        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        self.image_cache.clear()
        for row in self.tree.get_children():
            self.tree.delete(row)

        threading.Thread(target=self.run_scrapers_and_fetch_images, args=(keyword,), daemon=True).start()

    def parse_price(self, price_str):
        if not price_str or "No Price" in price_str or "Unavailable" in price_str:
            return float('inf')

        clean_str = re.sub(r'[^\d.]', '', price_str)
        try:
            return float(clean_str)
        except ValueError:
            return float('inf')

    def run_scrapers_and_fetch_images(self, keyword):
        best_results = []
        all_results = []

        for scraper in self.scrapers:
            try:
                results = scraper.search_figure(keyword)

                if results:
                    all_results.extend(results)  # Store ALL data for the table

                    best_item = min(results, key=lambda x: self.parse_price(x['price']))

                    if self.parse_price(best_item['price']) == float('inf'):
                        continue

                    if best_item['image_url'] != "No Image":
                        try:
                            headers = {"User-Agent": "Mozilla/5.0"}
                            response = requests.get(best_item['image_url'], headers=headers, timeout=5)
                            if response.status_code == 200:
                                best_item['raw_image_data'] = response.content
                            else:
                                best_item['raw_image_data'] = None
                        except Exception:
                            best_item['raw_image_data'] = None
                    else:
                        best_item['raw_image_data'] = None

                    best_results.append(best_item)
            except Exception as e:
                print(f"Scraper error: {e}")

        all_results_sorted = sorted(all_results, key=lambda x: self.parse_price(x['price']))

        self.root.after(0, self.update_ui, best_results, all_results_sorted)

    def update_ui(self, best_results, all_results_sorted):
        for item in all_results_sorted:
            self.tree.insert("", tk.END, values=(
                item['store'],
                item['title'],
                item['price'],
                item['product_link']
            ))

        if not best_results:
            self.status_label.config(text="No available figures found.", fg="#c0392b")
            self.search_btn.config(state=tk.NORMAL)
            return

        for index, item in enumerate(best_results):
            card = tk.Frame(self.cards_frame, bg="white", relief="ridge", bd=2, padx=15, pady=15, width=320, height=480)
            card.grid(row=0, column=index, padx=10, pady=5, sticky="n")
            card.grid_propagate(False)

            tk.Label(card, text=item['store'].upper(), font=("Arial", 10, "bold"), fg="#8e44ad", bg="white").pack(
                anchor="center", pady=(0, 10))

            img_label = tk.Label(card, bg="white")
            img_label.pack(pady=5)

            if item.get('raw_image_data'):
                try:
                    image = Image.open(io.BytesIO(item['raw_image_data']))
                    image.thumbnail((220, 220))

                    bg = Image.new('RGB', (220, 220), (255, 255, 255))
                    offset_x = (220 - image.width) // 2
                    offset_y = (220 - image.height) // 2
                    bg.paste(image, (offset_x, offset_y))

                    photo = ImageTk.PhotoImage(bg)
                    img_label.config(image=photo)
                    self.image_cache.append(photo)
                except Exception:
                    img_label.config(text="[Image Error]", width=30, height=14, bg="#ecf0f1")
            else:
                img_label.config(text="[No Image]", width=30, height=14, bg="#ecf0f1")

            title_text = item['title'] if len(item['title']) < 80 else item['title'][:77] + "..."
            tk.Label(card, text=title_text, font=("Arial", 10, "bold"), bg="white", wraplength=280, height=3,
                     justify="center").pack(pady=5)

            tk.Label(card, text=item['price'], font=("Arial", 16, "bold"), fg="#27ae60", bg="white").pack(pady=5)

            btn = tk.Button(card, text="Go to Store", bg="#e67e22", fg="white", font=("Arial", 11, "bold"), pady=6,
                            command=lambda url=item['product_link']: webbrowser.open(url))
            btn.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 5))

        self.status_label.config(text=f"Analyzed {len(all_results_sorted)} figures across 3 stores!", fg="#27ae60")
        self.search_btn.config(state=tk.NORMAL)

    def open_link_from_table(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_values = self.tree.item(selected_item[0], "values")
            url = item_values[3]  # The 4th column is the link
            if url and url.startswith("http"):
                webbrowser.open(url)


if __name__ == "__main__":
    root = tk.Tk()
    app = PriceComparerApp(root)
    root.mainloop()