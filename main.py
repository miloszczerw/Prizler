from scraper.scraper import MoreleScraper, ProductData
from database.models import session, Product, PriceHistory
import schedule
import time
import logging
from typing import List
import json
import os
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceMonitor:
    def __init__(self):
        self.scraper = MoreleScraper()
        self.load_config()

    def load_config(self):
        try:
            with open("config.json") as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logger.error("Brak pliku config.json! Zatrzymuję działanie programu.")
            raise SystemExit("Brak pliku config.json!")

    def check_prices(self):
        logger.info("Rozpoczynam sprawdzanie cen...")
        products_data = self.scraper.scrape_multiple(self.config["product_urls"])
        
        for data in products_data:
            if not data.price:
                logger.warning(f"Brak ceny dla produktu {data.name}, pomijam.")
                continue

            product = session.query(Product).filter_by(url=data.url).first()

            if product:
                self._update_existing_product(product, data)
            else:
                self._add_new_product(data)

    def _update_existing_product(self, product: Product, data: ProductData):
        price_changed = product.price != data.price
        
        if price_changed:
            logger.info(f"Zmiana ceny dla {product.name}: {product.price} -> {data.price}")
            product.price = data.price
            product.last_checked = datetime.now(timezone.utc)
            session.commit()

        self._add_price_history(product.id, data.price)

    def _add_new_product(self, data: ProductData):
        logger.info(f"Dodaję nowy produkt: {data.name} ({data.price} {data.shop})")
        
        if data.price is not None:
            product = Product(
                url=data.url,
                name=data.name,
                price=data.price,
                shop=data.shop
            )
            session.add(product)
            session.commit()
            self._add_price_history(product.id, data.price)
        else:
            logger.warning(f"Brak ceny dla {data.name}, pomijam dodanie.")

    def _add_price_history(self, product_id: int, price: float):
        history_entry = PriceHistory(
            product_id=product_id,
            price=price
        )
        session.add(history_entry)
        session.commit()

    def run_scheduled(self, interval_hours=6):
        schedule.every(interval_hours).hours.do(self.check_prices)
        logger.info(f"Uruchomiono monitorowanie cen (co {interval_hours} godzin)")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    monitor = PriceMonitor()
    if os.getenv("RUN_ONCE", "false").lower() == "true":
        monitor.check_prices()
    else:
        monitor.run_scheduled()