-- Тип для статуса товара
CREATE TYPE product_status AS ENUM ('На витрине', 'Продан', 'Возвращён комитенту');

-- Тип для статуса продажи
CREATE TYPE sale_status AS ENUM ('Ожидает оплаты', 'Оплачено', 'Возврат от покупателя');

-- Тип для типа отчёта по продажам
CREATE TYPE report_type_enum AS ENUM (
    'Ежедневный отчет',
    'Еженедельный отчет',
    'Ежемесячный отчет',
    'Квартальный отчет',
    'Годовой отчет'
);

CREATE TABLE IF NOT EXISTS consignors (
    id            serial       NOT NULL,
    last_name     varchar(50)  NOT NULL,
    first_name    varchar(50)  NOT NULL,
    middle_name   varchar(50),
    email         varchar(100) NOT NULL UNIQUE,
    phone_number  varchar(20)  NOT NULL UNIQUE,
    passport_data varchar(50)  NOT NULL UNIQUE,
    inn           varchar(12)  NOT NULL UNIQUE,
    PRIMARY KEY (id)
);

-- Акт приёма товара от комитента
CREATE TABLE IF NOT EXISTS consignor_reports (
    id              serial         NOT NULL,
    number          varchar(50)    NOT NULL UNIQUE,
    date            date           NOT NULL,
    description     varchar(200)   NOT NULL,
    consignor_id    integer        NOT NULL,
    commission_pct  numeric(5, 2)  NOT NULL DEFAULT 20,  -- Процент комиссии
    commission_min  numeric(10, 2) NOT NULL DEFAULT 0,   -- Минимальная сумма комиссии
    PRIMARY KEY (id),
    CONSTRAINT consignor_reports_fk1 FOREIGN KEY (consignor_id) REFERENCES consignors (id)
);

-- Акт возврата товара комитенту
CREATE TABLE IF NOT EXISTS consignor_returns (
    id           serial       NOT NULL,
    number       varchar(50)  NOT NULL UNIQUE,
    date         date         NOT NULL,
    description  varchar(200),
    consignor_id integer      NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT consignor_returns_fk1 FOREIGN KEY (consignor_id) REFERENCES consignors (id)
);

-- Отчёт по продажам за период
CREATE TABLE IF NOT EXISTS sales_reports (
    id          serial           NOT NULL,
    number      varchar(50)      NOT NULL UNIQUE,
    date        date             NOT NULL,
    report_type report_type_enum NOT NULL,
    description varchar(200),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS products (
    id                   serial         NOT NULL,
    product_name         varchar(100)   NOT NULL,
    description          varchar(500),
    delivery_date        date           NOT NULL,
    expiry_date          date           NOT NULL,
    price                numeric(10, 2) NOT NULL,
    status               product_status NOT NULL DEFAULT 'На витрине',
    consignor_report_id  integer        NOT NULL,
    consignor_return_id  integer,                         -- Заполняется при возврате комитенту
    PRIMARY KEY (id),
    CONSTRAINT products_fk1 FOREIGN KEY (consignor_report_id) REFERENCES consignor_reports (id),
    CONSTRAINT products_fk2 FOREIGN KEY (consignor_return_id) REFERENCES consignor_returns (id)
);

-- Фотографии товара (хранятся на файловой системе)
CREATE TABLE IF NOT EXISTS product_images (
    id         serial       NOT NULL,
    filename   varchar(255) NOT NULL,
    product_id integer      NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT product_images_fk1 FOREIGN KEY (product_id) REFERENCES products (id)
);

CREATE TABLE IF NOT EXISTS sales (
    id         serial          NOT NULL,
    sale_date  date            NOT NULL,
    sale_price numeric(10, 2)  NOT NULL,
    commission numeric(10, 2)  NOT NULL,  -- Итоговая сумма комиссии: max(price * pct/100, min)
    status     sale_status     NOT NULL,
    product_id integer         NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT sales_fk1 FOREIGN KEY (product_id) REFERENCES products (id)
);
