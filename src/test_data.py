"""Тестовые данные для инициализации базы данных."""
from datetime import datetime, date
from models import db, Consignor, ConsignorReport, ConsignorReturn, Category, Product, Sale, SalesReport, SalesReportLine


def _d(s: str) -> date:
    return datetime.strptime(s, '%Y-%m-%d').date()


CONSIGNORS = [
    {'last_name': 'Соколов',    'first_name': 'Иван',      'middle_name': 'Алексеевич',
     'email': 'ivan.sokolov@example.com',        'phone_number': '79001234567',
     'passport_data': '4510 123456', 'inn': '123456789012'},
    {'last_name': 'Морозова',   'first_name': 'Екатерина', 'middle_name': 'Дмитриевна',
     'email': 'ekaterina.morozova@example.com',  'phone_number': '79111234568',
     'passport_data': '4511 234567', 'inn': '234567890123'},
    {'last_name': 'Волков',     'first_name': 'Дмитрий',   'middle_name': 'Сергеевич',
     'email': 'dmitry.volkov@example.com',        'phone_number': '79221234569',
     'passport_data': '4512 345678', 'inn': '345678901234'},
    {'last_name': 'Зайцева',    'first_name': 'Анна',      'middle_name': 'Сергеевна',
     'email': 'anna.zaytseva@example.com',        'phone_number': '79331234570',
     'passport_data': '4513 456789', 'inn': '456789012345'},
    {'last_name': 'Кузнецов',   'first_name': 'Михаил',    'middle_name': 'Петрович',
     'email': 'mikhail.kuznetsov@example.com',    'phone_number': '79441234571',
     'passport_data': '4514 567890', 'inn': '567890123456'},
    {'last_name': 'Петрова',    'first_name': 'Ольга',     'middle_name': 'Васильевна',
     'email': 'olga.petrova@example.com',         'phone_number': '79551234572',
     'passport_data': '4515 678901', 'inn': '678901234567'},
    {'last_name': 'Смирнов',    'first_name': 'Андрей',    'middle_name': 'Николаевич',
     'email': 'andrey.smirnov@example.com',       'phone_number': '79661234573',
     'passport_data': '4516 789012', 'inn': '789012345678'},
]

CATEGORIES = [
    {'name': 'Верхняя одежда',  'description': 'Пальто, куртки, шубы'},
    {'name': 'Обувь',           'description': 'Сапоги, ботинки, туфли'},
    {'name': 'Аксессуары',      'description': 'Сумки, ремни, шарфы, шляпы'},
    {'name': 'Часы и украшения','description': 'Наручные часы, кольца, броши'},
    {'name': 'Посуда и декор',  'description': 'Сервизы, вазы, статуэтки'},
    {'name': 'Электроника',     'description': 'Телефоны, планшеты, фотоаппараты'},
    {'name': 'Книги и антиквариат', 'description': 'Старинные книги, монеты, марки'},
]

# consignor_id — 1-based порядковый номер из CONSIGNORS
CONSIGNOR_REPORTS = [
    {'number': 'ACT-001', 'date': '2025-08-10', 'consignor_id': 1,
     'commission_pct': 20, 'commission_min': 100,
     'description': 'Приёмка одежды и аксессуаров'},
    {'number': 'ACT-002', 'date': '2025-08-15', 'consignor_id': 2,
     'commission_pct': 25, 'commission_min': 150,
     'description': 'Приёмка обуви'},
    {'number': 'ACT-003', 'date': '2025-09-02', 'consignor_id': 3,
     'commission_pct': 20, 'commission_min': 100,
     'description': 'Приёмка посуды и часов'},
    {'number': 'ACT-004', 'date': '2025-09-10', 'consignor_id': 4,
     'commission_pct': 30, 'commission_min': 200,
     'description': 'Приёмка электроники'},
    {'number': 'ACT-005', 'date': '2025-09-20', 'consignor_id': 5,
     'commission_pct': 20, 'commission_min': 100,
     'description': 'Приёмка антиквариата и декора'},
    {'number': 'ACT-006', 'date': '2025-10-05', 'consignor_id': 6,
     'commission_pct': 25, 'commission_min': 150,
     'description': 'Приёмка верхней одежды'},
    {'number': 'ACT-007', 'date': '2025-11-03', 'consignor_id': 7,
     'commission_pct': 20, 'commission_min': 100,
     'description': 'Приёмка аксессуаров и украшений'},
    {'number': 'ACT-008', 'date': '2025-11-15', 'consignor_id': 1,
     'commission_pct': 20, 'commission_min': 100,
     'description': 'Доп. приёмка от Соколова'},
    {'number': 'ACT-009', 'date': '2025-12-01', 'consignor_id': 2,
     'commission_pct': 25, 'commission_min': 150,
     'description': 'Зимняя коллекция обуви'},
    {'number': 'ACT-010', 'date': '2026-01-10', 'consignor_id': 3,
     'commission_pct': 20, 'commission_min': 100,
     'description': 'Новогодняя приёмка'},
]

# category_id — 1-based из CATEGORIES, consignor_report_id — из CONSIGNOR_REPORTS
PRODUCTS = [
    # Верхняя одежда
    {'product_name': 'Пальто зимнее',      'category_id': 1, 'consignor_report_id': 1,
     'description': 'Женское, р.48, чёрное, шерсть',
     'delivery_date': '2025-08-10', 'expiry_date': '2026-03-10', 'price': 4500.00,
     'status': 'На витрине'},
    {'product_name': 'Куртка кожаная',     'category_id': 1, 'consignor_report_id': 6,
     'description': 'Мужская, р.52, чёрная',
     'delivery_date': '2025-10-05', 'expiry_date': '2026-04-05', 'price': 6800.00,
     'status': 'Продан'},
    {'product_name': 'Шуба норковая',      'category_id': 1, 'consignor_report_id': 6,
     'description': 'Женская, р.46, кофейная',
     'delivery_date': '2025-10-05', 'expiry_date': '2026-05-05', 'price': 28000.00,
     'status': 'На витрине'},
    {'product_name': 'Дублёнка мужская',   'category_id': 1, 'consignor_report_id': 8,
     'description': 'Р.50, натуральная, бежевая',
     'delivery_date': '2025-11-15', 'expiry_date': '2026-04-15', 'price': 9500.00,
     'status': 'На витрине'},
    # Обувь
    {'product_name': 'Ботинки кожаные',    'category_id': 2, 'consignor_report_id': 2,
     'description': 'Мужские, р.42, коричневые',
     'delivery_date': '2025-08-15', 'expiry_date': '2026-02-15', 'price': 3200.00,
     'status': 'Продан'},
    {'product_name': 'Сапоги зимние',      'category_id': 2, 'consignor_report_id': 9,
     'description': 'Женские, р.38, чёрные, натуральный мех',
     'delivery_date': '2025-12-01', 'expiry_date': '2026-05-01', 'price': 5400.00,
     'status': 'Продан'},
    {'product_name': 'Туфли замшевые',     'category_id': 2, 'consignor_report_id': 2,
     'description': 'Женские, р.37, бежевые',
     'delivery_date': '2025-08-15', 'expiry_date': '2026-02-15', 'price': 2100.00,
     'status': 'Возвращён комитенту'},
    {'product_name': 'Кроссовки Nike',     'category_id': 2, 'consignor_report_id': 9,
     'description': 'Р.44, белые, б/у',
     'delivery_date': '2025-12-01', 'expiry_date': '2026-06-01', 'price': 3800.00,
     'status': 'На витрине'},
    # Аксессуары
    {'product_name': 'Сумка женская',      'category_id': 3, 'consignor_report_id': 1,
     'description': 'Кожаная, бежевая, среднего размера',
     'delivery_date': '2025-08-10', 'expiry_date': '2026-03-10', 'price': 2800.00,
     'status': 'На витрине'},
    {'product_name': 'Шарф пуховый',       'category_id': 3, 'consignor_report_id': 1,
     'description': 'Оренбургский, белый, ажурный',
     'delivery_date': '2025-08-10', 'expiry_date': '2026-02-10', 'price': 1500.00,
     'status': 'Продан'},
    {'product_name': 'Ремень кожаный',     'category_id': 3, 'consignor_report_id': 7,
     'description': 'Мужской, коричневый, пряжка бронза',
     'delivery_date': '2025-11-03', 'expiry_date': '2026-05-03', 'price': 800.00,
     'status': 'На витрине'},
    {'product_name': 'Клатч вечерний',     'category_id': 3, 'consignor_report_id': 7,
     'description': 'Чёрный, расшит бисером',
     'delivery_date': '2025-11-03', 'expiry_date': '2026-05-03', 'price': 1900.00,
     'status': 'Продан'},
    # Часы и украшения
    {'product_name': 'Часы наручные Seiko','category_id': 4, 'consignor_report_id': 3,
     'description': 'Механические, мужские, сталь',
     'delivery_date': '2025-09-02', 'expiry_date': '2026-03-02', 'price': 12500.00,
     'status': 'Продан'},
    {'product_name': 'Брошь золотая',      'category_id': 4, 'consignor_report_id': 7,
     'description': '585 проба, в форме бабочки',
     'delivery_date': '2025-11-03', 'expiry_date': '2026-11-03', 'price': 7200.00,
     'status': 'На витрине'},
    {'product_name': 'Кольцо серебряное',  'category_id': 4, 'consignor_report_id': 10,
     'description': '925 проба, с аметистом',
     'delivery_date': '2026-01-10', 'expiry_date': '2027-01-10', 'price': 1800.00,
     'status': 'На витрине'},
    # Посуда и декор
    {'product_name': 'Сервиз чайный',      'category_id': 5, 'consignor_report_id': 3,
     'description': 'Фарфор, 12 персон, позолота',
     'delivery_date': '2025-09-02', 'expiry_date': '2026-09-02', 'price': 8900.00,
     'status': 'Продан'},
    {'product_name': 'Ваза хрустальная',   'category_id': 5, 'consignor_report_id': 5,
     'description': 'Богемское стекло, ручная резьба',
     'delivery_date': '2025-09-20', 'expiry_date': '2026-09-20', 'price': 3400.00,
     'status': 'На витрине'},
    {'product_name': 'Статуэтка фарфоровая','category_id': 5, 'consignor_report_id': 5,
     'description': 'Балерина, ЛФЗ, 1960-е',
     'delivery_date': '2025-09-20', 'expiry_date': '2026-09-20', 'price': 2200.00,
     'status': 'Продан'},
    # Электроника
    {'product_name': 'Фотоаппарат Canon',  'category_id': 6, 'consignor_report_id': 4,
     'description': 'EOS 600D, kit 18-55, б/у хорошее',
     'delivery_date': '2025-09-10', 'expiry_date': '2026-03-10', 'price': 14500.00,
     'status': 'Продан'},
    {'product_name': 'Планшет Samsung',    'category_id': 6, 'consignor_report_id': 4,
     'description': 'Galaxy Tab A7, 64GB, б/у отличное',
     'delivery_date': '2025-09-10', 'expiry_date': '2026-03-10', 'price': 11000.00,
     'status': 'Продан'},
    {'product_name': 'Наушники Sony',      'category_id': 6, 'consignor_report_id': 4,
     'description': 'WH-1000XM4, шумоподавление',
     'delivery_date': '2025-09-10', 'expiry_date': '2026-03-10', 'price': 9800.00,
     'status': 'Продан'},
    # Книги и антиквариат
    {'product_name': 'Монеты царской России', 'category_id': 7, 'consignor_report_id': 5,
     'description': 'Лот из 15 монет, 1880–1917',
     'delivery_date': '2025-09-20', 'expiry_date': '2026-09-20', 'price': 18000.00,
     'status': 'На витрине'},
    {'product_name': 'Книга «Война и мир»', 'category_id': 7, 'consignor_report_id': 5,
     'description': 'Толстой, 1-е советское изд. 1928 г.',
     'delivery_date': '2025-09-20', 'expiry_date': '2026-09-20', 'price': 4500.00,
     'status': 'Продан'},
    {'product_name': 'Марки СССР 1950-х',  'category_id': 7, 'consignor_report_id': 5,
     'description': 'Альбом, 120 штук, кат. состояние',
     'delivery_date': '2025-09-20', 'expiry_date': '2026-09-20', 'price': 6800.00,
     'status': 'На витрине'},
]

# product_id — 1-based из PRODUCTS
# Правила: перед каждой повторной продажей товара должен быть «Возврат от покупателя»
SALES = [
    # ─── Август 2025 ──────────────────────────────────────────────────────
    {'sale_date': '2025-08-20', 'product_id': 5,  'sale_price': 3200.00, 'commission': 800.00,  'status': 'Оплачено'},            # Ботинки    → Продан
    {'sale_date': '2025-08-25', 'product_id': 9,  'sale_price': 2800.00, 'commission': 560.00,  'status': 'Оплачено'},            # Сумка      → Продан
    # ─── Сентябрь 2025 ────────────────────────────────────────────────────
    {'sale_date': '2025-09-05', 'product_id': 13, 'sale_price': 12500.00,'commission': 3125.00, 'status': 'Оплачено'},            # Часы       → Продан
    {'sale_date': '2025-09-12', 'product_id': 19, 'sale_price': 14500.00,'commission': 4350.00, 'status': 'Оплачено'},            # Фотоап.    → Продан
    {'sale_date': '2025-09-15', 'product_id': 16, 'sale_price': 8900.00, 'commission': 2225.00, 'status': 'Оплачено'},            # Сервиз     → Продан
    {'sale_date': '2025-09-22', 'product_id': 21, 'sale_price': 9800.00, 'commission': 2940.00, 'status': 'Оплачено'},            # Наушники   → Продан
    {'sale_date': '2025-09-28', 'product_id': 18, 'sale_price': 2200.00, 'commission': 440.00,  'status': 'Оплачено'},            # Статуэтка  → Продан
    # ─── Октябрь 2025 ─────────────────────────────────────────────────────
    {'sale_date': '2025-10-01', 'product_id': 5,  'sale_price': 3200.00, 'commission': 800.00,  'status': 'Возврат от покупателя'},# Ботинки  → На витрине
    {'sale_date': '2025-10-01', 'product_id': 9,  'sale_price': 2800.00, 'commission': 560.00,  'status': 'Возврат от покупателя'},# Сумка    → На витрине
    {'sale_date': '2025-10-03', 'product_id': 2,  'sale_price': 6800.00, 'commission': 1700.00, 'status': 'Оплачено'},            # Куртка     → Продан
    {'sale_date': '2025-10-08', 'product_id': 10, 'sale_price': 1500.00, 'commission': 300.00,  'status': 'Оплачено'},            # Шарф       → Продан
    {'sale_date': '2025-10-10', 'product_id': 7,  'sale_price': 2100.00, 'commission': 525.00,  'status': 'Оплачено'},            # Туфли      → Продан
    {'sale_date': '2025-10-12', 'product_id': 5,  'sale_price': 3500.00, 'commission': 875.00,  'status': 'Оплачено'},            # Ботинки    → Продан (повторно)
    {'sale_date': '2025-10-15', 'product_id': 9,  'sale_price': 3000.00, 'commission': 600.00,  'status': 'Оплачено'},            # Сумка      → Продан (повторно)
    {'sale_date': '2025-10-18', 'product_id': 23, 'sale_price': 4500.00, 'commission': 900.00,  'status': 'Оплачено'},            # Книга      → Продан
    {'sale_date': '2025-10-22', 'product_id': 12, 'sale_price': 1900.00, 'commission': 475.00,  'status': 'Оплачено'},            # Клатч      → Продан
    {'sale_date': '2025-10-25', 'product_id': 7,  'sale_price': 2100.00, 'commission': 525.00,  'status': 'Возврат от покупателя'},# Туфли   → На витрине → потом RET-001
    # ─── Ноябрь 2025 ──────────────────────────────────────────────────────
    {'sale_date': '2025-11-02', 'product_id': 6,  'sale_price': 5400.00, 'commission': 1350.00, 'status': 'Оплачено'},            # Сапоги     → Продан
    {'sale_date': '2025-11-05', 'product_id': 13, 'sale_price': 12500.00,'commission': 3125.00, 'status': 'Возврат от покупателя'},# Часы    → На витрине
    {'sale_date': '2025-11-08', 'product_id': 16, 'sale_price': 8900.00, 'commission': 2225.00, 'status': 'Возврат от покупателя'},# Сервиз  → На витрине
    {'sale_date': '2025-11-12', 'product_id': 21, 'sale_price': 9800.00, 'commission': 2940.00, 'status': 'Возврат от покупателя'},# Наушники→ На витрине
    {'sale_date': '2025-11-18', 'product_id': 20, 'sale_price': 11000.00,'commission': 3300.00, 'status': 'Оплачено'},            # Планшет    → Продан
    {'sale_date': '2025-11-22', 'product_id': 18, 'sale_price': 2200.00, 'commission': 440.00,  'status': 'Возврат от покупателя'},# Статуэтка→ На витрине
    {'sale_date': '2025-11-25', 'product_id': 19, 'sale_price': 14500.00,'commission': 4350.00, 'status': 'Возврат от покупателя'},# Фотоап. → На витрине
    {'sale_date': '2025-11-28', 'product_id': 20, 'sale_price': 11000.00,'commission': 3300.00, 'status': 'Возврат от покупателя'},# Планшет → На витрине
    # ─── Декабрь 2025 ─────────────────────────────────────────────────────
    {'sale_date': '2025-12-03', 'product_id': 13, 'sale_price': 13000.00,'commission': 3250.00, 'status': 'Оплачено'},            # Часы       → Продан
    {'sale_date': '2025-12-08', 'product_id': 16, 'sale_price': 9200.00, 'commission': 2300.00, 'status': 'Оплачено'},            # Сервиз     → Продан
    {'sale_date': '2025-12-12', 'product_id': 21, 'sale_price': 10000.00,'commission': 3000.00, 'status': 'Оплачено'},            # Наушники   → Продан
    {'sale_date': '2025-12-18', 'product_id': 18, 'sale_price': 2400.00, 'commission': 480.00,  'status': 'Оплачено'},            # Статуэтка  → Продан
    {'sale_date': '2025-12-22', 'product_id': 19, 'sale_price': 15000.00,'commission': 4500.00, 'status': 'Оплачено'},            # Фотоап.    → Продан
    # ─── Январь 2026 ──────────────────────────────────────────────────────
    {'sale_date': '2026-01-05', 'product_id': 2,  'sale_price': 6800.00, 'commission': 1700.00, 'status': 'Возврат от покупателя'},# Куртка  → На витрине
    {'sale_date': '2026-01-08', 'product_id': 10, 'sale_price': 1500.00, 'commission': 300.00,  'status': 'Возврат от покупателя'},# Шарф    → На витрине
    {'sale_date': '2026-01-10', 'product_id': 13, 'sale_price': 13000.00,'commission': 3250.00, 'status': 'Возврат от покупателя'},# Часы    → На витрине
    {'sale_date': '2026-01-12', 'product_id': 23, 'sale_price': 4500.00, 'commission': 900.00,  'status': 'Возврат от покупателя'},# Книга   → На витрине
    {'sale_date': '2026-01-15', 'product_id': 12, 'sale_price': 1900.00, 'commission': 475.00,  'status': 'Возврат от покупателя'},# Клатч   → На витрине
    # ─── Февраль 2026 ─────────────────────────────────────────────────────
    {'sale_date': '2026-02-03', 'product_id': 2,  'sale_price': 7000.00, 'commission': 1750.00, 'status': 'Оплачено'},            # Куртка     → Продан
    {'sale_date': '2026-02-07', 'product_id': 10, 'sale_price': 1600.00, 'commission': 320.00,  'status': 'Оплачено'},            # Шарф       → Продан
    {'sale_date': '2026-02-10', 'product_id': 13, 'sale_price': 13500.00,'commission': 3375.00, 'status': 'Оплачено'},            # Часы       → Продан
    {'sale_date': '2026-02-14', 'product_id': 23, 'sale_price': 4800.00, 'commission': 960.00,  'status': 'Оплачено'},            # Книга      → Продан
    {'sale_date': '2026-02-18', 'product_id': 12, 'sale_price': 2000.00, 'commission': 500.00,  'status': 'Оплачено'},            # Клатч      → Продан
    # ─── Март 2026 ────────────────────────────────────────────────────────
    {'sale_date': '2026-03-05', 'product_id': 16, 'sale_price': 9200.00, 'commission': 2300.00, 'status': 'Возврат от покупателя'},# Сервиз  → На витрине
    {'sale_date': '2026-03-08', 'product_id': 21, 'sale_price': 10000.00,'commission': 3000.00, 'status': 'Возврат от покупателя'},# Наушники→ На витрине
    {'sale_date': '2026-03-12', 'product_id': 18, 'sale_price': 2400.00, 'commission': 480.00,  'status': 'Возврат от покупателя'},# Статуэтка→ На витрине
    {'sale_date': '2026-03-15', 'product_id': 19, 'sale_price': 15000.00,'commission': 4500.00, 'status': 'Возврат от покупателя'},# Фотоап. → На витрине
    # ─── Апрель 2026 ──────────────────────────────────────────────────────
    {'sale_date': '2026-04-02', 'product_id': 16, 'sale_price': 9500.00, 'commission': 2375.00, 'status': 'Оплачено'},            # Сервиз     → Продан
    {'sale_date': '2026-04-05', 'product_id': 6,  'sale_price': 5400.00, 'commission': 1350.00, 'status': 'Возврат от покупателя'},# Сапоги  → На витрине
    {'sale_date': '2026-04-08', 'product_id': 21, 'sale_price': 10500.00,'commission': 3150.00, 'status': 'Оплачено'},            # Наушники   → Продан
    {'sale_date': '2026-04-12', 'product_id': 18, 'sale_price': 2500.00, 'commission': 500.00,  'status': 'Оплачено'},            # Статуэтка  → Продан
    {'sale_date': '2026-04-18', 'product_id': 19, 'sale_price': 15500.00,'commission': 4650.00, 'status': 'Оплачено'},            # Фотоап.    → Продан
    {'sale_date': '2026-04-22', 'product_id': 2,  'sale_price': 7000.00, 'commission': 1750.00, 'status': 'Возврат от покупателя'},# Куртка  → На витрине
    {'sale_date': '2026-04-25', 'product_id': 13, 'sale_price': 13500.00,'commission': 3375.00, 'status': 'Возврат от покупателя'},# Часы    → На витрине
    # ─── Май 2026 (текущий месяц) ─────────────────────────────────────────
    {'sale_date': '2026-05-02', 'product_id': 6,  'sale_price': 5800.00, 'commission': 1450.00, 'status': 'Оплачено'},            # Сапоги     → Продан
    {'sale_date': '2026-05-07', 'product_id': 2,  'sale_price': 7200.00, 'commission': 1800.00, 'status': 'Оплачено'},            # Куртка     → Продан
    {'sale_date': '2026-05-10', 'product_id': 13, 'sale_price': 14000.00,'commission': 3500.00, 'status': 'Ожидает оплаты'},      # Часы       → Продан (ожидает)
    {'sale_date': '2026-05-14', 'product_id': 20, 'sale_price': 11500.00,'commission': 3450.00, 'status': 'Оплачено'},            # Планшет    → Продан
]

CONSIGNOR_RETURNS = [
    {'number': 'RET-001', 'date': '2025-12-15', 'consignor_id': 2,
     'description': 'Возврат нереализованной обуви'},
]

# product_id туфель (7) возвращён
RETURNED_PRODUCT_IDS = [7]

SALES_REPORTS = [
    {'number': 'REP-001', 'date': '2025-09-30',
     'date_from': '2025-09-01', 'date_to': '2025-09-30',
     'description': 'Отчёт за сентябрь 2025'},
    {'number': 'REP-002', 'date': '2025-10-31',
     'date_from': '2025-10-01', 'date_to': '2025-10-31',
     'description': 'Отчёт за октябрь 2025'},
    {'number': 'REP-003', 'date': '2025-11-30',
     'date_from': '2025-11-01', 'date_to': '2025-11-30',
     'description': 'Отчёт за ноябрь 2025'},
]


def insert_test_data():
    for d in CONSIGNORS:
        db.session.add(Consignor(**d))
    db.session.flush()

    for d in CATEGORIES:
        db.session.add(Category(**d))
    db.session.flush()

    for d in CONSIGNOR_REPORTS:
        db.session.add(ConsignorReport(
            number=d['number'],
            date=_d(d['date']),
            description=d['description'],
            consignor_id=d['consignor_id'],
            commission_pct=d['commission_pct'],
            commission_min=d['commission_min'],
        ))
    db.session.flush()

    for i, d in enumerate(PRODUCTS, start=1):
        db.session.add(Product(
            product_name=d['product_name'],
            description=d['description'],
            delivery_date=_d(d['delivery_date']),
            expiry_date=_d(d['expiry_date']),
            price=d['price'],
            status=d['status'],
            category_id=d['category_id'],
            consignor_report_id=d['consignor_report_id'],
        ))
    db.session.flush()

    for d in SALES:
        db.session.add(Sale(
            sale_date=_d(d['sale_date']),
            sale_price=d['sale_price'],
            commission=d['commission'],
            status=d['status'],
            product_id=d['product_id'],
        ))
    db.session.flush()

    # Акт возврата
    for d in CONSIGNOR_RETURNS:
        ret = ConsignorReturn(
            number=d['number'],
            date=_d(d['date']),
            consignor_id=d['consignor_id'],
            description=d['description'],
        )
        db.session.add(ret)
    db.session.flush()

    # Привязать возвращённые товары к акту возврата
    from models import ConsignorReturn as CR
    act = CR.query.filter_by(number='RET-001').first()
    for pid in RETURNED_PRODUCT_IDS:
        from models import Product as P
        p = P.query.get(pid)
        if p:
            p.consignor_return_id = act.id
    db.session.flush()

    # Отчёты по продажам (snapshot только оплаченных)
    for d in SALES_REPORTS:
        from decimal import Decimal
        period_sales = Sale.query.join(Product).filter(
            Sale.status == 'Оплачено',
            Sale.sale_date >= _d(d['date_from']),
            Sale.sale_date <= _d(d['date_to']),
        ).all()

        total_rev = sum(s.sale_price for s in period_sales)
        total_com = sum(s.commission for s in period_sales)
        report = SalesReport(
            number=d['number'],
            date=_d(d['date']),
            date_from=_d(d['date_from']),
            date_to=_d(d['date_to']),
            description=d['description'],
            total_revenue=total_rev,
            total_commission=total_com,
            total_payable=total_rev - total_com,
        )
        db.session.add(report)
        db.session.flush()

        for sale in period_sales:
            product = sale.product
            consignor = product.consignor_report.consignor
            db.session.add(SalesReportLine(
                report_id=report.id,
                sale_id=sale.id,
                sale_date=sale.sale_date,
                product_name=product.product_name,
                category_name=product.category.name if product.category else None,
                consignor_name=f'{consignor.last_name} {consignor.first_name}',
                sale_price=sale.sale_price,
                commission=sale.commission,
                payable=sale.sale_price - sale.commission,
            ))

    db.session.commit()
