-- Схема базы данных комиссионного магазина

-- Статус товара
CREATE TYPE product_status AS ENUM (
    'На витрине',
    'Продан',
    'Возвращён комитенту'
);

-- Статус продажи
CREATE TYPE sale_status AS ENUM (
    'Ожидает оплаты',
    'Оплачено',
    'Возврат от покупателя'
);

-- Комитенты
CREATE TABLE consignors (
    id             SERIAL PRIMARY KEY,
    last_name      VARCHAR(50)  NOT NULL,
    first_name     VARCHAR(50)  NOT NULL,
    middle_name    VARCHAR(50),
    email          VARCHAR(100) NOT NULL UNIQUE,
    phone_number   VARCHAR(20)  NOT NULL UNIQUE,
    passport_data  VARCHAR(50)  NOT NULL UNIQUE,
    inn            VARCHAR(12)  NOT NULL UNIQUE
);

-- Акты приёма товара от комитентов
CREATE TABLE consignor_reports (
    id              SERIAL PRIMARY KEY,
    number          VARCHAR(50)    NOT NULL UNIQUE,
    date            DATE           NOT NULL,
    description     VARCHAR(200)   NOT NULL,
    consignor_id    INTEGER        NOT NULL REFERENCES consignors(id),
    commission_pct  NUMERIC(5,2)   NOT NULL DEFAULT 20,  -- процент комиссии
    commission_min  NUMERIC(10,2)  NOT NULL DEFAULT 0    -- минимальная сумма комиссии
);

-- Акты возврата товара комитенту
CREATE TABLE consignor_returns (
    id            SERIAL PRIMARY KEY,
    number        VARCHAR(50)  NOT NULL UNIQUE,
    date          DATE         NOT NULL,
    description   VARCHAR(200),
    consignor_id  INTEGER      NOT NULL REFERENCES consignors(id)
);

-- Категории товаров
CREATE TABLE categories (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL UNIQUE,
    description  VARCHAR(200)
);

-- Товары
CREATE TABLE products (
    id                   SERIAL PRIMARY KEY,
    product_name         VARCHAR(100)    NOT NULL,
    description          VARCHAR(500),
    delivery_date        DATE            NOT NULL,
    expiry_date          DATE            NOT NULL,
    price                NUMERIC(10,2)   NOT NULL,
    status               product_status  NOT NULL DEFAULT 'На витрине',
    category_id          INTEGER         REFERENCES categories(id),
    consignor_report_id  INTEGER         NOT NULL REFERENCES consignor_reports(id),
    consignor_return_id  INTEGER         REFERENCES consignor_returns(id)
);

-- Фотографии товаров (хранятся на файловой системе)
CREATE TABLE product_images (
    id          SERIAL PRIMARY KEY,
    filename    VARCHAR(255) NOT NULL,
    product_id  INTEGER      NOT NULL REFERENCES products(id) ON DELETE CASCADE
);

-- Продажи
-- sale_price и commission: положительные для обычных продаж,
-- отрицательные (сторно) для возвратов от покупателя.
CREATE TABLE sales (
    id          SERIAL PRIMARY KEY,
    sale_date   DATE           NOT NULL,
    sale_price  NUMERIC(10,2)  NOT NULL,
    commission  NUMERIC(10,2)  NOT NULL,
    status      sale_status    NOT NULL,
    product_id  INTEGER        NOT NULL REFERENCES products(id)
);

-- Отчёты по продажам (snapshot)
CREATE TABLE sales_reports (
    id                SERIAL PRIMARY KEY,
    number            VARCHAR(50)    NOT NULL UNIQUE,
    date              DATE           NOT NULL,      -- дата формирования отчёта
    date_from         DATE           NOT NULL,      -- начало периода
    date_to           DATE           NOT NULL,      -- конец периода
    description       VARCHAR(200),
    total_revenue     NUMERIC(10,2)  NOT NULL DEFAULT 0,
    total_commission  NUMERIC(10,2)  NOT NULL DEFAULT 0,
    total_payable     NUMERIC(10,2)  NOT NULL DEFAULT 0
);

-- Строки отчёта по продажам
CREATE TABLE sales_report_lines (
    id              SERIAL PRIMARY KEY,
    report_id       INTEGER        NOT NULL REFERENCES sales_reports(id) ON DELETE CASCADE,
    sale_id         INTEGER        REFERENCES sales(id),  -- может быть NULL если продажа удалена
    -- snapshot данных на момент формирования
    sale_date       DATE           NOT NULL,
    product_name    VARCHAR(100)   NOT NULL,
    category_name   VARCHAR(100),
    consignor_name  VARCHAR(150)   NOT NULL,
    sale_price      NUMERIC(10,2)  NOT NULL,
    commission      NUMERIC(10,2)  NOT NULL,
    payable         NUMERIC(10,2)  NOT NULL
);
