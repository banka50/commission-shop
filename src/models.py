from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Consignor(db.Model):
    __tablename__ = 'consignors'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор комитента
    last_name = db.Column(db.String(50), nullable=False)  # Фамилия комитента
    first_name = db.Column(db.String(50), nullable=False)  # Имя комитента
    middle_name = db.Column(db.String(50), nullable=True)  # Отчество комитента
    email = db.Column(db.String(100), nullable=False, unique=True)  # Email комитента
    phone_number = db.Column(db.String(20), nullable=False, unique=True)  # Номер телефона комитента
    passport_data = db.Column(db.String(50), nullable=False, unique=True)  # Паспортные данные комитента
    inn = db.Column(db.String(12), nullable=False, unique=True)  # ИНН комитента

    consignor_reports = db.relationship('ConsignorReport', back_populates='consignor', lazy=True)


class ConsignorReport(db.Model):
    """Акт приёма товара от комитента."""
    __tablename__ = 'consignor_reports'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор акта приёма
    number = db.Column(db.String(50), nullable=False, unique=True)  # Номер акта
    date = db.Column(db.Date, nullable=False)  # Дата акта
    description = db.Column(db.String(200), nullable=False)  # Описание
    consignor_id = db.Column(db.Integer, db.ForeignKey('consignors.id'), nullable=False)  # Идентификатор комитента

    consignor = db.relationship('Consignor', back_populates='consignor_reports')
    products = db.relationship('Product', back_populates='consignor_report', lazy=True)


class SalesReport(db.Model):
    """Отчёт по продажам за период."""
    __tablename__ = 'sales_reports'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор отчёта
    number = db.Column(db.String(50), nullable=False, unique=True)  # Номер отчёта
    date = db.Column(db.Date, nullable=False)  # Дата отчёта
    report_type = db.Column(
        db.Enum(
            'Ежедневный отчет', 'Еженедельный отчет', 'Ежемесячный отчет',
            'Квартальный отчет', 'Годовой отчет',
            name='report_type_enum'
        ),
        nullable=False  # Тип отчёта
    )
    description = db.Column(db.String(200), nullable=True)  # Описание


class Sale(db.Model):
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор продажи
    sale_date = db.Column(db.Date, nullable=False)  # Дата продажи
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)  # Цена продажи
    commission = db.Column(db.Numeric(10, 2), nullable=False)  # Комиссия
    status = db.Column(
        db.Enum('Оплачено', 'Ожидает', 'Возврат', name='sale_status'),
        nullable=False  # Статус
    )

    products = db.relationship('Product', back_populates='sale', lazy=True)


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор товара
    product_name = db.Column(db.String(100), nullable=False)  # Наименование товара
    description = db.Column(db.String(500), nullable=True)  # Описание товара
    delivery_date = db.Column(db.Date, nullable=False)  # Дата доставки товара
    expiry_date = db.Column(db.Date, nullable=False)  # Срок реализации товара
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Цена товара
    consignor_report_id = db.Column(db.Integer, db.ForeignKey('consignor_reports.id'), nullable=False)  # Идентификатор акта приёма
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True)  # Идентификатор продажи

    consignor_report = db.relationship('ConsignorReport', back_populates='products')
    sale = db.relationship('Sale', back_populates='products')
