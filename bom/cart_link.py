"""
Build the one-click Amazon cart link from bom.csv, and write it into the
README between the CART-LINK markers.

Uses Amazon's multi-item add-to-cart URL
(https://www.amazon.com/gp/aws/cart/add.html?ASIN.1=...&Quantity.1=...).
No affiliate/Associates tag is added, on purpose: this BOM earns nothing.

Every row with cart_qty > 0 must have an https://www.amazon.com/dp/<ASIN>
URL; anything else fails loudly rather than silently dropping a part.

    python3 bom/cart_link.py          # print the link and update README.md
"""
import csv
import os
import re
import sys
from urllib.parse import urlencode

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "..", "README.md")
BEGIN, END = "<!-- CART-LINK:BEGIN -->", "<!-- CART-LINK:END -->"
ASIN_URL = re.compile(r"^https://www\.amazon\.com/dp/([A-Z0-9]{10})/?$")


def cart_items(path=os.path.join(HERE, "bom.csv")):
    items = []
    for row in csv.DictReader(open(path, newline="")):
        qty = int(row["cart_qty"] or 0)
        if qty <= 0:
            continue
        m = ASIN_URL.match(row["amazon_url"].strip())
        if not m:
            sys.exit(f"line {row['line']} ({row['part']}): cart_qty={qty} but no plain amazon.com/dp/<ASIN> URL")
        items.append((m.group(1), qty, row["part"]))
    return items


def cart_url(items):
    params = {}
    for n, (asin, qty, _) in enumerate(items, 1):
        params[f"ASIN.{n}"] = asin
        params[f"Quantity.{n}"] = qty
    return "https://www.amazon.com/gp/aws/cart/add.html?" + urlencode(params)


def main():
    items = cart_items()
    url = cart_url(items)
    assert "tag=" not in url.lower() and "associatetag" not in url.lower()
    block = (f"{BEGIN}\n**[Add the full BOM to your Amazon cart]({url})** "
             f"({len(items)} listings, {sum(q for _, q, _ in items)} items)\n{END}")
    text = open(README).read()
    if BEGIN in text:
        text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    else:
        sys.exit("README.md has no CART-LINK markers; add them where the button should go")
    open(README, "w").write(text)
    for asin, qty, part in items:
        print(f"  {qty} x {asin}  {part}")
    print(url)


if __name__ == "__main__":
    main()
