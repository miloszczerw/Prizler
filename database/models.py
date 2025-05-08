from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    __table_args__ = {'sqlite_autoincrement': True}
    shop = Column(String)
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    name = Column(String)
    price = Column(Float)
    last_checked = Column(DateTime, default=datetime.utcnow)
    price_history = relationship("PriceHistory", back_populates="product")
    def get_lowest_price(self):
        return min([h.price for h in self.price_history])

class PriceHistory(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_history")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///prizler.db")
Session = sessionmaker(bind=engine)
session = Session()
