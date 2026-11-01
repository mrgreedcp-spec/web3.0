-- 标准答案。每题以 "-- Q编号" 开头，check.py 按编号取答案判题。
-- 先自己做，做完再看。很多题有不止一种写法，结果一致就算对。
-- 约定：行金额 = quantity * unit_price - discount

-- ============================================================ L1 基础查询

-- Q01 所有门店按开业日期从早到晚
SELECT store_id, store_name, city, opened_date
FROM stores
ORDER BY opened_date;

-- Q02 乳制品里售价高于 5 元的商品，价格从高到低
SELECT product_id, product_name_zh, list_price
FROM products
WHERE category = '乳制品' AND list_price > 5
ORDER BY list_price DESC;

-- Q03 2026-10-01 当天的订单数
SELECT count(*) AS order_count
FROM orders
WHERE CAST(order_ts AS DATE) = DATE '2026-10-01';

-- Q04 英文名里含 rice 的商品（不区分大小写）
SELECT product_id, product_name, product_name_zh
FROM products
WHERE product_name ILIKE '%rice%'
ORDER BY product_id;

-- ============================================================ L2 聚合

-- Q05 每个品类的商品数和平均售价（保留 2 位小数）
SELECT category,
       count(*)                   AS product_count,
       round(avg(list_price), 2)  AS avg_price
FROM products
GROUP BY category
ORDER BY product_count DESC, category;

-- Q06 每家门店 2026 年的销售额
SELECT o.store_id,
       round(sum(i.quantity * i.unit_price - i.discount), 2) AS revenue_2026
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
WHERE o.order_ts >= TIMESTAMP '2026-01-01' AND o.order_ts < TIMESTAMP '2027-01-01'
GROUP BY o.store_id
ORDER BY revenue_2026 DESC;

-- Q07 每月销售额趋势
SELECT date_trunc('month', o.order_ts)                         AS month,
       round(sum(i.quantity * i.unit_price - i.discount), 2)  AS revenue
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
GROUP BY month
ORDER BY month;

-- Q08 下单超过 40 次的会员
SELECT customer_id, count(*) AS order_count
FROM orders
WHERE customer_id IS NOT NULL
GROUP BY customer_id
HAVING count(*) > 40
ORDER BY order_count DESC, customer_id;

-- Q09 各支付方式的订单占比（百分比，保留 1 位小数）
SELECT payment_method,
       count(*) AS order_count,
       round(100.0 * count(*) / sum(count(*)) OVER (), 1) AS pct
FROM orders
GROUP BY payment_method
ORDER BY order_count DESC;

-- ============================================================ L3 JOIN

-- Q10 每家门店、每个品类的销售额
SELECT s.store_name, p.category,
       round(sum(i.quantity * i.unit_price - i.discount), 2) AS revenue
FROM order_items i
JOIN orders   o ON o.order_id = i.order_id
JOIN stores   s ON s.store_id = o.store_id
JOIN products p ON p.product_id = i.product_id
GROUP BY s.store_name, p.category
ORDER BY s.store_name, revenue DESC;

-- Q11 从没下过单的会员
SELECT c.customer_id, c.signup_date, c.member_tier
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
ORDER BY c.customer_id;

-- Q12 销量（件数）前 10 的商品，带中文名和品类
SELECT p.product_id, p.product_name_zh, p.category,
       sum(i.quantity) AS units_sold
FROM order_items i
JOIN products p ON p.product_id = i.product_id
GROUP BY p.product_id, p.product_name_zh, p.category
ORDER BY units_sold DESC
LIMIT 10;

-- Q13 每个会员等级的平均客单价；非会员单独算一组
WITH order_totals AS (
    SELECT order_id, sum(quantity * unit_price - discount) AS order_value
    FROM order_items
    GROUP BY order_id
)
SELECT coalesce(c.member_tier, '非会员')   AS tier,
       count(*)                            AS order_count,
       round(avg(t.order_value), 2)        AS avg_order_value
FROM orders o
JOIN order_totals t ON t.order_id = o.order_id
LEFT JOIN customers c ON c.customer_id = o.customer_id
GROUP BY tier
ORDER BY avg_order_value DESC;

-- ============================================================ L4 窗口函数

-- Q14 每家门店销售额前 3 的商品
SELECT o.store_id, i.product_id,
       round(sum(i.quantity * i.unit_price - i.discount), 2) AS revenue,
       row_number() OVER (PARTITION BY o.store_id
                          ORDER BY sum(i.quantity * i.unit_price - i.discount) DESC) AS rn
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
GROUP BY o.store_id, i.product_id
QUALIFY rn <= 3
ORDER BY o.store_id, rn;

-- Q15 每月销售额和环比增长率（%）
WITH monthly AS (
    SELECT date_trunc('month', o.order_ts) AS month,
           sum(i.quantity * i.unit_price - i.discount) AS revenue
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    GROUP BY month
)
SELECT month,
       round(revenue, 2) AS revenue,
       round(100 * (revenue / lag(revenue) OVER (ORDER BY month) - 1), 1) AS mom_pct
FROM monthly
ORDER BY month;

-- Q16 会员 55 号（金卡）每笔订单的金额和累计消费
WITH order_totals AS (
    SELECT o.order_id, o.order_ts, sum(i.quantity * i.unit_price - i.discount) AS order_value
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    WHERE o.customer_id = 55
    GROUP BY o.order_id, o.order_ts
)
SELECT order_id, order_ts,
       round(order_value, 2) AS order_value,
       round(sum(order_value) OVER (ORDER BY order_ts
             ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total
FROM order_totals
ORDER BY order_ts;

-- Q17 2026 年 10 月每天的销售额和 7 日移动平均
WITH daily AS (
    SELECT CAST(o.order_ts AS DATE) AS day,
           sum(i.quantity * i.unit_price - i.discount) AS revenue
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    WHERE o.order_ts >= TIMESTAMP '2026-09-24' AND o.order_ts < TIMESTAMP '2026-11-01'
    GROUP BY day
)
SELECT day, round(revenue, 2) AS revenue,
       round(avg(revenue) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW), 2) AS ma7
FROM daily
QUALIFY day >= DATE '2026-10-01'
ORDER BY day;

-- Q18 每个商品在本品类销售额中的占比（%）
WITH prod AS (
    SELECT p.category, p.product_name_zh,
           sum(i.quantity * i.unit_price - i.discount) AS revenue
    FROM order_items i
    JOIN products p ON p.product_id = i.product_id
    GROUP BY p.category, p.product_name_zh
)
SELECT category, product_name_zh, round(revenue, 2) AS revenue,
       round(100 * revenue / sum(revenue) OVER (PARTITION BY category), 1) AS pct_of_category
FROM prod
ORDER BY category, pct_of_category DESC;

-- ============================================================ L5 业务分析（CTE + 日期）

-- Q19 星期几的平均日销售额最高（周一=1 … 周日=7）
WITH daily AS (
    SELECT CAST(o.order_ts AS DATE) AS day,
           sum(i.quantity * i.unit_price - i.discount) AS revenue
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    GROUP BY day
)
SELECT isodow(day) AS weekday, round(avg(revenue), 2) AS avg_daily_revenue
FROM daily
GROUP BY weekday
ORDER BY weekday;

-- Q20 促销效果：每个商品在促销期和非促销期的平均成交价、日均销量
--     （只看门店 1，促销按 store_id + product_id + 日期匹配）
WITH sales AS (
    SELECT CAST(o.order_ts AS DATE) AS day, i.product_id, i.quantity, i.unit_price
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    WHERE o.store_id = 1 AND i.quantity > 0
),
tagged AS (
    SELECT s.*, (pr.promo_id IS NOT NULL) AS on_promo
    FROM sales s
    LEFT JOIN promotions pr
           ON pr.store_id = 1 AND pr.product_id = s.product_id
          AND s.day BETWEEN pr.start_date AND pr.end_date
),
promo_days AS (   -- 每个商品在门店 1 的促销天数
    SELECT product_id, count(DISTINCT d) AS days
    FROM promotions, generate_series(start_date, end_date, INTERVAL 1 DAY) AS g(d)
    WHERE store_id = 1 AND CAST(d AS DATE) BETWEEN DATE '2025-01-01' AND DATE '2026-10-31'
    GROUP BY product_id
),
total_days AS (SELECT (DATE '2026-10-31' - DATE '2025-01-01') + 1 AS days)
SELECT t.product_id,
       round(avg(t.unit_price) FILTER (WHERE t.on_promo), 2)      AS avg_price_promo,
       round(avg(t.unit_price) FILTER (WHERE NOT t.on_promo), 2)  AS avg_price_normal,
       round(sum(t.quantity) FILTER (WHERE t.on_promo) / any_value(pd.days), 2) AS units_per_day_promo,
       round(sum(t.quantity) FILTER (WHERE NOT t.on_promo)
             / (any_value(td.days) - any_value(pd.days)), 2)        AS units_per_day_normal
FROM tagged t
JOIN promo_days pd ON pd.product_id = t.product_id
CROSS JOIN total_days td
GROUP BY t.product_id
ORDER BY units_per_day_promo / units_per_day_normal DESC;

-- Q21 首单后的次月复购率：按首单月份分组，看下一个自然月还有没有消费
WITH member_orders AS (
    SELECT DISTINCT customer_id, date_trunc('month', order_ts) AS month
    FROM orders
    WHERE customer_id IS NOT NULL
),
first_month AS (
    SELECT customer_id, min(month) AS cohort
    FROM member_orders
    GROUP BY customer_id
)
SELECT f.cohort,
       count(*) AS new_customers,
       round(100.0 * count(m.customer_id) / count(*), 1) AS next_month_return_pct
FROM first_month f
LEFT JOIN member_orders m
       ON m.customer_id = f.customer_id AND m.month = f.cohort + INTERVAL 1 MONTH
WHERE f.cohort < DATE '2026-10-01'
GROUP BY f.cohort
ORDER BY f.cohort;

-- Q22 购物篮分析：最常出现在同一订单里的商品组合前 10
WITH basket AS (
    SELECT DISTINCT order_id, product_id FROM order_items WHERE quantity > 0
)
SELECT a.product_id AS product_a, b.product_id AS product_b, count(*) AS together
FROM basket a
JOIN basket b ON a.order_id = b.order_id AND a.product_id < b.product_id
GROUP BY product_a, product_b
ORDER BY together DESC
LIMIT 10;

-- Q23 RFM 分层：以 2026-10-31 为基准，给每个下过单的会员算 R、F、M，各分 1-4 档（4 最好）
WITH base AS (
    SELECT o.customer_id,
           DATE '2026-10-31' - max(CAST(o.order_ts AS DATE))            AS recency_days,
           count(DISTINCT o.order_id)                                   AS frequency,
           sum(i.quantity * i.unit_price - i.discount)                  AS monetary
    FROM orders o
    JOIN order_items i ON i.order_id = o.order_id
    WHERE o.customer_id IS NOT NULL
    GROUP BY o.customer_id
)
SELECT customer_id, recency_days, frequency, round(monetary, 2) AS monetary,
       ntile(4) OVER (ORDER BY recency_days DESC, customer_id) AS r_score,
       ntile(4) OVER (ORDER BY frequency, customer_id)         AS f_score,
       ntile(4) OVER (ORDER BY monetary, customer_id)          AS m_score
FROM base
ORDER BY customer_id;

-- ============================================================ L6 半结构化 JSON

-- Q24 各事件类型的数量
SELECT event_type, count(*) AS events
FROM app_events
GROUP BY event_type
ORDER BY events DESC;

-- Q25 热门搜索词前 10
SELECT properties ->> 'keyword' AS keyword, count(*) AS searches
FROM app_events
WHERE event_type = 'search'
GROUP BY keyword
ORDER BY searches DESC, keyword
LIMIT 10;

-- Q26 iOS 和 Android 各有多少个会话
SELECT device ->> 'os' AS os, count(DISTINCT session_id) AS sessions
FROM app_events
GROUP BY os
ORDER BY sessions DESC;

-- Q27 把加购事件里的 items 数组展开，统计被加购件数最多的 10 个商品
WITH carts AS (
    SELECT unnest(CAST(properties -> 'items' AS JSON[])) AS item
    FROM app_events
    WHERE event_type = 'add_to_cart'
)
SELECT CAST(item ->> 'product_id' AS INTEGER) AS product_id,
       sum(CAST(item ->> 'qty' AS INTEGER))   AS units_added
FROM carts
GROUP BY product_id
ORDER BY units_added DESC, product_id
LIMIT 10;

-- Q28 转化漏斗：浏览 → 加购 → 结账 → 支付，各步会话数和相对上一步的转化率
WITH steps AS (
    SELECT 1 AS step, 'view_product' AS event_type UNION ALL
    SELECT 2, 'add_to_cart' UNION ALL
    SELECT 3, 'checkout' UNION ALL
    SELECT 4, 'purchase'
),
counts AS (
    SELECT s.step, s.event_type, count(DISTINCT e.session_id) AS sessions
    FROM steps s
    LEFT JOIN app_events e ON e.event_type = s.event_type
    GROUP BY s.step, s.event_type
)
SELECT step, event_type, sessions,
       round(100.0 * sessions / lag(sessions) OVER (ORDER BY step), 1) AS conversion_pct
FROM counts
ORDER BY step;

-- ============================================================ L7 数据质量

-- Q29 找出完全重复的订单明细行（每组列一次，并给出重复次数）
SELECT order_id, line_no, product_id, quantity, unit_price, discount, count(*) AS copies
FROM order_items
GROUP BY ALL
HAVING count(*) > 1
ORDER BY order_id, line_no;

-- Q30 各门店的退货率：退货件数 ÷ 售出件数（%）
SELECT o.store_id,
       sum(i.quantity) FILTER (WHERE i.quantity > 0)   AS units_sold,
       -sum(i.quantity) FILTER (WHERE i.quantity < 0)  AS units_returned,
       round(100.0 * -sum(i.quantity) FILTER (WHERE i.quantity < 0)
             / sum(i.quantity) FILTER (WHERE i.quantity > 0), 2) AS return_rate_pct
FROM orders o
JOIN order_items i ON i.order_id = o.order_id
GROUP BY o.store_id
ORDER BY o.store_id;

-- Q31 订单明细里引用了不存在商品的行
SELECT i.*
FROM order_items i
LEFT JOIN products p ON p.product_id = i.product_id
WHERE p.product_id IS NULL
ORDER BY i.order_id, i.line_no;

-- Q32 商品名首尾有多余空格的商品
SELECT product_id, product_name
FROM products
WHERE product_name <> trim(product_name);

-- Q33 建一个干净的视图：去重、去掉不存在的商品；再用它重算 2026 年各门店销售额
CREATE OR REPLACE VIEW clean_order_items AS
SELECT DISTINCT i.*
FROM order_items i
JOIN products p ON p.product_id = i.product_id;

SELECT o.store_id,
       round(sum(i.quantity * i.unit_price - i.discount), 2) AS revenue_2026
FROM orders o
JOIN clean_order_items i ON i.order_id = o.order_id
WHERE o.order_ts >= TIMESTAMP '2026-01-01' AND o.order_ts < TIMESTAMP '2027-01-01'
GROUP BY o.store_id
ORDER BY revenue_2026 DESC;
