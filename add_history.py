from database.models import session, Product, PriceHistory
from datetime import datetime, timedelta
import random

def add_fake_history(product: Product, days=10):
    base_price = product.price or 5000

    for i in range(days):
        fake_price = round(base_price + random.uniform(-200, 200), 2)
        timestamp = datetime.now() - timedelta(days=days - i)
        history = PriceHistory(product_id=product.id, price=fake_price, timestamp=timestamp)
        session.add(history)

    session.commit()
    print(f"Dodano historię cen dla produktu: {product.name}")

def main():
    products = session.query(Product).all()
    if not products:
        print("Brak produktów w bazie!")
        return

    for product in products:
        add_fake_history(product)

if __name__ == "__main__":
    main()
