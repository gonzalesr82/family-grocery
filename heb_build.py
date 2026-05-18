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
    js_cats += "];"

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
    js_prods += "};"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>Family Grocery — H-E-B</title>
<link href="https://fonts.googleapis.com/css2?family=Nunito:wght@700;800;900&family=Nunito+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{{--red:#CC2529;--red-l:#fdf2f2;--red-d:#a01e21;--green:#2d9b5a;--green-l:#f0faf4;--bg:#f5f3f0;--card:#fff;--text:#1a1a1a;--muted:#6b6b6b;--faint:#b8b8b8;--border:rgba(0,0,0,.08);--r:16px;}}
*{{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent;}}
body{{font-family:'Nunito Sans',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overscroll-behavior:none;}}
.app{{max-width:480px;margin:0 auto;min-height:100vh;display:flex;flex-direction:column;}}
.hdr{{background:var(--red);color:#fff;padding:14px 16px 12px;display:flex;align-items:center;justify-content:space-between;flex-shrink:0;}}
.hdr-logo{{font-family:'Nunito',sans-serif;font-weight:900;font-size:18px;line-height:1;}}
.hdr-sub{{font-size:10px;opacity:.75;margin-top:1px;}}
.hdr-store{{font-size:10px;opacity:.85;text-align:right;line-height:1.5;}}
.scr{{display:none;flex:1;flex-direction:column;overflow:hidden;}}
.scr.on{{display:flex;}}
.who-body{{padding:16px;flex:1;overflow-y:auto;}}
.pg-title{{font-family:'Nunito',sans-serif;font-size:20px;font-weight:900;margin-bottom:3px;}}
.pg-sub{{font-size:13px;color:var(--muted);margin-bottom:18px;}}
.mem-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:18px;}}
.mem{{background:var(--card);border:2.5px solid transparent;border-radius:var(--r);padding:20px 10px 15px;text-align:center;cursor:pointer;transition:all .15s;}}
.mem:active{{transform:scale(.97);}}
.mem.sel{{border-color:var(--red);background:var(--red-l);}}
.mem-av{{font-size:32px;display:block;margin-bottom:8px;}}
.mem-name{{font-family:'Nunito',sans-serif;font-weight:900;font-size:16px;}}
.btn{{width:100%;padding:14px;border-radius:14px;font-family:'Nunito',sans-serif;font-size:15px;font-weight:800;cursor:pointer;border:none;transition:all .15s;}}
.btn:active{{transform:scale(.98);}}
.btn-red{{background:var(--red);color:#fff;}}
.btn-ghost{{background:transparent;border:2px solid var(--border);color:var(--muted);font-size:13px;padding:11px;}}
.btn-ghost:hover{{border-color:var(--red);color:var(--red);}}
.cat-body{{flex:1;overflow-y:auto;padding:14px;}}
.back{{display:flex;align-items:center;gap:4px;background:none;border:none;font-size:13px;color:var(--muted);cursor:pointer;margin-bottom:12px;padding:0;}}
.back:hover{{color:var(--red);}}
.cat-grid{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;}}
.cat-card{{background:var(--card);border-radius:14px;padding:14px 8px 11px;text-align:center;cursor:pointer;border:1.5px solid transparent;transition:all .15s;}}
.cat-card:hover{{border-color:rgba(204,37,41,.25);}}
.cat-card:active{{transform:scale(.97);}}
.cat-em{{font-size:26px;display:block;margin-bottom:5px;}}
.cat-nm{{font-family:'Nunito',sans-serif;font-weight:800;font-size:11px;line-height:1.2;}}
.cat-ct{{font-size:9px;color:var(--faint);margin-top:2px;}}
.nav{{display:flex;background:var(--card);border-top:1px solid var(--border);flex-shrink:0;}}
.nav-btn{{flex:1;padding:10px 8px 13px;display:flex;flex-direction:column;align-items:center;gap:3px;background:none;border:none;cursor:pointer;font-size:9px;font-family:'Nunito',sans-serif;font-weight:800;color:var(--faint);transition:color .15s;}}
.nav-btn.on{{color:var(--red);}}
.nav-btn svg{{width:21px;height:21px;}}
.bdg{{background:var(--red);color:#fff;font-size:8px;border-radius:20px;padding:1px 5px;min-width:15px;text-align:center;display:none;}}
.bdg.show{{display:block;}}
.backdrop{{position:fixed;inset:0;background:rgba(0,0,0,0);transition:background .3s;pointer-events:none;z-index:40;max-width:480px;margin:0 auto;}}
.backdrop.show{{background:rgba(0,0,0,.5);pointer-events:auto;}}
.sheet{{position:fixed;left:50%;transform:translateX(-50%) translateY(100%);bottom:0;width:100%;max-width:480px;background:var(--card);border-radius:22px 22px 0 0;transition:transform .35s cubic-bezier(.32,.72,0,1);z-index:50;display:flex;flex-direction:column;height:85vh;}}
.sheet.open{{transform:translateX(-50%) translateY(0);}}
.sheet-handle{{width:38px;height:4px;background:var(--border);border-radius:2px;margin:10px auto 0;flex-shrink:0;}}
.sheet-hdr{{padding:12px 16px 10px;display:flex;align-items:center;justify-content:space-between;border-bottom:0.5px solid var(--border);flex-shrink:0;}}
.sheet-title{{font-family:'Nunito',sans-serif;font-weight:900;font-size:16px;}}
.sheet-close{{background:var(--bg);border:none;border-radius:50%;width:28px;height:28px;cursor:pointer;font-size:14px;color:var(--muted);display:flex;align-items:center;justify-content:center;}}
.brand-row{{padding:8px 14px 6px;border-bottom:0.5px solid var(--border);flex-shrink:0;}}
.brand-scroll{{display:flex;gap:6px;overflow-x:auto;padding-bottom:2px;}}
.brand-scroll::-webkit-scrollbar{{display:none;}}
.bpill{{background:var(--bg);border:1.5px solid var(--border);border-radius:20px;padding:5px 12px;font-size:11px;font-weight:700;color:var(--muted);cursor:pointer;white-space:nowrap;transition:all .15s;flex-shrink:0;font-family:'Nunito',sans-serif;}}
.bpill.on{{background:var(--red);color:#fff;border-color:var(--red);}}
.sheet-search-row{{padding:8px 14px;border-bottom:0.5px solid var(--border);flex-shrink:0;display:flex;gap:8px;}}
.sheet-search{{flex:1;padding:8px 12px;border-radius:10px;border:1.5px solid var(--border);font-size:13px;background:var(--bg);outline:none;}}
.sheet-search:focus{{border-color:var(--red);}}
.custom-row{{padding:8px 14px;border-bottom:0.5px solid var(--border);flex-shrink:0;}}
.custom-inner{{display:flex;gap:8px;align-items:center;background:var(--bg);border-radius:10px;padding:8px 12px;border:1.5px dashed var(--border);}}
.custom-input{{flex:1;background:transparent;border:none;outline:none;font-size:13px;color:var(--text);}}
.custom-input::placeholder{{color:var(--faint);}}
.custom-btn{{background:var(--red);color:#fff;border:none;border-radius:8px;padding:6px 11px;font-size:11px;font-weight:700;cursor:pointer;white-space:nowrap;font-family:'Nunito',sans-serif;}}
.sheet-body{{flex:1;overflow-y:auto;padding:10px 14px 20px;}}
.prod-count{{font-size:11px;color:var(--faint);margin-bottom:8px;}}
.prod-list{{display:flex;flex-direction:column;gap:7px;}}
.prod{{display:flex;align-items:center;gap:10px;background:var(--bg);border-radius:12px;padding:10px 11px;border:1.5px solid transparent;transition:all .15s;}}
.prod:hover{{border-color:rgba(204,37,41,.25);}}
.prod.added{{border-color:var(--green);background:var(--green-l);}}
.prod-img{{width:48px;height:48px;border-radius:8px;object-fit:contain;flex-shrink:0;background:var(--card);}}
.prod-ph{{width:48px;height:48px;border-radius:8px;background:var(--card);display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}}
.prod-info{{flex:1;min-width:0;}}
.prod-brand{{font-size:10px;color:var(--muted);}}
.prod-name{{font-size:12px;font-weight:700;color:var(--text);line-height:1.3;}}
.prod-price{{font-size:12px;font-weight:700;color:var(--red);margin-top:2px;}}
.add-btn{{background:var(--red);color:#fff;border:none;border-radius:9px;padding:7px 11px;font-size:11px;font-weight:700;cursor:pointer;flex-shrink:0;transition:all .15s;font-family:'Nunito',sans-serif;}}
.add-btn:active{{transform:scale(.95);}}
.prod.added .add-btn{{background:var(--green);}}
.no-results{{text-align:center;padding:30px 0;color:var(--faint);font-size:13px;}}
.list-body{{flex:1;overflow-y:auto;padding:14px;}}
.stats{{display:flex;gap:8px;margin-bottom:14px;}}
.stat{{flex:1;background:var(--card);border-radius:12px;padding:10px;text-align:center;}}
.stat-n{{font-family:'Nunito',sans-serif;font-weight:900;font-size:22px;}}
.stat-l{{font-size:10px;color:var(--muted);}}
.person-blk{{margin-bottom:14px;}}
.person-hd{{display:flex;align-items:center;gap:7px;margin-bottom:7px;}}
.person-hd span{{font-family:'Nunito',sans-serif;font-weight:900;font-size:14px;}}
.list-row{{display:flex;align-items:center;gap:9px;background:var(--card);border-radius:11px;padding:10px 12px;margin-bottom:6px;border:1.5px solid transparent;transition:border .15s;cursor:pointer;}}
.list-row:hover{{border-color:rgba(204,37,41,.25);}}
.list-row.done .lname{{text-decoration:line-through;color:var(--faint);}}
.lname{{font-size:13px;font-weight:600;flex:1;}}
.lprice{{font-size:11px;color:var(--muted);margin-right:4px;}}
.heb-pill{{font-size:10px;font-weight:700;color:var(--red);background:var(--red-l);padding:3px 9px;border-radius:20px;text-decoration:none;white-space:nowrap;flex-shrink:0;font-family:'Nunito',sans-serif;}}
.heb-pill:hover{{background:var(--red);color:#fff;}}
.rm-btn{{background:none;border:none;color:var(--faint);cursor:pointer;font-size:15px;padding:0 2px;flex-shrink:0;}}
.rm-btn:hover{{color:var(--red);}}
.empty-list{{text-align:center;padding:50px 20px;color:var(--muted);}}
.empty-list .big{{font-size:48px;margin-bottom:10px;}}
.list-actions{{display:flex;flex-direction:column;gap:8px;margin-top:16px;}}
.copy-ok{{background:var(--green-l);color:var(--green);border-radius:10px;padding:10px;font-size:13px;font-weight:700;text-align:center;display:none;margin-top:6px;}}
.toast{{position:fixed;bottom:80px;left:50%;transform:translateX(-50%) translateY(8px);background:#1a1a1a;color:#fff;font-size:12px;font-weight:700;padding:8px 16px;border-radius:20px;opacity:0;transition:all .25s;pointer-events:none;white-space:nowrap;z-index:100;}}
.toast.show{{opacity:1;transform:translateX(-50%) translateY(0);}}
</style>
</head>
<body>
<div class="app">
  <div class="hdr">
    <div><div class="hdr-logo">🛒 Family List</div><div class="hdr-sub">H‑E‑B Grocery</div></div>
    <div class="hdr-store">📍 Bandera &amp; 1604<br>San Antonio, TX</div>
  </div>
  <div class="scr on" id="s-who">
    <div class="who-body">
      <div class="pg-title">Hey! Who are you? 👋</div>
      <div class="pg-sub">Tap your name to add what you want this week</div>
      <div class="mem-grid">
        <div class="mem" onclick="pickWho('mom','👩','Mom')" id="c-mom"><span class="mem-av">👩</span><div class="mem-name">Mom</div></div>
        <div class="mem" onclick="pickWho('dad','👨','Dad')" id="c-dad"><span class="mem-av">👨</span><div class="mem-name">Dad</div></div>
        <div class="mem" onclick="pickWho('rory','🧒','Rory')" id="c-rory"><span class="mem-av">🧒</span><div class="mem-name">Rory</div></div>
        <div class="mem" onclick="pickWho('rowan','👦','Rowan')" id="c-rowan"><span class="mem-av">👦</span><div class="mem-name">Rowan</div></div>
      </div>
      <button class="btn btn-red" onclick="goCats()">Let's go! →</button>
    </div>
  </div>
  <div class="scr" id="s-cats">
    <div class="cat-body">
      <button class="back" onclick="show('s-who')">← Back</button>
      <div class="pg-title" id="cats-title">What do you want?</div>
      <div class="pg-sub" style="margin-bottom:14px">Tap a category to browse</div>
      <div class="cat-grid" id="cat-grid"></div>
    </div>
  </div>
  <div class="scr" id="s-list">
    <div class="list-body">
      <div class="stats">
        <div class="stat"><div class="stat-n" id="st-tot">0</div><div class="stat-l">Items</div></div>
        <div class="stat"><div class="stat-n" id="st-ppl">0</div><div class="stat-l">People</div></div>
        <div class="stat"><div class="stat-n" id="st-dn">0</div><div class="stat-l">In cart</div></div>
      </div>
      <div id="list-body"></div>
      <div class="list-actions">
        <button class="btn btn-red" onclick="openAll()">Open all on H‑E‑B 🛒</button>
        <button class="btn btn-ghost" onclick="copyList()">Copy list as text</button>
        <button class="btn btn-ghost" style="color:var(--red);border-color:var(--red)" onclick="resetList()">Clear this week's list</button>
      </div>
      <div class="copy-ok" id="copy-ok">✓ Copied!</div>
    </div>
  </div>
  <div class="nav">
    <button class="nav-btn on" id="n-add" onclick="navTo('add')">
      <svg fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/></svg>Add Items
    </button>
    <button class="nav-btn" id="n-list" onclick="navTo('list')">
      <svg fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/></svg>Our List
      <div class="bdg" id="bdg">0</div>
    </button>
  </div>
</div>
<div class="backdrop" id="backdrop" onclick="closeSheet()"></div>
<div class="sheet" id="sheet">
  <div class="sheet-handle"></div>
  <div class="sheet-hdr">
    <div class="sheet-title" id="sheet-title">Products</div>
    <button class="sheet-close" onclick="closeSheet()">✕</button>
  </div>
  <div class="brand-row"><div class="brand-scroll" id="brand-scroll"></div></div>
  <div class="sheet-search-row">
    <input class="sheet-search" id="sheet-search" placeholder="Search within this category..." oninput="filterProds()">
  </div>
  <div class="custom-row">
    <div class="custom-inner">
      <input class="custom-input" id="custom-input" placeholder="Not listed? Type it here and add...">
      <button class="custom-btn" onclick="addCustom()">+ Add</button>
    </div>
  </div>
  <div class="sheet-body">
    <div class="prod-count" id="prod-count"></div>
    <div class="prod-list" id="prod-list"></div>
  </div>
</div>
<div class="toast" id="toast"></div>
<script>
const STORE=623;
{js_cats}
{js_prods}
const MEMBERS={{mom:{{n:'Mom',e:'👩'}},dad:{{n:'Dad',e:'👨'}},rory:{{n:'Rory',e:'🧒'}},rowan:{{n:'Rowan',e:'👦'}}}};
let who=null,curCatId=null,activeBrand='All',picks={{}},checked={{}};
function load(){{try{{const d=JSON.parse(localStorage.getItem('heb-v6')||'{{}}');picks=d.p||{{}};checked=d.c||{{}}}}catch(e){{}}}}
function save(){{try{{localStorage.setItem('heb-v6',JSON.stringify({{p:picks,c:checked}}))}}catch(e){{}}}}
load();buildCatGrid();refreshBadge();
function buildCatGrid(){{
  document.getElementById('cat-grid').innerHTML=CATS.map(c=>
    `<div class="cat-card" onclick="openSheet('${{c.id}}')"><span class="cat-em">${{c.em}}</span><div class="cat-nm">${{c.nm}}</div><div class="cat-ct">${{c.count}} items</div></div>`
  ).join('');
}}
function show(id){{document.querySelectorAll('.scr').forEach(s=>s.classList.remove('on'));document.getElementById(id).classList.add('on');}}
function navTo(t){{
  document.querySelectorAll('.nav-btn').forEach(b=>b.classList.remove('on'));
  if(t==='add'){{document.getElementById('n-add').classList.add('on');show('s-cats');}}
  else{{document.getElementById('n-list').classList.add('on');renderList();show('s-list');}}
}}
function pickWho(id,em,nm){{who={{id,em,nm}};document.querySelectorAll('.mem').forEach(c=>c.classList.remove('sel'));document.getElementById('c-'+id).classList.add('sel');}}
function goCats(){{if(!who){{alert('Tap your name first!');return;}}document.getElementById('cats-title').textContent='Hi '+who.nm+'! What do you want? '+who.em;show('s-cats');}}
function openSheet(catId){{
  curCatId=catId;activeBrand='All';
  const cat=CATS.find(c=>c.id===catId);
  document.getElementById('sheet-title').textContent=cat.em+' '+cat.nm;
  document.getElementById('sheet-search').value='';
  document.getElementById('custom-input').value='';
  buildBrands();renderProds();
  document.getElementById('backdrop').classList.add('show');
  document.getElementById('sheet').classList.add('open');
}}
function closeSheet(){{document.getElementById('backdrop').classList.remove('show');document.getElementById('sheet').classList.remove('open');}}
function buildBrands(){{
  const prods=PRODUCTS[curCatId]||[];
  const brands=['All',...new Set(prods.map(p=>p.b).filter(Boolean))];
  document.getElementById('brand-scroll').innerHTML=brands.map(b=>
    `<div class="bpill${{b===activeBrand?' on':''}}" onclick="setBrand(this.textContent)">${{b}}</div>`
  ).join('');
}}
function setBrand(b){{activeBrand=b;document.querySelectorAll('.bpill').forEach(el=>el.classList.toggle('on',el.textContent===b));renderProds();}}
function filterProds(){{renderProds();}}
function renderProds(){{
  const q=(document.getElementById('sheet-search').value||'').toLowerCase();
  const all=PRODUCTS[curCatId]||[];
  const addedNames=(picks[who?.id]||[]).map(p=>p.n);
  let list=activeBrand==='All'?all:all.filter(p=>p.b===activeBrand);
  if(q)list=list.filter(p=>(p.n+' '+p.b).toLowerCase().includes(q));
  document.getElementById('prod-count').textContent=list.length+' products';
  if(!list.length){{document.getElementById('prod-list').innerHTML='<div class="no-results">No products found — use the field above to add manually</div>';return;}}
  document.getElementById('prod-list').innerHTML=list.map(p=>{{
    const added=addedNames.includes(p.n);
    const imgEl=p.img?`<img class="prod-img" src="${{p.img}}" loading="lazy" onerror="this.style.display='none'">`:`<div class="prod-ph">🛒</div>`;
    return `<div class="prod${{added?' added':''}}">
      ${{imgEl}}
      <div class="prod-info">
        ${{p.b?`<div class="prod-brand">${{p.b}}</div>`:''}}
        <div class="prod-name">${{p.n}}</div>
        <div class="prod-price">${{p.p}}${{p.uom?' / '+p.uom:''}}</div>
      </div>
      <button class="add-btn" onclick="addProd(this)"
        data-n="${{p.n.replace(/"/g,'&quot;')}}"
        data-b="${{(p.b||'').replace(/"/g,'&quot;')}}"
        data-p="${{p.p}}"
        data-url="${{p.url}}"
      >${{added?'✓ Added':'+ Add'}}</button>
    </div>`;
  }}).join('');
}}
function addProd(btn){{
  if(!who){{alert('Go back and tap your name first!');return;}}
  const name=btn.dataset.n,brand=btn.dataset.b,price=btn.dataset.p,url=btn.dataset.url;
  if(!picks[who.id])picks[who.id]=[];
  if(!picks[who.id].find(p=>p.n===name)){{
    picks[who.id].push({{n:name,b:brand,p:price,url:url}});
    save();refreshBadge();renderProds();showToast('✓ Added to list!');
  }}
}}
function addCustom(){{
  if(!who){{alert('Go back and tap your name first!');return;}}
  const val=document.getElementById('custom-input').value.trim();
  if(!val)return;
  if(!picks[who.id])picks[who.id]=[];
  if(!picks[who.id].find(p=>p.n===val)){{
    picks[who.id].push({{n:val,b:'',p:'',url:`https://www.heb.com/search?q=${{encodeURIComponent(val)}}&store=${{STORE}}`}});
    save();refreshBadge();showToast('✓ '+val+' added!');
  }}
  document.getElementById('custom-input').value='';
}}
function refreshBadge(){{
  const t=Object.values(picks).reduce((s,a)=>s+(a||[]).length,0);
  const b=document.getElementById('bdg');b.textContent=t;b.classList.toggle('show',t>0);
}}
function renderList(){{
  const body=document.getElementById('list-body');
  const all=[];Object.entries(picks).forEach(([mid,items])=>(items||[]).forEach(i=>all.push({{...i,mid}})));
  const ppl=Object.keys(picks).filter(k=>(picks[k]||[]).length>0).length;
  const dn=Object.values(checked).filter(Boolean).length;
  document.getElementById('st-tot').textContent=all.length;
  document.getElementById('st-ppl').textContent=ppl;
  document.getElementById('st-dn').textContent=dn;
  if(!all.length){{body.innerHTML='<div class="empty-list"><div class="big">🛒</div><p>Nothing yet!<br>Have the family tap <strong>Add Items</strong> to get started.</p></div>';return;}}
  let html='';
  Object.entries(picks).forEach(([mid,items])=>{{
    if(!items||!items.length)return;
    const m=MEMBERS[mid];
    html+=`<div class="person-blk"><div class="person-hd"><span>${{m.e}}</span><span>${{m.n}}'s picks</span></div>`;
    items.forEach(item=>{{
      const key=item.n+'|'+mid;const done=checked[key];
      html+=`<div class="list-row${{done?' done':''}}" onclick="toggleDone('${{key.replace(/'/g,"\\'")}}')">
        <span style="font-size:18px">🛒</span>
        <span class="lname">${{item.n}}</span>
        ${{item.p?`<span class="lprice">${{item.p}}</span>`:''}}
        <a class="heb-pill" href="${{item.url}}" target="_blank" rel="noopener" onclick="event.stopPropagation()">HEB →</a>
        <button class="rm-btn" onclick="event.stopPropagation();removeItem('${{mid}}','${{item.n.replace(/'/g,"\\'")}}')">✕</button>
      </div>`;
    }});
    html+='</div>';
  }});
  body.innerHTML=html;
}}
function toggleDone(key){{checked[key]=!checked[key];save();renderList();}}
function removeItem(mid,name){{if(!picks[mid])return;picks[mid]=picks[mid].filter(p=>p.n!==name);save();refreshBadge();renderList();}}
function openAll(){{
  const all=[];Object.values(picks).forEach(items=>(items||[]).forEach(i=>all.push(i)));
  if(!all.length){{alert('No items yet!');return;}}
  all.slice(0,5).forEach(i=>window.open(i.url,'_blank'));
  if(all.length>5)alert('Opened first 5 on HEB.\\nTap HEB → next to each item for the rest.');
}}
function copyList(){{
  const mmap={{mom:'Mom',dad:'Dad',rory:'Rory',rowan:'Rowan'}};
  let txt='Family Grocery List — H-E-B (Bandera & 1604)\\n\\n';
  Object.entries(picks).forEach(([mid,items])=>{{
    if(!items||!items.length)return;
    txt+=mmap[mid]+':\\n';items.forEach(i=>txt+='  '+i.n+(i.p?' — '+i.p:'')+'\\n');txt+='\\n';
  }});
  navigator.clipboard.writeText(txt).then(()=>{{
    const el=document.getElementById('copy-ok');el.style.display='block';setTimeout(()=>el.style.display='none',2500);
  }});
}}
function resetList(){{if(confirm("Clear everyone's picks?")){{picks={{}};checked={{}};save();refreshBadge();renderList();}}}}
function showToast(msg){{const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),2000);}}
</script>
</body>
</html>"""

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
