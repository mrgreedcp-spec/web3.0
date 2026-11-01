-- 建表并导入数据。在 sql-practice 目录下运行：
--   duckdb shop.duckdb -c ".read setup.sql"      （DuckDB 命令行）
--   python3 build_db.py                          （Python）
-- 写法刻意接近 Snowflake 的 CREATE TABLE + COPY INTO，方便以后迁移。

CREATE OR REPLACE TABLE stores (
    store_id     INTEGER PRIMARY KEY,
    store_name   VARCHAR,
    city         VARCHAR,
    opened_date  DATE
);

CREATE OR REPLACE TABLE products (
    product_id       INTEGER PRIMARY KEY,
    product_name     VARCHAR,
    product_name_zh  VARCHAR,
    category         VARCHAR,
    unit             VARCHAR,
    unit_cost        DECIMAL(10, 2),
    list_price       DECIMAL(10, 2)
);

CREATE OR REPLACE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    city         VARCHAR,
    signup_date  DATE,
    member_tier  VARCHAR,   -- 普通 / 银卡 / 金卡
    birth_year   INTEGER
);

CREATE OR REPLACE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER,   -- 非会员为 NULL
    store_id        INTEGER,
    order_ts        TIMESTAMP,
    payment_method  VARCHAR,
    channel         VARCHAR    -- 门店 / 线上自提
);

-- 没有加主键：数据里故意留了重复行，L7 要找出来
CREATE OR REPLACE TABLE order_items (
    order_id    INTEGER,
    line_no     INTEGER,
    product_id  INTEGER,
    quantity    INTEGER,       -- 负数表示退货
    unit_price  DECIMAL(10, 2),
    discount    DECIMAL(10, 2)
);

CREATE OR REPLACE TABLE promotions (
    promo_id     INTEGER PRIMARY KEY,
    store_id     INTEGER,
    product_id   INTEGER,
    start_date   DATE,
    end_date     DATE,
    promo_price  DECIMAL(10, 2)
);

COPY stores      FROM 'data/stores.csv'      (HEADER);
COPY products    FROM 'data/products.csv'    (HEADER);
COPY customers   FROM 'data/customers.csv'   (HEADER);
COPY orders      FROM 'data/orders.csv'      (HEADER);
COPY order_items FROM 'data/order_items.csv' (HEADER);
COPY promotions  FROM 'data/promotions.csv'  (HEADER);

-- App 行为日志：device 和 properties 保留为 JSON，用来练半结构化查询
CREATE OR REPLACE TABLE app_events AS
SELECT *
FROM read_json('data/app_events.jsonl',
    format = 'newline_delimited',
    columns = {
        session_id: 'VARCHAR',
        customer_id: 'INTEGER',
        event_ts: 'TIMESTAMP',
        event_type: 'VARCHAR',
        device: 'JSON',
        properties: 'JSON'
    });

SELECT 'stores' AS table_name, count(*) AS row_count FROM stores
UNION ALL SELECT 'products', count(*) FROM products
UNION ALL SELECT 'customers', count(*) FROM customers
UNION ALL SELECT 'orders', count(*) FROM orders
UNION ALL SELECT 'order_items', count(*) FROM order_items
UNION ALL SELECT 'promotions', count(*) FROM promotions
UNION ALL SELECT 'app_events', count(*) FROM app_events;
