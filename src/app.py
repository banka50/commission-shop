from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template, redirect, url_for, request, flash
from models import db, Consignor, ConsignorReport, SalesReport, Sale, Product
from config import Config

from datetime import datetime
from decimal import Decimal

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


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
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 2},
        {'id': 2, 'number': 'ACT-002', 'date': '2023-09-20',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 3},
        {'id': 3, 'number': 'ACT-003', 'date': '2023-10-01',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 4},
        {'id': 4, 'number': 'ACT-004', 'date': '2023-09-25',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 5},
        {'id': 5, 'number': 'ACT-005', 'date': '2023-10-05',
         'description': 'Акт приёма товаров от комитента', 'consignor_id': 1},
    ]

    sales_reports = [
        {'id': 1, 'number': 'REP-001', 'date': '2023-10-01',
         'report_type': 'Ежедневный отчет', 'description': 'Отчет о продажах за 01.10.2023'},
        {'id': 2, 'number': 'REP-002', 'date': '2023-10-07',
         'report_type': 'Еженедельный отчет', 'description': 'Отчет о продажах за неделю 02–07.10.2023'},
    ]

    products = [
        {'id': 1, 'product_name': 'Пальто зимнее', 'description': 'Женское, размер 48, цвет чёрный',
         'delivery_date': '2023-09-15', 'expiry_date': '2024-03-15', 'price': 4500.00,
         'consignor_report_id': 1, 'sale_id': None},
        {'id': 2, 'product_name': 'Ботинки кожаные', 'description': 'Мужские, размер 42, коричневые',
         'delivery_date': '2023-09-20', 'expiry_date': '2024-02-20', 'price': 3200.00,
         'consignor_report_id': 2, 'sale_id': 1},
        {'id': 3, 'product_name': 'Сумка женская', 'description': 'Кожаная, среднего размера, бежевая',
         'delivery_date': '2023-10-01', 'expiry_date': '2024-04-01', 'price': 2800.50,
         'consignor_report_id': 3, 'sale_id': None},
        {'id': 4, 'product_name': 'Часы наручные', 'description': 'Механические, мужские, сталь',
         'delivery_date': '2023-09-25', 'expiry_date': '2024-01-25', 'price': 12500.00,
         'consignor_report_id': 4, 'sale_id': 3},
        {'id': 5, 'product_name': 'Сервиз чайный', 'description': 'Фарфор, 12 персон, позолота',
         'delivery_date': '2023-10-05', 'expiry_date': '2024-05-05', 'price': 8900.00,
         'consignor_report_id': 5, 'sale_id': 4},
        {'id': 6, 'product_name': 'Шарф пуховый', 'description': 'Оренбургский, белый, ажурный',
         'delivery_date': '2023-10-10', 'expiry_date': '2024-01-10', 'price': 1500.00,
         'consignor_report_id': 1, 'sale_id': 5},
    ]

    sales = [
        {'id': 1, 'sale_date': '2023-10-01', 'sale_price': 1500.00,
         'commission': 150.00, 'status': 'Оплачено'},
        {'id': 2, 'sale_date': '2023-10-02', 'sale_price': 3200.50,
         'commission': 320.05, 'status': 'Ожидает'},
        {'id': 3, 'sale_date': '2023-10-03', 'sale_price': 780.00,
         'commission': 78.00, 'status': 'Оплачено'},
        {'id': 4, 'sale_date': '2023-10-04', 'sale_price': 2100.00,
         'commission': 210.00, 'status': 'Возврат'},
        {'id': 5, 'sale_date': '2023-10-05', 'sale_price': 540.75,
         'commission': 54.08, 'status': 'Оплачено'},
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
        )
        db.session.add(cr)
    db.session.flush()

    for sr_data in sales_reports:
        sr = SalesReport(
            number=sr_data['number'],
            date=datetime.strptime(sr_data['date'], '%Y-%m-%d').date(),
            report_type=sr_data['report_type'],
            description=sr_data['description'],
        )
        db.session.add(sr)
    db.session.flush()

    for sale_data in sales:
        sale = Sale(
            sale_date=datetime.strptime(sale_data['sale_date'], '%Y-%m-%d').date(),
            sale_price=sale_data['sale_price'],
            commission=sale_data['commission'],
            status=sale_data['status'],
        )
        db.session.add(sale)
    db.session.flush()

    for product_data in products:
        product = Product(
            product_name=product_data['product_name'],
            description=product_data['description'],
            delivery_date=datetime.strptime(product_data['delivery_date'], '%Y-%m-%d').date(),
            expiry_date=datetime.strptime(product_data['expiry_date'], '%Y-%m-%d').date(),
            price=product_data['price'],
            consignor_report_id=product_data['consignor_report_id'],
            sale_id=product_data['sale_id'],
        )
        db.session.add(product)

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

        new_report = ConsignorReport(
            number=number,
            date=date,
            description=description,
            consignor_id=consignor_id
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
    sales_reports = SalesReport.query.all()

    return render_template('sales_reports/sales_reports_list.html', sales_reports=sales_reports)


@app.route('/add_sales_report', methods=['GET', 'POST'])
def add_sales_report():
    if request.method == 'POST':
        number = request.form['number']
        date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        report_type = request.form['report_type']
        description = request.form['description']

        new_report = SalesReport(
            number=number,
            date=date,
            report_type=report_type,
            description=description
        )
        db.session.add(new_report)
        db.session.commit()
        flash('Отчёт по продажам успешно добавлен!', 'success')

        return redirect(url_for('sales_reports_list'))

    return render_template('sales_reports/sales_report_form.html', sales_report=None)


@app.route('/sales_report/<int:sales_report_id>')
def sales_report_detail(sales_report_id):
    sales_report = SalesReport.query.get_or_404(sales_report_id)

    return render_template('sales_reports/sales_report_detail.html', sales_report=sales_report)


@app.route('/edit_sales_report/<int:sales_report_id>', methods=['GET', 'POST'])
def edit_sales_report(sales_report_id):
    sales_report = SalesReport.query.get_or_404(sales_report_id)

    if request.method == 'POST':
        sales_report.number = request.form['number']
        sales_report.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        sales_report.report_type = request.form['report_type']
        sales_report.description = request.form['description']
        db.session.commit()
        flash('Данные обновлены!', 'success')

        return redirect(url_for('sales_reports_list'))

    return render_template('sales_reports/sales_report_form.html', sales_report=sales_report)


@app.route('/delete_sales_report/<int:sales_report_id>', methods=['POST'])
def delete_sales_report(sales_report_id):
    sales_report = SalesReport.query.get_or_404(sales_report_id)
    db.session.delete(sales_report)
    db.session.commit()
    flash('Отчёт по продажам успешно удалён!', 'success')

    return redirect(url_for('sales_reports_list'))


# ==============================
#           ПРОДАЖА
# ==============================


@app.route('/sales')
def sales_list():
    sales = Sale.query.all()

    return render_template('sales/sales_list.html', sales=sales)


@app.route('/add_sale', methods=['GET', 'POST'])
def add_sale():
    if request.method == 'POST':
        sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%d').date()
        sale_price = Decimal(request.form['sale_price'])
        commission = Decimal(request.form['commission'])
        status = request.form['status']

        new_sale = Sale(
            sale_date=sale_date,
            sale_price=sale_price,
            commission=commission,
            status=status
        )
        db.session.add(new_sale)
        db.session.commit()
        flash('Продажа успешно добавлена!', 'success')
        return redirect(url_for('sales_list'))

    return render_template('sales/sale_form.html', sale=None)


@app.route('/sale/<int:sale_id>')
def sale_detail(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    return render_template('sales/sale_detail.html', sale=sale)


@app.route('/edit_sale/<int:sale_id>', methods=['GET', 'POST'])
def edit_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    if request.method == 'POST':
        sale.sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%d').date()
        sale.sale_price = Decimal(request.form['sale_price'])
        sale.commission = Decimal(request.form['commission'])
        sale.status = request.form['status']
        db.session.commit()
        flash('Данные обновлены!', 'success')

        return redirect(url_for('sales_list'))

    return render_template('sales/sale_form.html', sale=sale)


@app.route('/delete_sale/<int:sale_id>', methods=['POST'])
def delete_sale(sale_id):
    sale = Sale.query.get_or_404(sale_id)

    if sale.products:
        flash('Продажу нельзя удалить, так как есть связанный с ней товар.', 'error')
        return redirect(url_for('sales_list'))
    db.session.delete(sale)
    db.session.commit()
    flash('Продажа успешно удалена!', 'success')

    return redirect(url_for('sales_list'))


# ==============================
#           ТОВАР
# ==============================


@app.route('/products')
def products_list():
    products = Product.query.all()
    consignor_reports = ConsignorReport.query.all()
    sales = Sale.query.all()
    consignor_reports_dict = {cr.id: cr.number for cr in consignor_reports}
    sales_dict = {sale.id: sale.status for sale in sales}

    return render_template('products/products_list.html', products=products,
                           consignor_reports=consignor_reports_dict, sales=sales_dict)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    consignor_reports = ConsignorReport.query.all()
    sales = Sale.query.all()
    preset_cr_id = request.args.get('consignor_report_id', type=int)
    preset_cr = ConsignorReport.query.get(preset_cr_id) if preset_cr_id else None

    if request.method == 'POST':
        product_name = request.form['product_name']
        description = request.form['description']
        delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d')
        expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d')
        price = request.form['price']
        consignor_report_id = request.form['consignor_report_id']
        sale_id = request.form['sale_id'] or None

        new_product = Product(
            product_name=product_name,
            description=description,
            delivery_date=delivery_date,
            expiry_date=expiry_date,
            price=price,
            consignor_report_id=consignor_report_id,
            sale_id=sale_id
        )
        db.session.add(new_product)
        db.session.commit()
        flash('Товар успешно добавлен!', 'success')

        if preset_cr_id:
            return redirect(url_for('consignor_report_detail', consignor_report_id=consignor_report_id))
        return redirect(url_for('products_list'))

    return render_template('products/product_form.html',
                           consignor_reports=consignor_reports, sales=sales,
                           preset_consignor_report=preset_cr)


@app.route('/products/<product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    return render_template('products/product_detail.html', product=product,
                           consignor_report=product.consignor_report, sale=product.sale)


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    consignor_reports = ConsignorReport.query.all()
    sales = Sale.query.all()

    if request.method == 'POST':
        product.product_name = request.form['product_name']
        product.description = request.form['description']
        product.delivery_date = datetime.strptime(request.form['delivery_date'], '%Y-%m-%d').date()
        product.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        product.price = request.form['price']
        product.consignor_report_id = request.form['consignor_report_id']
        product.sale_id = request.form['sale_id'] or None
        db.session.commit()
        flash('Данные обновлены!', 'success')

        return redirect(url_for('products_list'))

    return render_template('products/product_form.html', product=product,
                           consignor_reports=consignor_reports, sales=sales)


@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Товар успешно удалён!', 'success')

    return redirect(url_for('products_list'))


if __name__ == "__main__":
    init_db()
    app.run()  # debug=True
