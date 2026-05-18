#!/usr/bin/env python3
"""
HEB Family Grocery App Builder — GitHub Actions version
Pulls real product data from HEB's GraphQL API and builds index.html
Store #623: Bandera & 1604, San Antonio TX
"""
import requests, json, time, sys

STORE_ID = 623
GRAPHQL  = "https://www.heb.com/graphql"
LIMIT    = 100
DELAY    = 0.4
OUTPUT   = "index.html"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.heb.com/",
    "Origin": "https://www.heb.com",
}

QUERY = """
query Browse($categoryId:String!,$storeId:Int!,$offset:Int!,$limit:Int!){
  browseCategory(categoryId:$categoryId storeId:$storeId shoppingContext:CURBSIDE_PICKUP offset:$offset limit:$limit){
    totalCount
    records{
      id displayName brand unitOfMeasure
      productImageUrls{ url }
      price{ value unitOfMeasure }
    }
  }
}"""

CATEGORIES = [
    ("490589","🥔","Chips & Crisps"),
    ("490590","🌽","Tortilla Chips"),
    ("490591","🍿","Popcorn"),
    ("490592","🫙","Crackers"),
    ("490593","🥨","Pretzels & Puffs"),
    ("490600","🍬","Candy & Chocolate"),
    ("490601","🍪","Cookies"),
    ("490700","🍨","Ice Cream"),
    ("490701","🧊","Frozen Meals"),
    ("490702","🍕","Frozen Pizza"),
    ("490703","🍗","Frozen Chicken"),
    ("490200","🥣","Cereal & Breakfast"),
    ("490201","🧇","Waffles & Pastries"),
    ("490100","🍞","Bread & Rolls"),
    ("490101","🫓","Tortillas"),
    ("490800","🥛","Milk & Cream"),
    ("490801","🧀","Cheese"),
    ("490802","🥚","Eggs"),
    ("490803","🧈","Butter"),
    ("490804","🍦","Yogurt"),
    ("490300","🍗","Chicken"),
    ("490301","🥩","Beef & Steak"),
    ("490302","🥩","Pork"),
    ("490303","🥓","Bacon & Sausage"),
    ("490304","🌭","Hot Dogs"),
    ("490305","🐟","Seafood"),
    ("490306","🦃","Turkey"),
    ("490400","🥪","Deli Meats"),
    ("490401","🧀","Deli Cheese"),
    ("490500","🥦","Fresh Vegetables"),
    ("490501","🥬","Salads & Greens"),
    ("490502","🍎","Fresh Fruit"),
    ("490503","🍊","Citrus & Tropical"),
    ("490010","🥤","Sodas"),
    ("490011","💧","Water & Sparkling"),
    ("490012","🍊","Juice"),
    ("490013","☕","Coffee"),
    ("490014","🍵","Tea"),
    ("490015","⚡","Sports & Energy"),
    ("490020","🍝","Pasta & Noodles"),
    ("490021","🍅","Pasta Sauce"),
    ("490022","🧀","Mac & Cheese"),
    ("490030","🥫","Canned Soup"),
    ("490031","🥫","Canned Vegetables"),
    ("490032","🥫","Canned Beans"),
    ("490033","🥫","Canned Tomatoes"),
    ("490034","🐟","Canned Tuna"),
    ("490040","🍚","Rice"),
    ("490041","🫘","Dried Beans"),
    ("490042","🌾","Grains & Oats"),
    ("490050","🍅","Ketchup & Mustard"),
    ("490051","🫙","Mayo & Dressings"),
    ("490052","🌶️","Hot Sauce & Salsa"),
    ("490053","🍖","BBQ Sauce"),
    ("490060","🧂","Salt & Spices"),
    ("490061","🫙","Baking"),
    ("490070","🫒","Oils & Vinegar"),
    ("490080","🍫","Snack & Granola Bars"),
    ("490081","🥜","Nuts & Peanut Butter"),
    ("490090","📦","Lunchables & Kids"),
    ("490091","🧃","Kids Juice"),
    ("490092","🍬","Fruit Snacks"),
    ("490150","🧻","Toilet Paper & Tissues"),
    ("490151","🧻","Paper Towels"),
    ("490152","🛍️","Bags & Foil"),
    ("490153","🗑️","Trash Bags"),
    ("490154","🫧","Dish Soap"),
    ("490155","🧹","Cleaners"),
    ("490160","🧺","Laundry Detergent"),
    ("490161","🧺","Fabric Softener"),
    ("490170","🧼","Body Wash & Soap"),
    ("490171","🫧","Hand Soap"),
    ("490172","🧴","Lotion"),
    ("490173","☀️","Sunscreen"),
    ("490180","💆","Shampoo"),
    ("490181","💆","Conditioner"),
    ("490190","🪥","Toothpaste"),
    ("490191","🫧","Mouthwash"),
    ("490200","💊","Pain Relief"),
    ("490201","💊","Cold & Flu"),
    ("490202","💊","Allergy"),
    ("490203","🩹","First Aid"),
    ("490210","🍼","Diapers"),
    ("490211","🧻","Baby Wipes"),
    ("490212","🥣","Baby Food"),
    ("490213","🍼","Baby Formula"),
    ("490220","🐾","Dog Food"),
    ("490221","🐾","Cat Food"),
    ("490222","🐾","Pet Treats"),
]

def fetch_page(cat_id, offset):
    try:
        r = requests.post(GRAPHQL, json={
            "query": QUERY,
            "variables": {"categoryId": cat_id, "storeId": STORE_ID, "offset": offset, "limit": LIMIT}
        }, headers=HEADERS, timeout=20)
        r.raise_for_status()
        d = r.json()
        result = d.get("data", {}).get("browseCategory", {})
        return result.get("records", []), result.get("totalCount", 0)
    except Exception as ex:
        print(f"  Warning: {ex}", file=sys.stderr)
        return [], 0

def fetch_all(cat_id, max_items=300):
    items, offset = [], 0
    while True:
        page, total = fetch_page(cat_id, offset)
        if not page: break
        items.extend(page)
        offset += len(page)
        if offset >= total or offset >= max_items: break
        time.sleep(DELAY)
    return items

def clean(p):
    name  = (p.get("displayName") or "").strip()
    brand = (p.get("brand") or "").strip()
    imgs  = p.get("productImageUrls") or []
    img   = imgs[0].get("url", "") if imgs else ""
    pr    = (p.get("price") or {}).get("value")
    uom   = (p.get("price") or {}).get("unitOfMeasure") or p.get("unitOfMeasure") or ""
    pid   = p.get("id") or ""
    url   = f"https://www.heb.com/product-detail/{pid}" if pid else \
            f"https://www.heb.com/search?q={requests.utils.quote(name)}&store={STORE_ID}"
    return {"name": name, "brand": brand, "img": img,
            "price": f"${pr:.2f}" if pr else "", "uom": uom, "url": url}

def js_str(s):
    return s.replace("\\","\\\\").replace("'","\\'").replace("\n"," ")

def build_html(cat_data):
    js_cats = "const CATS=[\n"
    for cid, em, nm, prods in cat_data:
        js_cats += f"  {{id:'{cid}',em:'{em}',nm:'{js_str(nm)}',count:{len(prods)}}},\n"
    js_cats += "];\n"

    js_prods = "const PRODUCTS={\n"
    for cid, em, nm, prods in cat_data:
        js_prods += f"  '{cid}':[\n"
        for p in prods:
            js_prods += (
                f"    {{n:'{js_str(p['name'])}',b:'{js_str(p['brand'])}',"
                f"img:'{p['img']}',p:'{p['price']}',uom:'{p['uom']}',"
                f"url:'{p['url']}'}},\n"
            )
        js_prods += "  ],\n"
    js_prods += "};\n"

    with open("template.html", "r", encoding="utf-8") as f:
        tmpl = f.read()

    return tmpl.replace("%%CATS%%", js_cats).replace("%%PRODUCTS%%", js_prods)

def main():
    print(f"Building HEB Family Grocery App — Store #{STORE_ID}")
    cat_data = []
    total = 0
    for cid, em, nm in CATEGORIES:
        print(f"  {em} {nm}...", end=" ", flush=True)
        raw = fetch_all(cid)
        cleaned = []
        seen = set()
        for p in raw:
            c = clean(p)
            if c["name"] and c["name"] not in seen:
                seen.add(c["name"])
                cleaned.append(c)
        print(f"{len(cleaned)} products")
        cat_data.append((cid, em, nm, cleaned))
        total += len(cleaned)
        time.sleep(DELAY)
    print(f"\nTotal: {total} products across {len(cat_data)} categories")
    print("Building HTML...", end=" ", flush=True)
    html = build_html(cat_data)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(html)
    import os
    print(f"Done! {os.path.getsize(OUTPUT)//1024} KB")

if __name__ == "__main__":
    main()
