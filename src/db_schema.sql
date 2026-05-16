-- Тип для статуса продажи
CREATE TYPE sale_status AS ENUM ('Оплачено', 'Ожидает', 'Возврат');

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
    id           serial       NOT NULL,
    number       varchar(50)  NOT NULL UNIQUE,
    date         date         NOT NULL,
    description  varchar(200) NOT NULL,
    consignor_id integer      NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT consignor_reports_fk1 FOREIGN KEY (consignor_id) REFERENCES consignors (id)
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
    consignor_report_id  integer        NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT products_fk1 FOREIGN KEY (consignor_report_id) REFERENCES consignor_reports (id)
);

CREATE TABLE IF NOT EXISTS sales (
    id         serial          NOT NULL,
    sale_date  date            NOT NULL,
    sale_price numeric(10, 2)  NOT NULL,
    commission numeric(10, 2)  NOT NULL,
    status     sale_status     NOT NULL,
    product_id integer         NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT sales_fk1 FOREIGN KEY (product_id) REFERENCES products (id)
);
