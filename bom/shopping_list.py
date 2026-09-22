"""
Write the README's shopping list from bom.csv, between the SHOPPING-LIST
markers, so the list can never drift from the BOM.

One row per listing to buy (cart_qty > 0): the part, how many to add to your
cart, the per-build cost, and a direct link to the checked Amazon listing.
Links carry no affiliate tag, on purpose.

(Amazon's multi-item add-to-cart URL, /gp/aws/cart/add.html, was tested
2026-09-21 and no longer adds items, so there is no one-click button.)

    python3 bom/shopping_list.py
"""
import csv
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "..", "README.md")
BEGIN, END = "<!-- SHOPPING-LIST:BEGIN -->", "<!-- SHOPPING-LIST:END -->"
ASIN_URL = re.compile(r"^https://www\.amazon\.com/dp/([A-Z0-9]{10})/?$")


def rows(path=os.path.join(HERE, "bom.csv")):
    out = []
    for r in csv.DictReader(open(path, newline="")):
        qty = int(r["cart_qty"] or 0)
        if qty <= 0:
            continue
        url = r["amazon_url"].strip()
        if not ASIN_URL.match(url):
            sys.exit(f"line {r['line']} ({r['part']}): cart_qty={qty} but no plain amazon.com/dp/<ASIN> URL")
        if "tag=" in url.lower():
            sys.exit(f"line {r['line']}: affiliate tag in URL; this BOM carries none")
        out.append(r)
    return out


def table(items):
    lines = ["| Part | Buy | Per build | Listing |", "|---|---|---|---|"]
    for r in items:
        cost = f"${float(r['per_build_usd']):.2f}" if r["per_build_usd"] else ""
        part = r["part"].replace("|", "/")
        lines.append(f"| {part} | {r['cart_qty']} | {cost} | [Amazon]({r['amazon_url']}) |")
    return "\n".join(lines)


def main():
    items = rows()
    block = f"{BEGIN}\n{table(items)}\n{END}"
    text = open(README).read()
    if BEGIN not in text:
        sys.exit("README.md has no SHOPPING-LIST markers; add them where the list should go")
    text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    open(README, "w").write(text)
    print(f"{len(items)} listings, {sum(int(r['cart_qty']) for r in items)} items written to README.md")


if __name__ == "__main__":
    main()
