# 🧾 Prizler – Monitoring cen z Morele.net

**Prizler** to aplikacja do automatycznego śledzenia i wizualizacji cen produktów z serwisu [Morele.net](https://www.morele.net). Umożliwia dodawanie produktów przez interfejs webowy, przechowywanie historii cen oraz analizę zmian za pomocą wykresów.

---

## 🚀 Funkcje

- ✅ Automatyczne scrapowanie cen produktów z Morele.net
- 📈 Historia zmian cen zapisywana w bazie danych SQLite
- 💬 Interfejs webowy zbudowany w Streamlit
- 🧠 Statystyki: średnia cena, zmiana % od pierwszego pomiaru
- 🏆 Wyróżnienie najniższej ceny w historii
- 🔁 Monitorowanie cen w tle z harmonogramem

---

## 🛠️ Technologie

- Python 3.10+
- Streamlit
- SQLAlchemy (SQLite)
- BeautifulSoup
- schedule
- dotenv

---

## 🧩 Instalacja

1. Sklonuj repozytorium:

```bash
git clone https://github.com/twoj-login/prizler.git
cd prizler
