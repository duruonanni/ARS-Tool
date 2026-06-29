"""
Lenovo Spec Lookup – Local Helper Server
========================================
Run once:  python3 lenovo_spec_server.py
Listens on http://localhost:9527

The ALM→ARS Converter will automatically call this server to fetch
Lenovo product specs. Python has no CORS restrictions and can send
the browser-style headers that Lenovo's Akamai WAF expects.

API:
  GET /spec?sn=PW016STT          → JSON spec for one SN
  GET /spec?sn=SN1&sn=SN2&...   → batch (tries each until one succeeds)
  GET /health                    → {"ok": true}
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

PORT = int(os.environ.get("PORT", "9527"))

# ---------------------------------------------------------------------------
# Lenovo query logic
# ---------------------------------------------------------------------------

HEADERS_JSON = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://pcsupport.lenovo.com/",
}

HEADERS_HTML = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
}


def fetch(url, headers, timeout=15):
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            # Handle gzip transparently (urllib does it automatically for gzip)
            enc = r.headers.get("Content-Encoding", "")
            if enc == "gzip":
                import gzip
                raw = gzip.decompress(raw)
            return raw.decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {url}")
        return None
    except Exception as e:
        print(f"  Error: {e}: {url}")
        return None


def html_table_to_dict(html):
    """Extract <td>Label</td><td>Value</td> pairs → {label: value}"""
    table = {}
    for m in re.finditer(
        r"<td[^>]*>\s*([^<]+?)\s*</td>\s*<td[^>]*>\s*([^<]*?)\s*</td>",
        html, re.IGNORECASE
    ):
        table[m.group(1).strip().lower()] = m.group(2).strip()
    return table


def parse_spec_from_html(html, product_name=""):
    """Extract spec fields from product page HTML."""
    # Primary: window.config.product.Specification (JSON-escaped HTML table)
    m = re.search(r'"Specification"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
    if m:
        raw = (
            m.group(1)
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace('\\"', '"')
            .replace("\\\\", "\\")
        )
        table = html_table_to_dict(raw)
        if table:
            return build_spec(table, product_name)
    return None


def build_spec(table, product_name=""):
    """Map raw table dict → normalised spec dict."""
    spec = {}

    proc = table.get("processor") or table.get("cpu") or ""
    if proc and proc not in ("1x ", "1x"):
        # Strip trailing parenthetical e.g. "...i5-1135G7 Processor(Core™ i5-1135G7)"
        proc = re.sub(r'\s+\w+\([^)]+\)\s*$', '', proc).strip()
        spec["processor"] = proc
        m = re.match(r"^(\d+)x", proc, re.IGNORECASE)
        spec["procQty"] = int(m.group(1)) if m else 1

    mem = table.get("memory") or table.get("ram") or ""
    if mem and mem not in ("1x ", "1x"):
        spec["memory"] = mem
        m = re.match(r"^(\d+)x", mem, re.IGNORECASE)
        spec["memQty"] = int(m.group(1)) if m else 1

    drv = (
        table.get("hard drive") or table.get("storage")
        or table.get("ssd") or table.get("hdd") or ""
    )
    if drv:
        if "NVMe" in drv or "PCIe" in drv:
            spec["driveType"] = "SSD PCIe NVMe"
        elif "SSD" in drv and "SATA" in drv:
            spec["driveType"] = "SSD SATA"
        elif "SSD" in drv:
            spec["driveType"] = "SSD"
        elif "HDD" in drv or re.search(r"\d+RPM", drv):
            spec["driveType"] = "HDD"
        else:
            spec["driveType"] = "SSD"
        sm = re.search(r"(\d+)\s*(GB|TB)", drv, re.IGNORECASE)
        if sm:
            spec["driveSize"] = sm.group(1) + sm.group(2).upper()
        qm = re.match(r"^(\d+)x", drv, re.IGNORECASE)
        spec["driveQty"] = int(qm.group(1)) if qm else 1

    gpu = table.get("graphics") or table.get("gpu") or ""
    if gpu and gpu not in ("1x ", "1x"):
        spec["gpu"] = gpu
        m = re.match(r"^(\d+)x", gpu, re.IGNORECASE)
        spec["gpuQty"] = int(m.group(1)) if m else 1

    # Year from product name
    ym = re.search(r"Gen\s*(\d+)", product_name, re.IGNORECASE)
    if ym:
        spec["year"] = str(2019 + int(ym.group(1)))
    else:
        ym2 = re.search(r"20(\d{2})", product_name)
        if ym2:
            spec["year"] = "20" + ym2.group(1)

    return spec if spec else None


API_BASES = (
    "https://pcsupport.lenovo.com/us/zc/api/v4/mse",
    "https://pcsupport.lenovo.com/us/en/api/v4/mse",
    "https://pcsupport.lenovo.com/api/v4/mse",
)


def api_urls(endpoint, product_id):
    q = urllib.parse.quote(str(product_id).strip())
    return [f"{base}/{endpoint}?productId={q}" for base in API_BASES]


def query_lenovo(sn):
    sn = sn.upper().strip()
    print(f"  Querying SN: {sn}")

    # ── Step 1: resolve SN → product metadata ──────────────────────────────
    raw1 = None
    for url1 in api_urls("getproducts", sn):
        raw1 = fetch(url1, HEADERS_JSON, timeout=10)
        if raw1:
            break
    if not raw1:
        return {"error": "getproducts API failed"}

    try:
        products = json.loads(raw1)
    except Exception:
        return {"error": "invalid JSON from getproducts"}

    if not isinstance(products, list) or not products or not products[0].get("Id"):
        return {"error": "product not found for SN " + sn}

    product    = products[0]
    product_id = product["Id"].lower()
    name       = product.get("Name", "")
    mtm        = product.get("MTM") or product.get("MachineType") or ""
    prod_url   = product.get("Url") or product.get("ProductUrl") or ""

    print(f"  → productId={product_id}, MTM={mtm}, Name={name[:60]}")

    # ── Step 2a: try dedicated JSON spec endpoints ──────────────────────────
    spec_apis = []
    spec_apis.extend(api_urls("getproductspec", sn))
    spec_apis.extend(api_urls("getproductspec", product_id))
    if mtm:
        spec_apis.extend(api_urls("getproductspec", mtm))

    for api_url in spec_apis:
        raw = fetch(api_url, HEADERS_JSON, timeout=10)
        if not raw:
            continue
        try:
            ds = json.loads(raw)
            spec_raw = (
                ds.get("Specification") or ds.get("specification")
                or (ds[0].get("Specification") if isinstance(ds, list) and ds else None)
            )
            if spec_raw:
                if isinstance(spec_raw, str):
                    table = html_table_to_dict(spec_raw)
                elif isinstance(spec_raw, dict):
                    table = {k.lower(): str(v) for k, v in spec_raw.items()}
                else:
                    table = {}
                if table:
                    s = build_spec(table, name)
                    if s:
                        s["productId"] = product_id
                        s["mtm"] = mtm
                        s["productName"] = name
                        print("  ✓ spec from JSON API")
                        return s
        except Exception:
            pass

    # ── Step 2b: fetch product HTML page ───────────────────────────────────
    # NOTE: product_id from getproducts already contains the FULL path including
    # MTM and SN (e.g. "laptops-and-netbooks/.../thinkpad-l13.../20vl/20vls20600/pw016stt")
    # Just use it directly — do NOT append MTM/SN again.
    html_urls = []
    if prod_url:
        base = "https://pcsupport.lenovo.com"
        full = prod_url if prod_url.startswith("http") else base + prod_url
        html_urls.append(full)
    html_urls.append(f"https://pcsupport.lenovo.com/de/en/products/{product_id}")
    html_urls.append(f"https://pcsupport.lenovo.com/us/en/products/{product_id}")

    for page_url in html_urls:
        print(f"  Fetching: {page_url}")
        html = fetch(page_url, HEADERS_HTML, timeout=20)
        if not html:
            continue
        s = parse_spec_from_html(html, name)
        if s:
            s["productId"] = product_id
            s["mtm"] = mtm
            s["productName"] = name
            print("  ✓ spec from HTML page")
            return s
        else:
            print("  ✗ spec not found in HTML")

    return {
        "error": "spec not found — try Paste Spec manually",
        "productId": product_id,
        "mtm": mtm,
        "productName": name,
    }


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path in ("/", "/index.html", "/ALM_to_ARS_Converter.html"):
            # Serve the converter HTML so the page runs on http:// (no file:// CORS issues)
            import os
            html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "ALM_to_ARS_Converter.html")
            try:
                with open(html_path, "rb") as f:
                    body = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                self._json({"error": "ALM_to_ARS_Converter.html not found"}, 404)
            return

        if parsed.path == "/health":
            self._json({"ok": True, "port": PORT})
            return

        if parsed.path == "/spec":
            sns = params.get("sn", [])
            if not sns:
                self._json({"error": "missing ?sn= parameter"}, 400)
                return

            result = None
            last_result = None
            for sn in sns:
                r = query_lenovo(sn.strip())
                last_result = r
                # Accept result if it has at least one real spec field
                if r and any(k in r for k in ("processor", "memory", "driveType", "gpu")):
                    result = r
                    break

            if result is None:
                # Return the last attempt's error/metadata without querying it again.
                result = last_result if last_result is not None else {"error": "no SN provided"}

            self._json(result)
            return

        self._json({"error": "unknown path"}, 404)

    def _cors(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Type", "application/json")

    def _json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        # Minimal logging
        print(f"  [{self.address_string()}] {fmt % args}")


def run():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"╔══════════════════════════════════════════════╗")
    print(f"║  Lenovo Spec Helper  →  http://localhost:{PORT}  ║")
    print(f"╚══════════════════════════════════════════════╝")
    print(f"Open the ALM→ARS Converter in your browser.")
    print(f"Specs will be fetched automatically via this server.")
    print(f"Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run()
