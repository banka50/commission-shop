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

    reports = db.relationship('Report', back_populates='consignor', lazy=True)


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор отчета
    number = db.Column(db.String(50), nullable=False, unique=True)  # Номер отчета
    date = db.Column(db.Date, nullable=False)  # Дата отчета
    report_type = db.Column(
        db.Enum(
            'Ежедневный отчет', 'Еженедельный отчет', 'Ежемесячный отчет',
            'Квартальный отчет', 'Годовой отчет',
            name='report_type_enum'
        ),
        nullable=False  # Тип отчета
    )
    description = db.Column(db.String(200), nullable=False)  # Описание отчета
    consignor_id = db.Column(db.Integer, db.ForeignKey('consignors.id'), nullable=False)  # Идентификатор комитента

    consignor = db.relationship('Consignor', back_populates='reports')
    products = db.relationship('Product', back_populates='report', lazy=True)


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
    report_id = db.Column(db.Integer, db.ForeignKey('reports.id'), nullable=False)  # Идентификатор отчёта
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True)  # Идентификатор продажи

    report = db.relationship('Report', back_populates='products')
    sale = db.relationship('Sale', back_populates='products')
