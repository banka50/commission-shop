from dotenv import load_dotenv

load_dotenv()

import os
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from werkzeug.utils import secure_filename
from models import db, Consignor, ConsignorReport, ConsignorReturn, SalesReport, SalesReportLine, Sale, Product, ProductImage, Category
from config import Config

from datetime import datetime
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


def _unique_error_message(err: IntegrityError) -> str:
    """Возвращает понятное сообщение при нарушении уникальности."""
    msg = str(err.orig).lower()
    field_labels = {
        'email': 'Email',
        'phone_number': 'Номер телефона',
        'passport_data': 'Паспортные данные',
        'inn': 'ИНН',
        'number': 'Номер',
        'name': 'Название',
    }
    for field, label in field_labels.items():
        if field in msg:
            return f'{label} уже занят — введите другое значение.'
    return 'Запись с такими данными уже существует.'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.context_processor
def inject_breadcrumbs():
    """Автоматически формирует хлебные крошки по текущему endpoint."""
    from flask import request as _req
    endpoint = _req.endpoint
    args = _req.view_args or {}
    crumbs = [{'label': 'Дашборд', 'url': url_for('dashboard')}]

    section_map = {
        'consignors_list':         ('Комитенты',           'consignors_list',         {}),
        'consignor_detail':        ('Комитенты',           'consignors_list',         {}),
        'add_consignor':           ('Комитенты',           'consignors_list',         {}),
        'edit_consignor':          ('Комитенты',           'consignors_list',         {}),
        'categories_list':         ('Категории',           'categories_list',         {}),
        'add_category':            ('Категории',           'categories_list',         {}),
        'edit_category':           ('Категории',           'categories_list',         {}),
        'products_list':           ('Товары',              'products_list',           {}),
        'product_detail':          ('Товары',              'products_list',           {}),
        'add_product':             ('Товары',              'products_list',           {}),
        'edit_product':            ('Товары',              'products_list',           {}),
        'sales_list':              ('Продажи',             'sales_list',              {}),
        'sale_detail':             ('Продажи',             'sales_list',              {}),
        'add_sale':                ('Продажи',             'sales_list',              {}),
        'edit_sale':               ('Продажи',             'sales_list',              {}),
        'consignor_reports_list':  ('Акты приёма',         'consignor_reports_list',  {}),
        'consignor_report_detail': ('Акты приёма',         'consignor_reports_list',  {}),
        'add_consignor_report':    ('Акты приёма',         'consignor_reports_list',  {}),
        'edit_consignor_report':   ('Акты приёма',         'consignor_reports_list',  {}),
        'consignor_returns_list':  ('Акты возврата',       'consignor_returns_list',  {}),
        'consignor_return_detail': ('Акты возврата',       'consignor_returns_list',  {}),
        'add_consignor_return':    ('Акты возврата',       'consignor_returns_list',  {}),
        'edit_consignor_return':   ('Акты возврата',       'consignor_returns_list',  {}),
        'sales_reports_list':      ('Отчёты по продажам', 'sales_reports_list',      {}),
        'sales_report_detail':     ('Отчёты по продажам', 'sales_reports_list',      {}),
        'add_sales_report':        ('Отчёты по продажам', 'sales_reports_list',      {}),
        'edit_sales_report':       ('Отчёты по продажам', 'sales_reports_list',      {}),
        'search':                  ('Поиск',              'search',                  {}),
    }

    if endpoint in section_map:
        section_label, section_endpoint, section_args = section_map[endpoint]
        is_section_root = (endpoint == section_endpoint)
        crumbs.append({
            'label': section_label,
            'url': None if is_section_root else url_for(section_endpoint, **section_args),
        })

        # Третий уровень — название конкретной записи
        detail_label = None
        if endpoint == 'consignor_detail':
            c = db.session.get(Consignor, args.get('consignor_id'))
            if c:
                detail_label = f'{c.last_name} {c.first_name}'
        elif endpoint in ('add_consignor', 'edit_consignor'):
            detail_label = 'Редактировать' if 'consignor_id' in args else 'Добавить'
        elif endpoint == 'product_detail':
            p = db.session.get(Product, args.get('product_id'))
            if p:
                detail_label = p.product_name
        elif endpoint in ('add_product', 'edit_product'):
            detail_label = 'Редактировать' if 'product_id' in args else 'Добавить'
        elif endpoint == 'sale_detail':
            detail_label = 'Продажа'
        elif endpoint in ('add_sale', 'edit_sale'):
            detail_label = 'Редактировать' if 'sale_id' in args else 'Добавить'
        elif endpoint in ('add_category', 'edit_category'):
            detail_label = 'Редактировать' if 'category_id' in args else 'Добавить'
        elif endpoint == 'consignor_report_detail':
            cr = db.session.get(ConsignorReport, args.get('consignor_report_id'))
            if cr:
                detail_label = f'Акт № {cr.number}'
        elif endpoint in ('add_consignor_report', 'edit_consignor_report'):
            detail_label = 'Редактировать' if 'consignor_report_id' in args else 'Добавить'
        elif endpoint in ('consignor_return_detail', 'edit_consignor_return'):
            ret = db.session.get(ConsignorReturn, args.get('return_id'))
            if ret:
                detail_label = f'Акт № {ret.number}'
        elif endpoint == 'add_consignor_return':
            detail_label = 'Новый акт'
        elif endpoint == 'sales_report_detail':
            sr = db.session.get(SalesReport, args.get('sales_report_id'))
            if sr:
                detail_label = f'Отчёт № {sr.number}'
        elif endpoint in ('add_sales_report', 'edit_sales_report'):
            detail_label = 'Редактировать' if 'sales_report_id' in args else 'Сформировать'

        if detail_label:
            crumbs.append({'label': detail_label, 'url': None})

    return {'breadcrumbs': crumbs}


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
    from test_data import insert_test_data as _insert
    _insert()



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
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('consignors/consignor_form.html', consignor=None)
        flash('Комитент успешно добавлен!', 'success')
        return redirect(url_for('consignors_list'))

    return render_template('consignors/consignor_form.html', consignor=None)


@app.route('/consignors/<consignor_id>')
def consignor_detail(consignor_id):
    consignor = Consignor.query.get_or_404(consignor_id)

    all_products = [p for cr in consignor.consignor_reports for p in cr.products]
    on_display = [p for p in all_products if p.status == 'На витрине']
    sold = [p for p in all_products if p.status == 'Продан']
    returned = [p for p in all_products if p.status == 'Возвращён комитенту']

    paid_sales = [
        s for p in all_products for s in p.sales if s.status == 'Оплачено'
    ]
    total_revenue = sum(s.sale_price for s in paid_sales)
    total_commission = sum(s.commission for s in paid_sales)
    total_payable = total_revenue - total_commission

    return render_template(
        'consignors/consignor_detail.html',
        consignor=consignor,
        on_display=on_display,
        sold=sold,
        returned=returned,
        total_revenue=total_revenue,
        total_commission=total_commission,
        total_payable=total_payable,
    )


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
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('consignors/consignor_form.html', consignor=consignor)
        flash('Данные обновлены!', 'success')
        if request.args.get('back') == 'detail':
            return redirect(url_for('consignor_detail', consignor_id=consignor_id))
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
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('consignor_reports/consignor_report_form.html',
                                   consignor_report=None, consignors=consignors)
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
        consignor_report.commission_pct = Decimal(request.form['commission_pct'])
        consignor_report.commission_min = Decimal(request.form['commission_min'])
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('consignor_reports/consignor_report_form.html',
                                   consignor_report=consignor_report, consignors=consignors)
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

        # Продажи и возвраты за период (возвраты хранятся с отрицательными суммами)
        sales = Sale.query.join(Product).filter(
            Sale.status.in_(['Оплачено', 'Возврат от покупателя']),
            Sale.sale_date >= datetime.combine(date_from, datetime.min.time()),
            Sale.sale_date <= datetime.combine(date_to, datetime.max.time()),
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

        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('sales_reports/sales_report_form.html', sales_report=None)
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
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()

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
    products = Product.query.filter(Product.status != 'Возвращён комитенту').order_by(Product.product_name).all()
    preset_product_id = request.args.get('product_id', type=int)
    preset_product = db.session.get(Product, preset_product_id) if preset_product_id else None

    # Последняя оплаченная продажа товара — для автоподстановки сторно
    last_paid_sale = None
    if preset_product and preset_product.status == 'Продан':
        last_paid_sale = (
            Sale.query
            .filter_by(product_id=preset_product.id, status='Оплачено')
            .order_by(Sale.sale_date.desc())
            .first()
        )

    if request.method == 'POST':
        sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%dT%H:%M:%S')
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

        # Для возврата суммы должны быть отрицательными
        if status == 'Возврат от покупателя':
            if sale_price > 0:
                sale_price = -sale_price
            if commission > 0:
                commission = -commission

            # Проверяем совпадение суммы возврата с исходной продажей
            orig_sale = (
                Sale.query
                .filter_by(product_id=product_id, status='Оплачено')
                .order_by(Sale.sale_date.desc())
                .first()
            )
            if orig_sale:
                if abs(sale_price) != abs(orig_sale.sale_price):
                    flash(
                        f'Сумма возврата ({abs(sale_price)} ₽) должна совпадать '
                        f'с суммой исходной продажи ({abs(orig_sale.sale_price)} ₽).',
                        'danger'
                    )
                    return redirect(request.url)
                max_commission_refund = abs(orig_sale.commission)
                if commission < -max_commission_refund or commission > 0:
                    flash(
                        f'Возврат комиссии должен быть от 0 до {max_commission_refund} ₽.',
                        'danger'
                    )
                    return redirect(request.url)

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
                           products=products, preset_product=preset_product,
                           last_paid_sale=last_paid_sale,
                           now=datetime.now())


@app.route('/sale/<int:sale_id>')
def sale_detail(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    return render_template('sales/sale_detail.html', sale=sale)


@app.route('/edit_sale/<int:sale_id>', methods=['GET', 'POST'])
def edit_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)
    products = Product.query.all()

    if request.method == 'POST':
        sale.sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%dT%H:%M:%S')
        sale.sale_price = Decimal(request.form['sale_price'])
        sale.commission = Decimal(request.form['commission'])
        sale.status = request.form['status']
        sale.product_id = int(request.form['product_id'])
        db.session.flush()
        _update_product_status(sale.product)
        db.session.commit()
        flash('Данные обновлены!', 'success')

        back = request.args.get('back', '')
        if back == 'product' and sale.product:
            return redirect(url_for('product_detail', product_id=sale.product_id))
        if back == 'products_list':
            return redirect(url_for('products_list'))
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
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('categories/category_form.html', category=None)
        flash('Категория добавлена!', 'success')
        return redirect(url_for('categories_list'))
    return render_template('categories/category_form.html', category=None)


@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        category.name = request.form['name'].strip()
        category.description = request.form.get('description', '').strip() or None
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('categories/category_form.html', category=category)
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


@app.route('/api/product/<int:product_id>', methods=['PATCH'])
def api_patch_product(product_id):
    """Inline-редактирование полей товара (price, category_id)."""
    product = Product.query.get_or_404(product_id)
    data = request.get_json(force=True)
    field = data.get('field')
    value = data.get('value')

    allowed_fields = {'price', 'category_id'}
    if field not in allowed_fields:
        return jsonify(error='Поле не допустимо для редактирования.'), 400

    if field == 'price':
        try:
            price = Decimal(str(value))
            if price <= 0:
                return jsonify(error='Цена должна быть больше нуля.'), 400
        except Exception:
            return jsonify(error='Некорректное значение цены.'), 400
        product.price = price

    elif field == 'category_id':
        if value == '' or value is None:
            product.category_id = None
        else:
            cat = db.session.get(Category, int(value))
            if not cat:
                return jsonify(error='Категория не найдена.'), 404
            product.category_id = cat.id

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify(error='Ошибка при сохранении.'), 500

    return jsonify(
        ok=True,
        display_price=str(product.price),
        display_category=product.category.name if product.category else 'Без категории',
    )


@app.route('/products')
def products_list():
    products = Product.query.all()
    consignor_reports = ConsignorReport.query.all()
    consignor_reports_dict = {
        cr.id: f'{cr.consignor.last_name} {cr.consignor.first_name} ({cr.number})'
        for cr in consignor_reports
    }
    categories = Category.query.order_by(Category.name).all()
    from datetime import date as date_type
    today = date_type.today()

    return render_template('products/products_list.html', products=products,
                           consignor_reports=consignor_reports_dict,
                           categories=categories,
                           today=today)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    consignor_reports = ConsignorReport.query.all()
    categories = Category.query.order_by(Category.name).all()
    preset_cr_id = request.args.get('consignor_report_id', type=int)
    preset_cr = db.session.get(ConsignorReport, preset_cr_id) if preset_cr_id else None

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
            img = db.session.get(ProductImage, int(image_id))
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

        if request.args.get('back') == 'detail':
            return redirect(url_for('product_detail', product_id=product_id))
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
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            return render_template('consignor_returns/consignor_return_form.html',
                                   ret=None, consignors=consignors)
        flash('Акт возврата создан!', 'success')
        return redirect(url_for('edit_consignor_return', return_id=new_return.id))

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
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            flash(_unique_error_message(e), 'danger')
            available_products = Product.query.filter(
                Product.consignor_report.has(consignor_id=ret.consignor_id),
                Product.status.in_(['На витрине', 'Возвращён комитенту']),
            ).all()
            return render_template('consignor_returns/consignor_return_form.html',
                                   ret=ret, consignors=consignors,
                                   available_products=available_products)
        flash('Акт возврата обновлён!', 'success')
        if request.args.get('back') == 'detail':
            return redirect(url_for('consignor_return_detail', return_id=ret.id))
        return redirect(url_for('edit_consignor_return', return_id=ret.id))

    available_products = Product.query.filter(
        Product.consignor_report.has(consignor_id=ret.consignor_id),
        Product.status.in_(['На витрине', 'Возвращён комитенту']),
    ).all()
    return render_template('consignor_returns/consignor_return_form.html',
                           ret=ret, consignors=consignors,
                           available_products=available_products)


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
    return redirect(url_for('edit_consignor_return', return_id=return_id))


@app.route('/remove_product_from_return/<int:return_id>/<int:product_id>', methods=['POST'])
def remove_product_from_return(return_id, product_id):
    product = Product.query.get_or_404(product_id)
    product.consignor_return_id = None
    product.status = 'На витрине'
    db.session.commit()
    flash(f'Товар «{product.product_name}» убран из акта возврата.', 'success')
    return redirect(url_for('edit_consignor_return', return_id=return_id))


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
            Sale.status.in_(['Оплачено', 'Возврат от покупателя']),
            Sale.sale_date >= datetime.combine(date_from, datetime.min.time()),
            Sale.sale_date <= datetime.combine(date_to, datetime.max.time()),
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
        Sale.status.in_(['Оплачено', 'Возврат от покупателя']),
        Sale.sale_date >= datetime.combine(today - timedelta(days=365), datetime.min.time()),
    ).group_by(month_expr).order_by(month_expr).all()

    # Продажи по категориям за текущий месяц
    cat_expr = func.coalesce(Category.name, 'Без категории')
    by_category = db.session.query(
        cat_expr.label('cat'),
        func.sum(Sale.sale_price).label('revenue'),
    ).join(Product, Sale.product_id == Product.id
    ).outerjoin(Category, Product.category_id == Category.id
    ).filter(
        Sale.status.in_(['Оплачено', 'Возврат от покупателя']),
        Sale.sale_date >= datetime.combine(month_start, datetime.min.time()),
        Sale.sale_date <= datetime.combine(today, datetime.max.time()),
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


# ==============================
#        ГЛОБАЛЬНЫЙ ПОИСК
# ==============================


@app.route('/search')
def search():
    from sqlalchemy import or_
    q = request.args.get('q', '').strip()
    results = {'products': [], 'consignors': [], 'consignor_reports': [], 'consignor_returns': []}
    total = 0

    if q and len(q) >= 2:
        # SQLite lower() не поддерживает кириллицу, поэтому ищем как есть.
        # Для покрытия обоих регистров первой буквы добавляем два варианта.
        pat = f'%{q}%'
        pat_cap = f'%{q[0].upper()}{q[1:]}%'
        pat_low = f'%{q[0].lower()}{q[1:]}%'

        results['products'] = Product.query.filter(
            or_(
                Product.product_name.like(pat),
                Product.product_name.like(pat_cap),
                Product.product_name.like(pat_low),
                Product.description.like(pat),
                Product.description.like(pat_cap),
                Product.description.like(pat_low),
            )
        ).order_by(Product.product_name).limit(30).all()

        results['consignors'] = Consignor.query.filter(
            or_(
                Consignor.last_name.like(pat),
                Consignor.last_name.like(pat_cap),
                Consignor.last_name.like(pat_low),
                Consignor.first_name.like(pat),
                Consignor.first_name.like(pat_cap),
                Consignor.first_name.like(pat_low),
                Consignor.middle_name.like(pat),
                Consignor.phone_number.like(pat),
            )
        ).order_by(Consignor.last_name).limit(20).all()

        results['consignor_reports'] = ConsignorReport.query.filter(
            or_(
                ConsignorReport.number.like(pat),
                ConsignorReport.description.like(pat),
                ConsignorReport.description.like(pat_cap),
                ConsignorReport.description.like(pat_low),
            )
        ).order_by(ConsignorReport.date.desc()).limit(20).all()

        results['consignor_returns'] = ConsignorReturn.query.filter(
            or_(
                ConsignorReturn.number.like(pat),
                ConsignorReturn.description.like(pat),
                ConsignorReturn.description.like(pat_cap),
                ConsignorReturn.description.like(pat_low),
            )
        ).order_by(ConsignorReturn.date.desc()).limit(20).all()

        total = sum(len(v) for v in results.values())

    return render_template('search_results.html', q=q, results=results, total=total)


if __name__ == "__main__":
    init_db()
    app.run()  # debug=True
