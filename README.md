# Anime Best Prices - Figure Price Comparer

A robust, multi-threaded Python desktop application built with **Tkinter** that allows users to search, centralize, and compare anime figure prices in real-time across multiple renowned international storefronts (**Good Smile Company**, **ZenMarket**, and **HobbyLink Japan**).

The system analyzes the network behavior of target websites, employing conventional static web scraping and browser automation to handle dynamic JavaScript rendering and local currency conversion systems.

## 🚀 Key Features

- **Multi-threaded Architecture:** Search routines and image downloads run asynchronously on a background thread, preventing the Graphical User Interface (GUI) from freezing or becoming unresponsive.
- **Visual Product Cards:** Prominently displays the top 3 best deals found (one per store) with a symmetrical layout, centered and proportionally resized images (using `Pillow`).
- **Comprehensive Sorted Table:** A bottom `Treeview` component lists all collected results, automatically sorted from lowest to highest price.
- **Direct Access:** Double-clicking any row in the table or clicking the "Go to Store" button on a card instantly opens the original product link in your default web browser.
- **Advanced Extraction Strategies:**
  - **Good Smile:** Intercepts internal XHR/AJAX requests to consume backend API endpoints and process data in structured JSON format.
  - **ZenMarket:** Fast HTML scraping that extracts metadata from element attributes to prevent visual noise and filter out unneeded text labels.
  - **HobbyLink Japan:** Automation via **Playwright** in hidden (*headless*) mode to wait for dynamic JavaScript scripts that inject localized currency conversions (MXN).

## 📁 Project Structure

```text
FiguresPriceComparer/
├── scrapers_api/
│   ├── __init__.py
│   ├── goodsmile.py
│   ├── zenMarket.py
│   └── hobbylinkjpn.py
├── UI/
│   └── main.py          
└── requirements.txt
