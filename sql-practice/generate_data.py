#!/usr/bin/env python3
"""生成超市练习数据（虚构），输出到 data/ 目录。

只用 Python 标准库；固定随机种子，每次生成的数据完全一样，答案可以对得上。
数据里故意埋了几个质量问题（重复行、退货负数、脏字符串、不存在的商品），L7 会用到。
"""
from __future__ import annotations

import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 42
START = date(2025, 1, 1)
END = date(2026, 10, 31)
OUT = Path(__file__).resolve().parent / "data"

STORES = [
    # store_id, name, city, opened_date, size_factor
    (1, "Maple Fresh Square One", "Mississauga", "2018-05-12", 1.4),
    (2, "Maple Fresh Heartland", "Mississauga", "2020-09-01", 1.1),
    (3, "Maple Fresh Erin Mills", "Mississauga", "2022-03-19", 0.9),
    (4, "Maple Fresh Scarborough", "Toronto", "2016-11-05", 1.2),
    (5, "Maple Fresh Brampton", "Brampton", "2021-06-26", 0.8),
    (6, "Maple Fresh Oakville", "Oakville", "2025-04-10", 0.7),  # 2025 年新开
]

# product_id, name, name_zh, category, unit, cost, list_price
PRODUCTS = [
    (101, "Bananas", "香蕉", "蔬菜水果", "lb", 0.35, 0.79),
    (102, "Gala Apples 3lb", "嘎啦苹果 3磅", "蔬菜水果", "bag", 2.10, 4.99),
    (103, "Russet Potatoes 5lb", "褐皮土豆 5磅", "蔬菜水果", "bag", 1.80, 3.99),
    (104, "Bok Choy", "上海青", "蔬菜水果", "lb", 0.70, 1.99),
    (105, "Napa Cabbage", "大白菜", "蔬菜水果", "each", 1.10, 2.99),
    (106, "Strawberries 1lb", "草莓 1磅", "蔬菜水果", "pack", 2.20, 4.49),
    (107, "Yellow Onions 3lb", "黄洋葱 3磅", "蔬菜水果", "bag", 1.00, 2.49),
    (108, "Avocados 4pk", "牛油果 4个装", "蔬菜水果", "pack", 2.60, 5.99),
    (109, "Ginger", "生姜", "蔬菜水果", "lb", 1.20, 2.99),
    (110, "Cucumbers", "黄瓜", "蔬菜水果", "each", 0.40, 0.99),
    (201, "Chicken Thighs", "鸡腿肉", "肉类海鲜", "kg", 6.50, 11.99),
    (202, "Pork Belly", "五花肉", "肉类海鲜", "kg", 8.00, 14.99),
    (203, "Lean Ground Beef", "瘦牛肉馅", "肉类海鲜", "kg", 9.50, 15.99),
    (204, "Atlantic Salmon Fillet", "三文鱼柳", "肉类海鲜", "kg", 14.00, 24.99),
    (205, "Frozen Shrimp 31-40", "冻虾 31-40", "肉类海鲜", "bag", 7.50, 13.99),
    (206, "Tilapia Fillet", "罗非鱼柳", "肉类海鲜", "kg", 6.00, 10.99),
    (301, "2% Milk 4L", "2% 牛奶 4升", "乳制品", "jug", 4.20, 6.49),
    (302, "Large Eggs 12", "大号鸡蛋 12个", "乳制品", "dozen", 2.80, 4.79),
    (303, "Greek Yogurt 750g", "希腊酸奶 750克", "乳制品", "tub", 3.50, 6.99),
    (304, "Cheddar Cheese 400g", "切达奶酪 400克", "乳制品", "block", 4.00, 7.49),
    (305, "Salted Butter 454g", "有盐黄油 454克", "乳制品", "block", 4.30, 6.99),
    (306, "Soy Milk 1.89L", "豆奶 1.89升", "乳制品", "carton", 2.10, 3.99),
    (307, "Cream Cheese 250g", "奶油奶酪 250克", "乳制品", "block", 2.20, 4.29),
    (401, "Sliced White Bread", "切片白面包", "烘焙", "loaf", 1.30, 2.99),
    (402, "Croissants 6pk", "牛角包 6个装", "烘焙", "pack", 2.50, 5.49),
    (403, "Bagels 6pk", "贝果 6个装", "烘焙", "pack", 1.80, 3.99),
    (404, "Pineapple Buns 4pk", "菠萝包 4个装", "烘焙", "pack", 2.30, 4.99),
    (501, "Jasmine Rice 8kg", "茉莉香米 8公斤", "粮油干货", "bag", 11.00, 19.99),
    (502, "Brown Rice 2kg ", "糙米 2公斤", "粮油干货", "bag", 3.20, 5.99),  # 名字末尾故意多一个空格
    (503, "Canola Oil 3L", "菜籽油 3升", "粮油干货", "bottle", 5.50, 9.99),
    (504, "Soy Sauce 1.8L", "生抽 1.8升", "粮油干货", "bottle", 3.00, 5.49),
    (505, "Spaghetti 900g", "意大利面 900克", "粮油干货", "box", 1.20, 2.79),
    (506, "Instant Noodles 5pk", "方便面 5包装", "粮油干货", "pack", 2.00, 4.49),
    (507, "All Purpose Flour 2.5kg", "中筋面粉 2.5公斤", "粮油干货", "bag", 2.60, 4.99),
    (508, "Rice Vinegar 500ml", "米醋 500毫升", "粮油干货", "bottle", 1.40, 2.99),
    (601, "Potato Chips 235g", "薯片 235克", "饮料零食", "bag", 1.60, 3.99),
    (602, "Sparkling Water 12pk", "气泡水 12罐", "饮料零食", "case", 3.50, 6.99),
    (603, "Orange Juice 1.54L", "橙汁 1.54升", "饮料零食", "carton", 2.40, 4.99),
    (604, "Green Tea 24 bags", "绿茶 24包", "饮料零食", "box", 1.80, 3.99),
    (605, "Dark Chocolate 100g", "黑巧克力 100克", "饮料零食", "bar", 1.30, 2.99),
    (606, "Rice Crackers", "米饼", "饮料零食", "bag", 1.50, 3.49),
    (607, "Cola 2L", "可乐 2升", "饮料零食", "bottle", 1.00, 2.49),
    (701, "Frozen Dumplings 1kg", "速冻饺子 1公斤", "冷冻食品", "bag", 4.50, 8.99),
    (702, "Frozen Pizza", "冷冻披萨", "冷冻食品", "box", 3.20, 6.99),
    (703, "Ice Cream 1.5L", "冰淇淋 1.5升", "冷冻食品", "tub", 3.00, 5.99),
    (704, "Frozen Mixed Vegetables 1kg", "冷冻杂菜 1公斤", "冷冻食品", "bag", 2.00, 3.99),
    (705, "Hash Browns 1kg", "薯饼 1公斤", "冷冻食品", "bag", 2.10, 4.49),
    (801, "Paper Towels 6 rolls", "厨房纸 6卷", "日用品", "pack", 4.50, 8.99),
    (802, "Dish Soap 709ml", "洗洁精 709毫升", "日用品", "bottle", 1.80, 3.49),
    (803, "Toilet Paper 12 rolls", "卫生纸 12卷", "日用品", "pack", 6.00, 10.99),
    (804, "Laundry Detergent 2.03L", "洗衣液 2.03升", "日用品", "jug", 6.50, 12.99),
    (805, "Garbage Bags 40ct", "垃圾袋 40个", "日用品", "box", 3.20, 6.49),
]

# 经常一起买的组合（购物篮分析题会用到）
BUNDLES = [(301, 302), (401, 305), (201, 104), (701, 504), (402, 303), (601, 607), (501, 504)]
# 季节性：月份 -> {product_id: 倍数}
SEASONAL = {6: {106: 3, 703: 3, 602: 2}, 7: {106: 3, 703: 3, 602: 2}, 8: {703: 2, 602: 2},
            12: {204: 2, 202: 2, 402: 2}, 1: {701: 2.5, 105: 2}, 2: {701: 2, 105: 1.5}}

PAYMENTS = [("借记卡", 0.38), ("信用卡", 0.34), ("手机支付", 0.18), ("现金", 0.10)]
TIERS = [("普通", 0.6), ("银卡", 0.3), ("金卡", 0.1)]
TIER_FREQ = {"普通": 1.0, "银卡": 2.0, "金卡": 4.0}
CITIES = [("Mississauga", 0.5), ("Toronto", 0.2), ("Brampton", 0.15), ("Oakville", 0.15)]
SEARCH_WORDS = ["牛奶", "鸡蛋", "大米", "饺子", "milk", "eggs", "rice", "三文鱼", "草莓", "面包",
                "avocado", "五花肉", "豆奶", "方便面", "洗衣液", "chips", "yogurt", "上海青"]


def wchoice(rng: random.Random, pairs):
    return rng.choices([p[0] for p in pairs], weights=[p[1] for p in pairs])[0]


def daterange(a: date, b: date):
    d = a
    while d <= b:
        yield d
        d += timedelta(days=1)


def write_csv(name: str, header: list[str], rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def main():
    rng = random.Random(SEED)
    OUT.mkdir(exist_ok=True)
    price = {p[0]: p[6] for p in PRODUCTS}
    pids = [p[0] for p in PRODUCTS]

    # ---------------- 门店、商品
    write_csv("stores.csv", ["store_id", "store_name", "city", "opened_date"],
              [s[:4] for s in STORES])
    write_csv("products.csv", ["product_id", "product_name", "product_name_zh", "category", "unit",
                               "unit_cost", "list_price"], PRODUCTS)

    # ---------------- 会员
    customers = []
    signup_start, signup_end = date(2024, 6, 1), date(2026, 9, 30)
    span = (signup_end - signup_start).days
    for cid in range(1, 801):
        signup = signup_start + timedelta(days=int(span * rng.random() ** 1.3))
        customers.append((cid, wchoice(rng, CITIES), signup.isoformat(), wchoice(rng, TIERS),
                          rng.randint(1950, 2006)))
    write_csv("customers.csv", ["customer_id", "city", "signup_date", "member_tier", "birth_year"],
              customers)
    dormant = set(rng.sample(range(1, 801), 60))  # 这些会员从不下单
    active = [c for c in customers if c[0] not in dormant]

    # ---------------- 每周传单促销（周四开始到下周三）
    promos = []
    promo_lookup: dict[tuple[int, date], dict[int, float]] = {}
    promo_id = 1
    d = START
    while d.weekday() != 3:
        d += timedelta(days=1)
    d -= timedelta(days=7)
    while d <= END:
        for s in STORES:
            for pid in rng.sample(pids, 5):
                pp = round(price[pid] * rng.uniform(0.6, 0.85), 2)
                start, end = d, d + timedelta(days=6)
                promos.append((promo_id, s[0], pid, start.isoformat(), end.isoformat(), pp))
                promo_id += 1
                for day in daterange(start, end):
                    promo_lookup.setdefault((s[0], day), {})[pid] = pp
        d += timedelta(days=7)
    write_csv("promotions.csv", ["promo_id", "store_id", "product_id", "start_date", "end_date",
                                 "promo_price"], promos)

    # ---------------- 订单与明细
    orders, items = [], []
    oid = 100000
    for day in daterange(START, END):
        wk = 1.45 if day.weekday() >= 5 else 1.0
        season = 1.3 if day.month == 12 else (0.9 if day.month in (2, 3) else 1.0)
        growth = 1 + 0.25 * (day - START).days / (END - START).days
        eligible = [c for c in active if c[2] <= day.isoformat()]
        weights = [TIER_FREQ[c[3]] for c in eligible]
        for s in STORES:
            if s[3] > day.isoformat():
                continue
            lam = 2.6 * s[4] * wk * season * growth
            n = sum(1 for _ in range(int(lam * 2)) if rng.random() < 0.5) + (rng.random() < lam % 1)
            for _ in range(n):
                oid += 1
                cust = rng.choices(eligible, weights=weights)[0][0] if eligible and rng.random() < 0.7 else None
                ts = datetime(day.year, day.month, day.day, rng.randint(8, 21), rng.randint(0, 59),
                              rng.randint(0, 59))
                channel = "线上自提" if rng.random() < 0.15 else "门店"
                orders.append((oid, cust if cust is not None else "", s[0], ts.isoformat(sep=" "),
                               wchoice(rng, PAYMENTS), channel))
                today_promos = promo_lookup.get((s[0], day), {})
                season_boost = SEASONAL.get(day.month, {})
                w = [(3.0 if p in today_promos else 1.0) * season_boost.get(p, 1) for p in pids]
                basket = set()
                for _ in range(rng.randint(1, 7)):
                    p = rng.choices(pids, weights=w)[0]
                    basket.add(p)
                    for a, b in BUNDLES:
                        if p == a and rng.random() < 0.45:
                            basket.add(b)
                line = 0
                for p in sorted(basket):
                    line += 1
                    qty = rng.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
                    up = today_promos.get(p, price[p])
                    disc = round(qty * up * 0.1, 2) if rng.random() < 0.05 else 0.0
                    items.append((oid, line, p, qty, up, disc))
                    if rng.random() < 0.008:  # 退货：同一订单里追加一行负数量
                        line += 1
                        items.append((oid, line, p, -1, up, 0.0))

    # 故意埋的数据质量问题
    for row in rng.sample(items, 15):
        items.append(row)  # 完全重复的行
    for k in range(3):
        o = rng.choice(orders)[0]
        items.append((o, 90 + k, 999, 1, 9.99, 0.0))  # 不存在的商品
    items.sort(key=lambda r: (r[0], r[1]))

    write_csv("orders.csv", ["order_id", "customer_id", "store_id", "order_ts", "payment_method",
                             "channel"], orders)
    write_csv("order_items.csv", ["order_id", "line_no", "product_id", "quantity", "unit_price",
                                  "discount"], items)

    # ---------------- App 行为日志（JSON Lines，半结构化）
    ev_rows = []
    ev_start = date(2026, 9, 1)
    for sid in range(1, 6001):
        day = ev_start + timedelta(days=rng.randint(0, 60))
        t = datetime(day.year, day.month, day.day, rng.randint(7, 23), rng.randint(0, 59), rng.randint(0, 59))
        cust = rng.choice(active)[0] if rng.random() < 0.75 else None
        device = {"os": rng.choice(["iOS", "iOS", "Android"]),
                  "app_version": rng.choice(["3.1.0", "3.2.0", "3.2.1"])}
        session = f"s{sid:05d}"

        def emit(kind, props):
            nonlocal t
            ev_rows.append({"session_id": session, "customer_id": cust,
                            "event_ts": t.isoformat(sep=" "), "event_type": kind,
                            "device": device, "properties": props})
            t += timedelta(seconds=rng.randint(5, 180))

        if rng.random() < 0.5:
            emit("search", {"keyword": rng.choice(SEARCH_WORDS)})
        viewed = rng.sample(pids, rng.randint(1, 5))
        for p in viewed:
            emit("view_product", {"product_id": p, "source": rng.choice(["home", "search", "flyer", "flyer"])})
        if rng.random() < 0.45:
            cart = [{"product_id": p, "qty": rng.randint(1, 3)} for p in viewed[: rng.randint(1, len(viewed))]]
            value = round(sum(price[c["product_id"]] * c["qty"] for c in cart), 2)
            emit("add_to_cart", {"items": cart, "cart_value": value})
            if rng.random() < 0.6:
                emit("checkout", {"cart_value": value})
                if rng.random() < 0.85:
                    emit("purchase", {"order_value": value, "payment": wchoice(rng, PAYMENTS)})
    with (OUT / "app_events.jsonl").open("w", encoding="utf-8") as fh:
        for r in ev_rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"stores={len(STORES)} products={len(PRODUCTS)} customers={len(customers)} "
          f"promotions={len(promos)} orders={len(orders)} order_items={len(items)} app_events={len(ev_rows)}")
    print(f"已写入 {OUT}")


if __name__ == "__main__":
    main()
