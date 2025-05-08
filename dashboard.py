import streamlit as st
from scraper.scraper import MoreleScraper
from database.models import Product, PriceHistory, session
from datetime import datetime
import pandas as pd
import json
from sqlalchemy import create_engine

st.set_page_config(page_title="Prizler – Ceny z Morele", layout="centered", initial_sidebar_state="auto")
st.title("📉 Prizler – Monitoring cen produktów z Morele.pl")

engine = create_engine("sqlite:///prizler.db")
scraper = MoreleScraper()

st.markdown("### ➕ Dodaj nowy produkt")
with st.form("add_product_form"):
    new_url = st.text_input("🔗 Wklej link do produktu z Morele.net")
    submitted = st.form_submit_button("Dodaj produkt")

    if submitted:
        if "morele.net" in new_url:
            scraped = scraper.scrape_morele(new_url)

            if scraped.price is None:
                st.error("❌ Nie udało się pobrać ceny.")
            else:
                existing = session.query(Product).filter_by(url=new_url).first()
                if existing:
                    st.info("ℹ️ Ten produkt już istnieje w bazie.")
                else:
                    product = Product(
                        url=scraped.url,
                        name=scraped.name,
                        price=scraped.price,
                        shop=scraped.shop,
                        last_checked=datetime.now()
                    )
                    session.add(product)
                    session.commit()

                    history = PriceHistory(
                        product_id=product.id,
                        price=scraped.price,
                        timestamp=datetime.now()
                    )
                    session.add(history)
                    session.commit()

                    with open("config.json", "r+") as f:
                        config = json.load(f)
                        if new_url not in config["product_urls"]:
                            config["product_urls"].append(new_url)
                            f.seek(0)
                            json.dump(config, f, indent=2)
                            f.truncate()

                    st.success("✅ Produkt został dodany i załadowany.")
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.error("❌ Link musi pochodzić z domeny morele.net")

st.markdown("---")
st.markdown("### 📦 Wybierz produkt, aby zobaczyć szczegóły:")

@st.cache_data
def load_products():
    return pd.read_sql("SELECT * FROM products", engine)

products = load_products()

if products.empty:
    st.warning("🚨 Brak produktów w bazie danych.")
    st.stop()

selected_name = st.selectbox("Wybierz z listy:", products["name"])
product_id = products[products["name"] == selected_name]["id"].iloc[0]

@st.cache_data
def load_history(product_id):
    query = f"""
        SELECT timestamp, price
        FROM price_history
        WHERE product_id = {product_id}
        ORDER BY timestamp
    """
    return pd.read_sql(query, engine, parse_dates=["timestamp"])

history = load_history(product_id)

product_row = products[products["id"] == product_id].iloc[0]

st.markdown("---")
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🧾 Szczegóły produktu")
    st.markdown(f"**🛍 Nazwa:** {product_row['name']}")
    st.markdown(f"**🏬 Sklep:** {product_row['shop']}")
    st.markdown(f"**💰 Aktualna cena:** `{product_row['price']} zł`")

    min_price = history["price"].min() if not history.empty else None
    if min_price and product_row["price"] == min_price:
        st.success("🏆 Najniższa cena w historii!")

    st.markdown(f"[🔗 Link do produktu]({product_row['url']})")

with col2:
    st.subheader("📊 Historia cen")
    if history.empty:
        st.info("Brak danych historycznych.")
    else:
        st.line_chart(history.set_index("timestamp")["price"])

        if len(history) >= 2:
            avg_price = round(history["price"].mean(), 2)
            first_price = history["price"].iloc[0]
            last_price = history["price"].iloc[-1]
            diff = round(last_price - first_price, 2)
            pct_change = round((diff / first_price) * 100, 2)
            trend_icon = "⬇️" if diff < 0 else "⬆️"

            st.markdown("---")
            st.markdown("📊 **Statystyki cenowe**")
            st.markdown(f"- Średnia cena: `{avg_price} zł`")
            st.markdown(f"- Zmiana od pierwszego pomiaru: `{diff:+.2f} zł` ({pct_change:+.2f}%) {trend_icon}")

st.markdown("---")
st.caption("🔍 Prizler działa tylko z produktami z morele.net.")