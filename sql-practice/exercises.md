# 超市 SQL 练习题（33 题，7 个等级）

数据是虚构的连锁超市 **Maple Fresh**：6 家门店（密西沙加 3 家，多伦多、布兰普顿、奥克维尔各 1 家），数据覆盖 2025-01-01 至 2026-10-31。

## 怎么做题

1. 先自己写，把 SQL 存成文件，比如 `answers/q05.sql`。
2. 判题：`python3 check.py 5 answers/q05.sql`。
3. 卡住了：先看本题的"提示"；还不行，用 `python3 check.py 5 --peek` 看答案的结果长什么样；最后再看 `solutions.sql`。
4. 判题只比结果，不比写法；行的顺序不计。所以**列的个数、顺序和小数位要按题目要求来**。

**通用约定：**行金额 = `quantity * unit_price - discount`。L1–L6 直接用原始数据，不用管里面的数据质量问题，L7 会专门处理。

## 表结构速查

| 表 | 字段 |
|---|---|
| `stores` 门店 | store_id, store_name, city, opened_date |
| `products` 商品 | product_id, product_name, product_name_zh, category, unit, unit_cost, list_price |
| `customers` 会员 | customer_id, city, signup_date, member_tier（普通/银卡/金卡）, birth_year |
| `orders` 订单 | order_id, customer_id（非会员为 NULL）, store_id, order_ts, payment_method, channel |
| `order_items` 订单明细 | order_id, line_no, product_id, quantity（负数=退货）, unit_price, discount |
| `promotions` 每周传单促销 | promo_id, store_id, product_id, start_date, end_date, promo_price |
| `app_events` App 行为日志 | session_id, customer_id, event_ts, event_type, device（JSON）, properties（JSON） |

拿到一张陌生的表，先跑这三条：`DESCRIBE orders;`、`SELECT * FROM orders LIMIT 5;`、`SUMMARIZE orders;`（DuckDB 专有，能一次看到每列的范围、空值和不同值的个数）。

---

## L1 基础查询：SELECT / WHERE / ORDER BY

**Q01** 列出所有门店，按开业日期从早到晚排序。
列：store_id, store_name, city, opened_date

**Q02** 找出品类为"乳制品"、售价（list_price）高于 5 的商品，按价格从高到低排。
列：product_id, product_name_zh, list_price

**Q03** 2026 年 10 月 1 日当天一共有多少笔订单？
列：order_count
> 提示：order_ts 带时分秒，需要先转成日期再比较。

**Q04** 找出英文名里含 "rice" 的商品，不区分大小写。
列：product_id, product_name, product_name_zh
> 提示：`ILIKE`。

> **平台差异：**`ILIKE` 在 Snowflake 和 Databricks 都能用。转日期也可以写成 `order_ts::DATE`，DuckDB 和 Snowflake 都支持这种写法。

---

## L2 聚合：GROUP BY / HAVING / 聚合函数

**Q05** 每个品类有多少个商品、平均售价是多少（保留 2 位小数）。
列：category, product_count, avg_price

**Q06** 每家门店 2026 年的销售额（保留 2 位小数）。
列：store_id, revenue_2026
> 提示：写成 `order_ts >= '2026-01-01' AND order_ts < '2027-01-01'`，比 `year(order_ts) = 2026` 更好。在大表上，前一种写法能利用分区或排序跳过无关数据，后一种不能。

**Q07** 每个月的销售额趋势。
列：month（用 `date_trunc('month', order_ts)`）, revenue（2 位小数）

**Q08** 找出下单次数超过 40 次的会员。
列：customer_id, order_count
> 提示：对聚合结果做筛选要用 `HAVING`，不能用 `WHERE`。

**Q09** 各支付方式的订单数，以及占总订单数的百分比（保留 1 位小数）。
列：payment_method, order_count, pct
> 提示：总数可以用窗口函数 `sum(count(*)) OVER ()` 在同一条查询里算出来。

> **平台差异：**`date_trunc` 三个平台都有。Snowflake 和 Databricks 习惯把单位写成大写 `'MONTH'`，效果一样。

---

## L3 JOIN

**Q10** 每家门店、每个品类的销售额（2 位小数）。
列：store_name, category, revenue

**Q11** 找出注册了但从没下过单的会员。
列：customer_id, signup_date, member_tier
> 提示：`LEFT JOIN` 之后筛选右表为空的行，也可以用 `NOT EXISTS`。

**Q12** 总销量（件数）前 10 的商品。
列：product_id, product_name_zh, category, units_sold

**Q13** 每个会员等级的订单数和平均客单价（一笔订单的总金额，2 位小数）。非会员订单单独算一组，名字叫"非会员"。
列：tier, order_count, avg_order_value
> 提示：先算出每笔订单的总额，再去关联会员表。如果直接用明细行关联再求平均，算出来的是"平均每行金额"，不是客单价。

---

## L4 窗口函数

**Q14** 每家门店销售额排前 3 的商品。
列：store_id, product_id, revenue（2 位小数）, rn（名次 1–3）
> 提示：`row_number() OVER (PARTITION BY ... ORDER BY ...)`，配合 `QUALIFY rn <= 3` 过滤。

**Q15** 每月销售额，以及相比上个月的环比增长率（%，1 位小数；第一个月为空）。
列：month, revenue（2 位小数）, mom_pct
> 提示：`lag()`。

**Q16** 会员 55 号（金卡）每笔订单的金额，以及到这笔为止的累计消费。
列：order_id, order_ts, order_value, running_total（都保留 2 位小数）

**Q17** 2026 年 10 月每天的销售额和 7 日移动平均（当天加前 6 天）。
列：day, revenue, ma7（2 位小数）
> 提示：这题有个坑。如果先只取 10 月的数据，10 月 1–6 日的移动平均会缺少 9 月底那几天。正确做法是多取几天再算，最后只保留 10 月。

**Q18** 每个商品的销售额占它所在品类销售额的百分比（1 位小数）。
列：category, product_name_zh, revenue（2 位小数）, pct_of_category

> **平台差异：**`QUALIFY` 和 `ROWS BETWEEN` 在 Snowflake 和 Databricks 都能用。窗口函数的写法三个平台基本一样，学一次就能通用。

---

## L5 业务分析：CTE + 日期

**Q19** 一周里星期几的平均日销售额最高？先算出每天的销售额，再按星期几求平均。
列：weekday（周一=1 … 周日=7）, avg_daily_revenue（2 位小数）
> 提示：DuckDB 用 `isodow(day)`。

**Q20** 促销效果分析（只看门店 1，去掉退货行）。对每个商品算四个数：促销期间的平均成交价、非促销期间的平均成交价、促销期间的日均销量、非促销期间的日均销量。
- 某天某商品"在促销"：门店 1 当天有一条覆盖这一天的促销记录
- 促销天数：该商品在 2025-01-01 到 2026-10-31 之间处于促销的天数（同一天只算一次）
- 非促销天数 = 669（总天数）− 促销天数
- 平均成交价 = 明细行 unit_price 的平均值；日均销量 = 件数 ÷ 天数。都保留 2 位小数

列：product_id, avg_price_promo, avg_price_normal, units_per_day_promo, units_per_day_normal
> 提示：用日期范围关联：`ON s.day BETWEEN pr.start_date AND pr.end_date`。数促销天数时，可以用 `generate_series` 把每段促销展开成逐日的行。

**Q21** 次月复购率。每个会员按首次下单的月份分组；看每组里有多少人在下一个自然月也下过单。不统计 2026-10 这一组（它还没有"下个月"）。
列：cohort（首单月份，`date_trunc` 的结果）, new_customers, next_month_return_pct（1 位小数）

**Q22** 购物篮分析。哪两个商品最常出现在同一笔订单里？列出前 10 对。去掉退货行；每对只算一次（小编号在前）。
列：product_a, product_b, together（同时出现的订单数）
> 提示：订单明细表和自己关联，条件 `a.product_id < b.product_id`。

**Q23** RFM 分层。以 2026-10-31 为基准，给每个下过单的会员计算：
- R：距离最后一次下单的天数（越小越好）
- F：订单数
- M：总消费

再用 `ntile(4)` 把 R、F、M 各分成 1–4 档，4 代表最好。排序时 R 按天数从大到小，F 和 M 从小到大，并列时按 customer_id 从小到大。
列：customer_id, recency_days, frequency, monetary（2 位小数）, r_score, f_score, m_score

> **平台差异（这一级差异最多）：**
> | 功能 | DuckDB | Snowflake | Databricks |
> |---|---|---|---|
> | 星期几（周一=1） | `isodow(d)` | `DAYOFWEEKISO(d)` | `weekday(d) + 1` |
> | 日期相减得天数 | `d2 - d1` | `DATEDIFF('day', d1, d2)` | `datediff(d2, d1)` |
> | 加一个月 | `d + INTERVAL 1 MONTH` | `DATEADD(month, 1, d)` | `add_months(d, 1)` |
> | 按条件聚合 | `sum(x) FILTER (WHERE …)` | `SUM(IFF(…, x, 0))` 或 `COUNT_IF` | `FILTER` 可用 |
> | 展开日期序列 | `generate_series` | 用 `GENERATOR` 或日期维表 | `explode(sequence(…))` |

---

## L6 半结构化 JSON

`app_events` 是 2026 年 9–10 月的 App 行为日志，`device` 和 `properties` 两列是 JSON。先看几行，了解结构：

```sql
SELECT event_type, device, properties FROM app_events LIMIT 10;
```

**Q24** 每种事件类型各有多少条。
列：event_type, events

**Q25** 热门搜索词前 10（搜索次数相同时按搜索词排序）。
列：keyword, searches
> 提示：`properties ->> 'keyword'` 取出文本。

**Q26** iOS 和 Android 各有多少个会话（session）。
列：os, sessions

**Q27** 加购事件的 `properties.items` 是一个数组。把它展开，统计被加购件数（qty 合计）最多的 10 个商品（并列时按 product_id 排序）。
列：product_id, units_added
> 提示：`unnest(CAST(properties -> 'items' AS JSON[]))`。

**Q28** 转化漏斗。统计浏览商品 → 加入购物车 → 结账 → 支付，每一步有多少个会话，以及相对上一步的转化率（%，1 位小数；第一步为空）。
列：step（1–4）, event_type, sessions, conversion_pct

> **平台差异：**半结构化数据是三个平台写法差别最大的地方。
> - Snowflake：列类型用 `VARIANT`；取字段 `properties:keyword::string`；展开数组用 `LATERAL FLATTEN(input => properties:items)`
> - Databricks：取字段 `properties:keyword`；展开数组用 `explode(from_json(...))`
>
> 写法不同，思路一样：先取出字段，再展开数组，最后聚合。

---

## L7 数据质量

真实数据一定会有问题。这份数据里故意埋了四类问题，找出来。

**Q29** 找出完全重复的订单明细行。每组只列一次，并给出重复了几次。
列：order_id, line_no, product_id, quantity, unit_price, discount, copies

**Q30** 各门店的退货率 = 退货件数 ÷ 售出件数（%，2 位小数）。退货件数用正数表示。
列：store_id, units_sold, units_returned, return_rate_pct

**Q31** 订单明细里有哪些行引用了商品表里不存在的商品？
列：order_items 的全部 6 列

**Q32** 哪个商品的英文名首尾有多余的空格？
列：product_id, product_name
> 提示：比较 `product_name` 和 `trim(product_name)`。

**Q33** 建一个干净的视图 `clean_order_items`：去掉完全重复的行和不存在的商品（退货行要保留，它们是真实业务）。然后用这个视图重算 Q06，对比一下和原来差了多少。
列：store_id, revenue_2026

> **思考：**Q06 和 Q33 差多少？如果报表一直用的是脏数据，会多报还是少报？在实际工作里，这类视图（或者 dbt 模型）通常就是数据团队交给业务方使用的那一层。

---

## 配合 AI 练习

上一课的 prompt 模板在这里都用得上：

- **做错了，让 AI 帮你找原因，但不直接给答案：**
  > 我在用 DuckDB 做 SQL 练习。题目是：（贴题目）。表结构：（贴相关表）。我的 SQL：（贴）。判题结果：（贴 check.py 的输出）。请指出我错在哪里、为什么错，先不要给完整答案。
- **做对了，让 AI 帮你迁移到其他平台：**
  > 把这条 DuckDB SQL 改写成 Snowflake 版本和 Databricks SQL 版本，并列出改动了哪些函数、为什么要改。
- **让 AI 出变式题：**
  > 基于这份超市数据的表结构，按 Q20 的难度再出 3 道题，只给题目和要求输出的列，不要答案。

建议做法：每一级先自己独立做完，再用 AI 复盘。直接问 AI 要答案学得最慢，也最费 token。
