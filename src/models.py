from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Consignor(db.Model):
    """Комитент."""
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
    consignor_returns = db.relationship('ConsignorReturn', back_populates='consignor', lazy=True)


class ConsignorReport(db.Model):
    """Акт приёма товара от комитента."""
    __tablename__ = 'consignor_reports'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор акта приёма
    number = db.Column(db.String(50), nullable=False, unique=True)  # Номер акта
    date = db.Column(db.Date, nullable=False)  # Дата акта
    description = db.Column(db.String(200), nullable=False)  # Описание
    consignor_id = db.Column(db.Integer, db.ForeignKey('consignors.id'), nullable=False)  # Идентификатор комитента
    commission_pct = db.Column(db.Numeric(5, 2), nullable=False, default=20)  # Процент комиссии
    commission_min = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Минимальная сумма комиссии

    consignor = db.relationship('Consignor', back_populates='consignor_reports')
    products = db.relationship('Product', back_populates='consignor_report', lazy=True)


class ConsignorReturn(db.Model):
    """Акт возврата товара комитенту."""
    __tablename__ = 'consignor_returns'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор акта возврата
    number = db.Column(db.String(50), nullable=False, unique=True)  # Номер акта
    date = db.Column(db.Date, nullable=False)  # Дата акта
    description = db.Column(db.String(200), nullable=True)  # Описание
    consignor_id = db.Column(db.Integer, db.ForeignKey('consignors.id'), nullable=False)  # Идентификатор комитента

    consignor = db.relationship('Consignor', back_populates='consignor_returns')
    products = db.relationship('Product', back_populates='consignor_return', lazy=True)


class Category(db.Model):
    """Категория товара."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор категории
    name = db.Column(db.String(100), nullable=False, unique=True)  # Название категории
    description = db.Column(db.String(200), nullable=True)  # Описание

    products = db.relationship('Product', back_populates='category', lazy=True)


class Product(db.Model):
    """Товар."""
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор товара
    product_name = db.Column(db.String(100), nullable=False)  # Наименование товара
    description = db.Column(db.String(500), nullable=True)  # Описание товара
    delivery_date = db.Column(db.Date, nullable=False)  # Дата доставки товара
    expiry_date = db.Column(db.Date, nullable=False)  # Срок реализации товара
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Цена товара
    status = db.Column(
        db.Enum('На витрине', 'Продан', 'Возвращён комитенту', name='product_status'),
        nullable=False,
        default='На витрине'  # Текущий статус товара
    )
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)  # Категория
    consignor_report_id = db.Column(db.Integer, db.ForeignKey('consignor_reports.id'), nullable=False)  # Идентификатор акта приёма
    consignor_return_id = db.Column(db.Integer, db.ForeignKey('consignor_returns.id'), nullable=True)  # Идентификатор акта возврата

    category = db.relationship('Category', back_populates='products')
    consignor_report = db.relationship('ConsignorReport', back_populates='products')
    consignor_return = db.relationship('ConsignorReturn', back_populates='products')
    sales = db.relationship('Sale', back_populates='product', lazy=True, order_by='Sale.sale_date')
    images = db.relationship('ProductImage', back_populates='product', lazy=True,
                             cascade='all, delete-orphan')


class ProductImage(db.Model):
    """Фотография товара, хранится на файловой системе."""
    __tablename__ = 'product_images'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор
    filename = db.Column(db.String(255), nullable=False)  # Имя файла
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Идентификатор товара

    product = db.relationship('Product', back_populates='images')


class Sale(db.Model):
    """Продажа товара."""
    __tablename__ = 'sales'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор продажи
    sale_date = db.Column(db.DateTime, nullable=False)  # Дата и время продажи
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)  # Цена продажи
    commission = db.Column(db.Numeric(10, 2), nullable=False)  # Сумма комиссии
    status = db.Column(
        db.Enum('Ожидает оплаты', 'Оплачено', 'Возврат от покупателя', name='sale_status'),
        nullable=False  # Статус
    )
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)  # Идентификатор товара

    product = db.relationship('Product', back_populates='sales')
    report_lines = db.relationship('SalesReportLine', back_populates='sale', lazy=True)


class SalesReport(db.Model):
    """Отчёт по продажам за период (snapshot)."""
    __tablename__ = 'sales_reports'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор отчёта
    number = db.Column(db.String(50), nullable=False, unique=True)  # Номер отчёта
    date = db.Column(db.Date, nullable=False)  # Дата формирования
    date_from = db.Column(db.Date, nullable=False)  # Начало периода
    date_to = db.Column(db.Date, nullable=False)  # Конец периода
    description = db.Column(db.String(200), nullable=True)  # Примечание
    total_revenue = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Итого выручка
    total_commission = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Итого комиссия
    total_payable = db.Column(db.Numeric(10, 2), nullable=False, default=0)  # Итого к выплате комитентам

    lines = db.relationship('SalesReportLine', back_populates='report', lazy=True,
                            cascade='all, delete-orphan',
                            order_by='SalesReportLine.sale_date')


class SalesReportLine(db.Model):
    """Строка отчёта по продажам — snapshot данных на момент формирования."""
    __tablename__ = 'sales_report_lines'

    id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор строки
    report_id = db.Column(db.Integer, db.ForeignKey('sales_reports.id'), nullable=False)  # Идентификатор отчёта
    sale_id = db.Column(db.Integer, db.ForeignKey('sales.id'), nullable=True)  # Ссылка на продажу (может быть удалена)

    # Snapshot полей на момент формирования отчёта
    sale_date = db.Column(db.DateTime, nullable=False)  # Дата и время продажи (snapshot)
    product_name = db.Column(db.String(100), nullable=False)  # Наименование товара
    category_name = db.Column(db.String(100), nullable=True)  # Категория
    consignor_name = db.Column(db.String(150), nullable=False)  # ФИО комитента
    sale_price = db.Column(db.Numeric(10, 2), nullable=False)  # Цена продажи
    commission = db.Column(db.Numeric(10, 2), nullable=False)  # Комиссия магазина
    payable = db.Column(db.Numeric(10, 2), nullable=False)  # К выплате комитенту

    report = db.relationship('SalesReport', back_populates='lines')
    sale = db.relationship('Sale', back_populates='report_lines')
