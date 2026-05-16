from dotenv import load_dotenv

load_dotenv()

import os
from flask import Flask, render_template, redirect, url_for, request, flash
from werkzeug.utils import secure_filename
from models import db, Consignor, ConsignorReport, ConsignorReturn, SalesReport, SalesReportLine, Sale, Product, ProductImage, Category
from config import Config

from datetime import datetime
from decimal import Decimal

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


def _allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def _save_images(files) -> list[str]:
    """Сохраняет список загруженных файлов, возвращает имена сохранённых файлов."""
    saved = []
    for file in files:
        if not file or not file.filename:
            continue
        if not _allowed_file(file.filename):
            continue
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        saved.append(filename)
    return saved


# Для тестирования
def insert_test_data():
    consignors = [
        {'id': 1, 'last_name': 'Соколов', 'first_name': 'Иван', 'middle_name': 'Алексеевич',
         'email': 'ivan.sokolov@example.com',
         'phone_number': '79001234567', 'passport_data': '4510 123456', 'INN': '123456789012'},
        {'id': 2, 'last_name': 'Морозова', 'first_name': 'Екатерина', 'middle_name': 'Дмитриевна',
         'email': 'ekaterina.morozova@example.com',
         'phone_number': '79111234568', 'passport_data': '4511 234567', 'INN': '234567890123'},
        {'id': 3, 'last_name': 'Волков', 'first_name': 'Дмитрий', 'middle_name': 'Отсутствует',
         'email': 'dmitry.volkov@example.com',
         'phone_number': '79221234569', 'passport_data': '4512 345678', 'INN': '345678901234'},
        {'id': 4, 'last_name': 'Зайцева', 'first_name': 'Анна', 'middle_name': 'Сергеевна',
         'email': 'anna.zaytseva@example.com',
         'phone_number': '79331234570', 'passport_data': '4513 456789', 'INN': '456789012345'},
        {'id': 5, 'last_name': 'Кузнецов', 'first_name': 'Михаил', 'middle_name': 'Петрович',
         'email': 'mikhail.kuznetsov@example.com',
         'phone_number': '79441234571', 'passport_data': '4514 567890', 'INN': '567890123456'},
    ]

    consignor_reports = [
        {'id': 1, 'number': 'ACT-001', 'date': '2023-09-15',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 2,
         'commission_pct': 20, 'commission_min': 100},
        {'id': 2, 'number': 'ACT-002', 'date': '2023-09-20',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 3,
         'commission_pct': 25, 'commission_min': 150},
        {'id': 3, 'number': 'ACT-003', 'date': '2023-10-01',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 4,
         'commission_pct': 20, 'commission_min': 100},
        {'id': 4, 'number': 'ACT-004', 'date': '2023-09-25',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 5,
         'commission_pct': 30, 'commission_min': 200},
        {'id': 5, 'number': 'ACT-005', 'date': '2023-10-05',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 1,
         'commission_pct': 20, 'commission_min': 100},
    ]

    sales_reports = [
        {'id': 1, 'number': 'REP-001', 'date': '2023-10-31',
         'date_from': '2023-10-01', 'date_to': '2023-10-31',
         'description': 'Отчёт о продажах за октябрь 2023'},
        {'id': 2, 'number': 'REP-002', 'date': '2023-11-30',
         'date_from': '2023-11-01', 'date_to': '2023-11-30',
         'description': 'Отчёт о продажах за ноябрь 2023'},
    ]

    products = [
        {'id': 1, 'product_name': 'Пальто зимнее', 'description': 'Женское, размер 48, цвет чёрный',
         'delivery_date': '2023-09-15', 'expiry_date': '2024-03-15', 'price': 4500.00,
         'consignor_report_id': 1, 'status': 'На витрине'},
        {'id': 2, 'product_name': 'Ботинки кожаные', 'description': 'Мужские, размер 42, коричневые',
         'delivery_date': '2023-09-20', 'expiry_date': '2024-02-20', 'price': 3200.00,
         'consignor_report_id': 2, 'status': 'Продан'},
        {'id': 3, 'product_name': 'Сумка женская', 'description': 'Кожаная, среднего размера, бежевая',
         'delivery_date': '2023-10-01', 'expiry_date': '2024-04-01', 'price': 2800.50,
         'consignor_report_id': 3, 'status': 'На витрине'},
        {'id': 4, 'product_name': 'Часы наручные', 'description': 'Механические, мужские, сталь',
         'delivery_date': '2023-09-25', 'expiry_date': '2024-01-25', 'price': 12500.00,
         'consignor_report_id': 4, 'status': 'Продан'},
        {'id': 5, 'product_name': 'Сервиз чайный', 'description': 'Фарфор, 12 персон, позолота',
         'delivery_date': '2023-10-05', 'expiry_date': '2024-05-05', 'price': 8900.00,
         'consignor_report_id': 5, 'status': 'Продан'},
        {'id': 6, 'product_name': 'Шарф пуховый', 'description': 'Оренбургский, белый, ажурный',
         'delivery_date': '2023-10-10', 'expiry_date': '2024-01-10', 'price': 1500.00,
         'consignor_report_id': 1, 'status': 'Продан'},
    ]

    sales = [
        {'id': 1, 'sale_date': '2023-10-01', 'sale_price': 1500.00,
         'commission': 150.00, 'status': 'Оплачено', 'product_id': 2},
        {'id': 2, 'sale_date': '2023-10-02', 'sale_price': 3200.50,
         'commission': 320.05, 'status': 'Ожидает оплаты', 'product_id': 3},
        {'id': 3, 'sale_date': '2023-10-03', 'sale_price': 780.00,
         'commission': 200.00, 'status': 'Оплачено', 'product_id': 4},
        {'id': 4, 'sale_date': '2023-10-04', 'sale_price': 2100.00,
         'commission': 420.00, 'status': 'Возврат от покупателя', 'product_id': 5},
        {'id': 5, 'sale_date': '2023-10-05', 'sale_price': 540.75,
         'commission': 108.15, 'status': 'Оплачено', 'product_id': 6},
        # Повторная продажа товара 5 после возврата
        {'id': 6, 'sale_date': '2023-10-10', 'sale_price': 2200.00,
         'commission': 440.00, 'status': 'Оплачено', 'product_id': 5},
    ]

    for consignor_data in consignors:
        consignor = Consignor(
            first_name=consignor_data['first_name'],
            last_name=consignor_data['last_name'],
            middle_name=consignor_data['middle_name'],
            email=consignor_data['email'],
            phone_number=consignor_data['phone_number'],
            passport_data=consignor_data['passport_data'],
            inn=consignor_data['INN'],
        )
        db.session.add(consignor)
    db.session.flush()

    for cr_data in consignor_reports:
        cr = ConsignorReport(
            number=cr_data['number'],
            date=datetime.strptime(cr_data['date'], '%Y-%m-%d').date(),
            description=cr_data['description'],
            consignor_id=cr_data['consignor_id'],
            commission_pct=cr_data['commission_pct'],
            commission_min=cr_data['commission_min'],
        )
        db.session.add(cr)
    db.session.flush()

    for sr_data in sales_reports:
        sr = SalesReport(
            number=sr_data['number'],
            date=datetime.strptime(sr_data['date'], '%Y-%m-%d').date(),
            date_from=datetime.strptime(sr_data['date_from'], '%Y-%m-%d').date(),
            date_to=datetime.strptime(sr_data['date_to'], '%Y-%m-%d').date(),
            description=sr_data['description'],
        )
        db.session.add(sr)
    db.session.flush()

    for product_data in products:
        product = Product(
            product_name=product_data['product_name'],
            description=product_data['description'],
            delivery_date=datetime.strptime(product_data['delivery_date'], '%Y-%m-%d').date(),
            expiry_date=datetime.strptime(product_data['expiry_date'], '%Y-%m-%d').date(),
            price=product_data['price'],
            consignor_report_id=product_data['consignor_report_id'],
            status=product_data['status'],
        )
        db.session.add(product)
    db.session.flush()

    for sale_data in sales:
        sale = Sale(
            sale_date=datetime.strptime(sale_data['sale_date'], '%Y-%m-%d').date(),
            sale_price=sale_data['sale_price'],
            commission=sale_data['commission'],
            status=sale_data['status'],
            product_id=sale_data['product_id'],
        )
        db.session.add(sale)

    db.session.commit()


def init_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        insert_test_data()


@app.route('/')
def index():
    return render_template('index.html')


# ==============================
#           КОМИТЕНТ
# ==============================


@app.route('/consignors')
def consignors_list():
    consignors = Consignor.query.all()

    return render_template('consignors/consignors_list.html', consignors=consignors)


@app.route('/add_consignor', methods=['GET', 'POST'])
def add_consignor():
    if request.method == 'POST':
        last_name = request.form['last_name']
        first_name = request.form['first_name']
        middle_name = request.form['middle_name'] or 'Отсутствует'
        email = request.form['email']
        phone_number = request.form['phone_number']
        passport_data = request.form['passport_data']
        inn = request.form['INN']

        new_consignor = Consignor(
            last_name=last_name,
            first_name=first_name,
            middle_name=middle_name,
            email=email,
            phone_number=phone_number,
            passport_data=passport_data,
            inn=inn
        )
        db.session.add(new_consignor)
        db.session.commit()
        flash('Комитент успешно добавлен!', 'success')

        return redirect(url_for('consignors_list'))

    return render_template('consignors/consignor_form.html', consignor=None)


@app.route('/consignors/<consignor_id>')
def consignor_detail(consignor_id):
    consignor = Consignor.query.get_or_404(consignor_id)

    return render_template('consignors/consignor_detail.html', consignor=consignor)


@app.route('/edit_consignor/<int:consignor_id>', methods=['GET', 'POST'])
def edit_consignor(consignor_id):
    consignor = Consignor.query.get_or_404(consignor_id)

    if request.method == 'POST':
        consignor.last_name = request.form['last_name']
        consignor.first_name = request.form['first_name']
        consignor.middle_name = request.form['middle_name'] or 'Отсутствует'
        consignor.email = request.form['email']
        consignor.phone_number = request.form['phone_number']
        consignor.passport_data = request.form['passport_data']
        consignor.inn = request.form['INN']
        db.session.commit()
        flash('Данные обновлены!', 'success')

        return redirect(url_for('consignors_list'))

    return render_template('consignors/consignor_form.html', consignor=consignor)


@app.route('/delete_consignor/<int:consignor_id>', methods=['POST'])
def delete_consignor(consignor_id):
    consignor = Consignor.query.get_or_404(consignor_id)

    if consignor.consignor_reports:
        flash('Комитента нельзя удалить, так как есть связанный с ним акт приёма.', 'error')
        return redirect(url_for('consignors_list'))
    db.session.delete(consignor)
    db.session.commit()
    flash('Комитент успешно удалён!', 'success')

    return redirect(url_for('consignors_list'))


# ==============================
#       АКТ ПРИЁМА (КОМИТЕНТ)
# ==============================


@app.route('/consignor_reports')
def consignor_reports_list():
    consignor_reports = ConsignorReport.query.all()
    consignors = Consignor.query.all()
    consignors_dict = {
        c.id: f"{c.last_name} {c.first_name} {c.middle_name or ''}".strip()
        for c in consignors
    }

    return render_template('consignor_reports/consignor_reports_list.html',
                           consignor_reports=consignor_reports, consignors=consignors_dict)


@app.route('/add_consignor_report', methods=['GET', 'POST'])
def add_consignor_report():
    consignors = Consignor.query.all()

    if request.method == 'POST':
        number = request.form['number']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        description = request.form['description']
        consignor_id = request.form['consignor_id']
        commission_pct = Decimal(request.form['commission_pct'])
        commission_min = Decimal(request.form['commission_min'])

        new_report = ConsignorReport(
            number=number,
            date=date,
            description=description,
            consignor_id=consignor_id,
            commission_pct=commission_pct,
            commission_min=commission_min,
        )
        db.session.add(new_report)
        db.session.commit()
        flash('Акт приёма успешно добавлен!', 'success')

        return redirect(url_for('consignor_reports_list'))

    return render_template('consignor_reports/consignor_report_form.html',
                           consignor_report=None, consignors=consignors)


@app.route('/consignor_report/<int:consignor_report_id>')
def consignor_report_detail(consignor_report_id):
    consignor_report = ConsignorReport.query.get_or_404(consignor_report_id)

    return render_template('consignor_reports/consignor_report_detail.html',
                           consignor_report=consignor_report,
                           consignor=consignor_report.consignor)


@app.route('/edit_consignor_report/<int:consignor_report_id>', methods=['GET', 'POST'])
def edit_consignor_report(consignor_report_id):
    consignor_report = ConsignorReport.query.get_or_404(consignor_report_id)
    consignors = Consignor.query.all()

    if request.method == 'POST':
        consignor_report.number = request.form['number']
        consignor_report.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        consignor_report.description = request.form['description']
        consignor_report.consignor_id = request.form['consignor_id']
        consignor_report.commission_pct = Decimal(request.form['commission_pct'])
        consignor_report.commission_min = Decimal(request.form['commission_min'])
        db.session.commit()
        flash('Данные обновлены!', 'success')

        return redirect(url_for('consignor_reports_list'))

    return render_template('consignor_reports/consignor_report_form.html',
                           consignor_report=consignor_report, consignors=consignors)


@app.route('/delete_consignor_report/<int:consignor_report_id>', methods=['POST'])
def delete_consignor_report(consignor_report_id):
    consignor_report = ConsignorReport.query.get_or_404(consignor_report_id)

    if consignor_report.products:
        flash('Акт приёма нельзя удалить, так как есть связанный с ним товар.', 'error')
        return redirect(url_for('consignor_reports_list'))
    db.session.delete(consignor_report)
    db.session.commit()
    flash('Акт приёма успешно удалён!', 'success')

    return redirect(url_for('consignor_reports_list'))


# ==============================
#       ОТЧЁТ ПО ПРОДАЖАМ
# ==============================


@app.route('/sales_reports')
def sales_reports_list():
    sales_reports = SalesReport.query.order_by(SalesReport.date.desc()).all()
    return render_template('sales_reports/sales_reports_list.html', sales_reports=sales_reports)


@app.route('/add_sales_report', methods=['GET', 'POST'])
def add_sales_report():
    if request.method == 'POST':
        number = request.form['number']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        date_from = datetime.strptime(request.form['date_from'], '%Y-%m-%d').date()
        date_to = datetime.strptime(request.form['date_to'], '%Y-%m-%d').date()
        description = request.form.get('description', '').strip() or None

        # Собираем все оплаченные продажи за период
        sales = Sale.query.join(Product).filter(
            Sale.status == 'Оплачено',
            Sale.sale_date >= date_from,
            Sale.sale_date <= date_to,
        ).all()

        total_revenue = sum(s.sale_price for s in sales)
        total_commission = sum(s.commission for s in sales)
        total_payable = total_revenue - total_commission

        report = SalesReport(
            number=number,
            date=date,
            date_from=date_from,
            date_to=date_to,
            description=description,
            total_revenue=total_revenue,
            total_commission=total_commission,
            total_payable=total_payable,
        )
        db.session.add(report)
        db.session.flush()

        for sale in sales:
            product = sale.product
            consignor = product.consignor_report.consignor
            line = SalesReportLine(
                report_id=report.id,
                sale_id=sale.id,
                sale_date=sale.sale_date,
                product_name=product.product_name,
                category_name=product.category.name if product.category else None,
                consignor_name=f'{consignor.last_name} {consignor.first_name}',
                sale_price=sale.sale_price,
                commission=sale.commission,
                payable=sale.sale_price - sale.commission,
            )
            db.session.add(line)

        db.session.commit()
        flash('Отчёт сформирован!', 'success')
        return redirect(url_for('sales_report_detail', sales_report_id=report.id))

    return render_template('sales_reports/sales_report_form.html', sales_report=None)


@app.route('/sales_report/<int:sales_report_id>')
def sales_report_detail(sales_report_id):
    report = SalesReport.query.get_or_404(sales_report_id)
    # Агрегация по категориям для графика
    category_totals = {}
    for line in report.lines:
        cat = line.category_name or 'Без категории'
        category_totals[cat] = category_totals.get(cat, Decimal('0')) + line.sale_price
    return render_template('sales_reports/sales_report_detail.html',
                           report=report, category_totals=category_totals)


@app.route('/edit_sales_report/<int:sales_report_id>', methods=['GET', 'POST'])
def edit_sales_report(sales_report_id):
    report = SalesReport.query.get_or_404(sales_report_id)
    if request.method == 'POST':
        report.number = request.form['number']
        report.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        report.description = request.form.get('description', '').strip() or None
        db.session.commit()
        flash('Реквизиты отчёта обновлены!', 'success')
        return redirect(url_for('sales_report_detail', sales_report_id=report.id))
    return render_template('sales_reports/sales_report_form.html', sales_report=report)


@app.route('/delete_sales_report/<int:sales_report_id>', methods=['POST'])
def delete_sales_report(sales_report_id):
    report = SalesReport.query.get_or_404(sales_report_id)
    db.session.delete(report)
    db.session.commit()
    flash('Отчёт удалён.', 'success')
    return redirect(url_for('sales_reports_list'))


# ==============================
#           ПРОДАЖА
# ==============================


@app.route('/sales')
def sales_list():
    sales = Sale.query.all()

    return render_template('sales/sales_list.html', sales=sales)


def _update_product_status(product: Product) -> None:
    """Обновляет статус товара на основе последней продажи."""
    if not product.sales:
        product.status = 'На витрине'
        return
    last_sale = sorted(product.sales, key=lambda s: s.sale_date)[-1]
    if last_sale.status in ('Ожидает оплаты', 'Оплачено'):
        product.status = 'Продан'
    else:
        product.status = 'На витрине'


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    products = Product.query.all()
    preset_product_id = request.args.get('product_id', type=int)
    preset_product = Product.query.get(preset_product_id) if preset_product_id else None

    if request.method == 'POST':
        sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%d').date()
        sale_price = Decimal(request.form['sale_price'])
        commission = Decimal(request.form['commission'])
        status = request.form['status']
        product_id = int(request.form['product_id'])
        product = Product.query.get_or_404(product_id)

        if product.status == 'Возвращён комитенту':
            flash('Нельзя оформить продажу: товар возвращён комитенту.', 'danger')
            return redirect(url_for('product_detail', product_id=product_id))

        if product.status == 'Продан' and status in ('Ожидает оплаты', 'Оплачено'):
            flash('Нельзя оформить продажу: товар уже продан. Сначала оформите возврат от покупателя.', 'danger')
            return redirect(url_for('product_detail', product_id=product_id))

        new_sale = Sale(
            sale_date=sale_date,
            sale_price=sale_price,
            commission=commission,
            status=status,
            product_id=product_id
        )
        db.session.add(new_sale)
        db.session.flush()
        _update_product_status(new_sale.product)
        db.session.commit()
        flash('Продажа успешно добавлена!', 'success')

        if preset_product_id:
            return redirect(url_for('product_detail', product_id=product_id))
        return redirect(url_for('sales_list'))

    return render_template('sales/sale_form.html', sale=None,
                           products=products, preset_product=preset_product)


@app.route('/sale/<int:sale_id>')
def sale_detail(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    return render_template('sales/sale_detail.html', sale=sale)


@app.route('/edit_sale/<int:sale_id>', methods=['GET', 'POST'])
def edit_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    products = Product.query.all()

    if request.method == 'POST':
        sale.sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%d').date()
        sale.sale_price = Decimal(request.form['sale_price'])
        sale.commission = Decimal(request.form['commission'])
        sale.status = request.form['status']
        sale.product_id = int(request.form['product_id'])
        db.session.flush()
        _update_product_status(sale.product)
        db.session.commit()
        flash('Данные обновлены!', 'success')

        return redirect(url_for('sales_list'))

    return render_template('sales/sale_form.html', sale=sale,
                           products=products, preset_product=None)


@app.route('/delete_sale/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    product = sale.product
    db.session.delete(sale)
    db.session.flush()
    _update_product_status(product)
    db.session.commit()
    flash('Продажа успешно удалена!', 'success')

    return redirect(url_for('sales_list'))


# ==============================
#         КАТЕГОРИИ
# ==============================


@app.route('/categories')
def categories_list():
    categories = Category.query.order_by(Category.name).all()
    return render_template('categories/categories_list.html', categories=categories)


@app.route('/add_category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        name = request.form['name'].strip()
        description = request.form.get('description', '').strip() or None
        db.session.add(Category(name=name, description=description))
        db.session.commit()
        flash('Категория добавлена!', 'success')
        return redirect(url_for('categories_list'))
    return render_template('categories/category_form.html', category=None)


@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name = request.form['name'].strip()
        category.description = request.form.get('description', '').strip() or None
        db.session.commit()
        flash('Категория обновлена!', 'success')
        return redirect(url_for('categories_list'))
    return render_template('categories/category_form.html', category=category)


@app.route('/delete_category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    if category.products:
        flash('Нельзя удалить категорию: есть товары в этой категории.', 'danger')
        return redirect(url_for('categories_list'))
    db.session.delete(category)
    db.session.commit()
    flash('Категория удалена.', 'success')
    return redirect(url_for('categories_list'))


# ==============================
#           ТОВАР
# ==============================


@app.route('/products')
def products_list():
    products = Product.query.all()
    consignor_reports = ConsignorReport.query.all()
    consignor_reports_dict = {cr.id: cr.number for cr in consignor_reports}

    return render_template('products/products_list.html', products=products,
                           consignor_reports=consignor_reports_dict)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    consignor_reports = ConsignorReport.query.all()
    categories = Category.query.order_by(Category.name).all()
    preset_cr_id = request.args.get('consignor_report_id', type=int)
    preset_cr = ConsignorReport.query.get(preset_cr_id) if preset_cr_id else None

    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        price = request.form['price']
        consignor_report_id = request.form['consignor_report_id']
        category_id = request.form.get('category_id') or None
        image_filenames = _save_images(request.files.getlist('images'))

        new_product = Product(
            product_name=product_name,
            description=description,
            delivery_date=delivery_date,
            expiry_date=expiry_date,
            price=price,
            consignor_report_id=consignor_report_id,
            category_id=category_id,
        )
        db.session.add(new_product)
        db.session.flush()
        for fn in image_filenames:
            db.session.add(ProductImage(filename=fn, product_id=new_product.id))
        db.session.commit()
        flash('Товар успешно добавлен!', 'success')

        if preset_cr_id:
            return redirect(url_for('consignor_report_detail', consignor_report_id=consignor_report_id))
        return redirect(url_for('products_list'))

    return render_template('products/product_form.html',
                           consignor_reports=consignor_reports,
                           categories=categories,
                           preset_consignor_report=preset_cr)


@app.route('/products/<product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    return render_template('products/product_detail.html', product=product,
                           consignor_report=product.consignor_report)


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    consignor_reports = ConsignorReport.query.all()
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.description = request.form['description']
        product.delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date()
        product.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        product.price = request.form['price']
        product.consignor_report_id = request.form['consignor_report_id']
        product.category_id = request.form.get('category_id') or None

        # Удалить отмеченные фотографии
        ids_to_delete = request.form.getlist('delete_image_ids')
        for image_id in ids_to_delete:
            img = ProductImage.query.get(int(image_id))
            if img and img.product_id == product.id:
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
                if os.path.exists(img_path):
                    os.remove(img_path)
                db.session.delete(img)

        new_images = _save_images(request.files.getlist('images'))
        for fn in new_images:
            db.session.add(ProductImage(filename=fn, product_id=product.id))

        db.session.commit()
        flash('Данные обновлены!', 'success')

        return redirect(url_for('products_list'))

    return render_template('products/product_form.html', product=product,
                           consignor_reports=consignor_reports,
                           categories=categories)


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if product.sales:
        flash('Товар нельзя удалить, так как есть связанные с ним продажи.', 'error')
        return redirect(url_for('products_list'))

    for img in product.images:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], img.filename)
        if os.path.exists(img_path):
            os.remove(img_path)

    db.session.delete(product)
    db.session.commit()
    flash('Товар успешно удалён!', 'success')

    return redirect(url_for('products_list'))


@app.route('/delete_product_image/<int:image_id>', methods=['POST'])
def delete_product_image(image_id):
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id
    back = request.form.get('back', 'edit')
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    if os.path.exists(img_path):
        os.remove(img_path)
    db.session.delete(image)
    db.session.commit()
    flash('Фотография удалена.', 'success')
    if back == 'detail':
        return redirect(url_for('product_detail', product_id=product_id))
    return redirect(url_for('edit_product', product_id=product_id))


@app.route('/upload_product_images/<int:product_id>', methods=['POST'])
def upload_product_images(product_id):
    product = Product.query.get_or_404(product_id)
    saved = _save_images(request.files.getlist('images'))
    for fn in saved:
        db.session.add(ProductImage(filename=fn, product_id=product.id))
    db.session.commit()
    if saved:
        flash(f'Загружено фотографий: {len(saved)}.', 'success')
    return redirect(url_for('product_detail', product_id=product_id))


# ==============================
#       АКТЫ ВОЗВРАТА
# ==============================


@app.route('/consignor_returns')
def consignor_returns_list():
    returns = ConsignorReturn.query.order_by(ConsignorReturn.date.desc()).all()
    return render_template('consignor_returns/consignor_returns_list.html', returns=returns)


@app.route('/add_consignor_return', methods=['GET', 'POST'])
def add_consignor_return():
    consignors = Consignor.query.order_by(Consignor.last_name).all()

    if request.method == 'POST':
        number = request.form['number']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        description = request.form.get('description', '').strip() or None
        consignor_id = int(request.form['consignor_id'])

        new_return = ConsignorReturn(
            number=number,
            date=date,
            description=description,
            consignor_id=consignor_id,
        )
        db.session.add(new_return)
        db.session.commit()
        flash('Акт возврата создан!', 'success')
        return redirect(url_for('consignor_return_detail', return_id=new_return.id))

    return render_template('consignor_returns/consignor_return_form.html',
                           ret=None, consignors=consignors)


@app.route('/consignor_returns/<int:return_id>')
def consignor_return_detail(return_id):
    ret = ConsignorReturn.query.get_or_404(return_id)
    # Товары комитента, которые на витрине или уже возвращены этим актом
    available_products = Product.query.filter(
        Product.consignor_report.has(consignor_id=ret.consignor_id),
        Product.status.in_(['На витрине', 'Возвращён комитенту']),
    ).all()
    return render_template('consignor_returns/consignor_return_detail.html',
                           ret=ret, available_products=available_products)


@app.route('/edit_consignor_return/<int:return_id>', methods=['GET', 'POST'])
def edit_consignor_return(return_id):
    ret = ConsignorReturn.query.get_or_404(return_id)
    consignors = Consignor.query.order_by(Consignor.last_name).all()

    if request.method == 'POST':
        ret.number = request.form['number']
        ret.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        ret.description = request.form.get('description', '').strip() or None
        ret.consignor_id = int(request.form['consignor_id'])
        db.session.commit()
        flash('Акт возврата обновлён!', 'success')
        return redirect(url_for('consignor_return_detail', return_id=ret.id))

    return render_template('consignor_returns/consignor_return_form.html',
                           ret=ret, consignors=consignors)


@app.route('/delete_consignor_return/<int:return_id>', methods=['POST'])
def delete_consignor_return(return_id):
    ret = ConsignorReturn.query.get_or_404(return_id)
    # Освобождаем товары — они снова «на витрине»
    for product in ret.products:
        product.consignor_return_id = None
        product.status = 'На витрине'
    db.session.delete(ret)
    db.session.commit()
    flash('Акт возврата удалён.', 'success')
    return redirect(url_for('consignor_returns_list'))


@app.route('/add_product_to_return/<int:return_id>', methods=['POST'])
def add_product_to_return(return_id):
    ret = ConsignorReturn.query.get_or_404(return_id)
    product_id = int(request.form['product_id'])
    product = Product.query.get_or_404(product_id)
    product.consignor_return_id = ret.id
    product.status = 'Возвращён комитенту'
    db.session.commit()
    flash(f'Товар «{product.product_name}» добавлен в акт возврата.', 'success')
    return redirect(url_for('consignor_return_detail', return_id=return_id))


@app.route('/remove_product_from_return/<int:return_id>/<int:product_id>', methods=['POST'])
def remove_product_from_return(return_id, product_id):
    product = Product.query.get_or_404(product_id)
    product.consignor_return_id = None
    product.status = 'На витрине'
    db.session.commit()
    flash(f'Товар «{product.product_name}» убран из акта возврата.', 'success')
    return redirect(url_for('consignor_return_detail', return_id=return_id))


# ==============================
#          ДАШБОРД
# ==============================


@app.route('/dashboard')
def dashboard():
    from sqlalchemy import func
    from datetime import date, timedelta

    today = date.today()
    month_start = today.replace(day=1)
    # Предыдущий месяц
    prev_month_end = month_start - timedelta(days=1)
    prev_month_start = prev_month_end.replace(day=1)

    def sales_stats(date_from, date_to):
        rows = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.sale_price), 0),
            func.coalesce(func.sum(Sale.commission), 0),
        ).filter(
            Sale.status == 'Оплачено',
            Sale.sale_date >= date_from,
            Sale.sale_date <= date_to,
        ).one()
        return {'count': rows[0], 'revenue': rows[1], 'commission': rows[2],
                'payable': rows[1] - rows[2]}

    curr = sales_stats(month_start, today)
    prev = sales_stats(prev_month_start, prev_month_end)

    # Кол-во товаров по статусам
    product_counts = dict(
        db.session.query(Product.status, func.count(Product.id))
        .group_by(Product.status).all()
    )

    # Продажи по месяцам за последние 12 месяцев
    dialect = db.engine.dialect.name
    if dialect == 'sqlite':
        month_expr = func.strftime('%Y-%m', Sale.sale_date)
    else:
        month_expr = func.date_trunc('month', Sale.sale_date)

    monthly = db.session.query(
        month_expr.label('month'),
        func.sum(Sale.sale_price).label('revenue'),
        func.sum(Sale.commission).label('commission'),
    ).filter(
        Sale.status == 'Оплачено',
        Sale.sale_date >= today - timedelta(days=365),
    ).group_by(month_expr).order_by(month_expr).all()

    # Продажи по категориям за текущий месяц
    cat_expr = func.coalesce(Category.name, 'Без категории')
    by_category = db.session.query(
        cat_expr.label('cat'),
        func.sum(Sale.sale_price).label('revenue'),
    ).join(Product, Sale.product_id == Product.id
    ).outerjoin(Category, Product.category_id == Category.id
    ).filter(
        Sale.status == 'Оплачено',
        Sale.sale_date >= month_start,
        Sale.sale_date <= today,
    ).group_by(cat_expr).order_by(func.sum(Sale.sale_price).desc()).all()

    # Товары с истекающим сроком (ближайшие 30 дней)
    expiring = Product.query.filter(
        Product.status == 'На витрине',
        Product.expiry_date <= today + timedelta(days=30),
        Product.expiry_date >= today,
    ).order_by(Product.expiry_date).all()

    # Просроченные товары
    overdue = Product.query.filter(
        Product.status == 'На витрине',
        Product.expiry_date < today,
    ).order_by(Product.expiry_date).all()

    # Подготовка данных для графиков
    monthly_labels = [str(row.month)[:7] for row in monthly]
    monthly_revenue = [float(row.revenue) for row in monthly]
    monthly_commission = [float(row.commission) for row in monthly]

    cat_labels = [row.cat for row in by_category]
    cat_revenue = [float(row.revenue) for row in by_category]

    return render_template('dashboard.html',
                           curr=curr, prev=prev,
                           product_counts=product_counts,
                           monthly_labels=monthly_labels,
                           monthly_revenue=monthly_revenue,
                           monthly_commission=monthly_commission,
                           cat_labels=cat_labels,
                           cat_revenue=cat_revenue,
                           expiring=expiring,
                           overdue=overdue,
                           today=today)


if __name__ == "__main__":
    init_db()
    app.run()  # debug=True
