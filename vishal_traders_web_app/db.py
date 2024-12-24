from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Column, JSON, Date, func, table, Float
from flask_login import UserMixin

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
db = SQLAlchemy(model_class=Base)


# CREATE User TABLE
class User(UserMixin, db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


# Invoive Table
class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = Column(Integer, primary_key=True)
    invoice_no = Column(Integer, unique=True)
    customer_details = Column(JSON)
    goods_details = Column(JSON)
    total_amount = Column(JSON)
    date = Column(Date, nullable=False)


# Customer Table
class Customer(db.Model):
    __tablename__ = 'customer'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_name: Mapped[str] = mapped_column(String(1000))
    gst_no: Mapped[int] = mapped_column(Integer, unique=True)



#Daily Stock Update
class DailyStock(db.Model):
    __tablename__ = 'dailystock'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(1000))
    tins = mapped_column(JSON)
    total_quantity = mapped_column(Integer)
    date = mapped_column(Date, nullable=False)


#Stock Details
class Stock(db.Model):
    __tablename__ = 'stock'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    oil = mapped_column(JSON)
    tins_in_stock = mapped_column(Integer)
    other = mapped_column(JSON)
    date = mapped_column(Date, nullable=False)