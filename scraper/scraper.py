import requests
from bs4 import BeautifulSoup
import logging
from dataclasses import dataclass
from typing import Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProductData:
    url: str
    name: str
    price: Optional[float]
    shop: str

class MoreleScraper:
    def __init__(self):
        pass

    def scrape_morele(self, url: str) -> ProductData:
        if "morele.net" not in url:
            logger.warning(f"Pomijam nieobsługiwany URL: {url}")
            return ProductData(url=url, name="Nieobsługiwany sklep", price=None, shop="Unknown")

        return self._scrape_site(
            url,
            title_selector="h1.prod-name",
            price_selector="div#product_price",
            shop_name="Morele.pl"
        )

    def scrape_multiple(self, urls: List[str]) -> List[ProductData]:
        products_data = []
        for url in urls:
            logger.info(f"Scraping: {url}")
            data = self.scrape_morele(url)
            products_data.append(data)
        return products_data

    def _scrape_site(self, url: str, title_selector: str, price_selector: str, shop_name: str) -> ProductData:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            title_el = soup.select_one(title_selector)
            title = title_el.get_text(strip=True) if title_el else "Brak tytułu"
            if not title_el:
                logger.error(f"Nie znaleziono tytułu dla URL: {url}")

            price_el = soup.select_one(price_selector)
            if not price_el:
                logger.error(f"Nie znaleziono ceny dla URL: {url}")
                return ProductData(url=url, name=title, price=None, shop=shop_name)

            price_text = price_el.get_text(strip=True)
            price = self._parse_price(price_text)

            return ProductData(url=url, name=title, price=price, shop=shop_name)

        except Exception as e:
            logger.error(f"Błąd podczas scrapowania {shop_name}: {e}")
            return ProductData(url=url, name="Error", price=None, shop=shop_name)

    def _parse_price(self, price_text: str) -> Optional[float]:
        try:
            price_cleaned = price_text.replace(",", ".").replace("zł", "").replace(" ", "").strip()
            return float(price_cleaned) if price_cleaned else None
        except Exception as e:
            logger.error(f"Błąd podczas parsowania ceny: {e}")
            return None
