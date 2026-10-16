"""
Provera pokrivenosti: koliko beogradskih restorana ima Wayback snimak TA stranice
iz 2022 (stanje 2022) i iz 2025/2026 (stanje danas).

Kandidati:
  1. restorani sa TA liste za Beograd, Wayback snimak 3.6.2022 (strane 1–2)
  2. restorani iz Apify probe (podaci/raw/ta_beograd_spisak_proba.json), ako postoji

Izlaz: podaci/obradjeni/wayback_pokrivenost.csv

Pokretanje (iz korena repoa):
  python skripte/01_wayback_pokrivenost.py
"""
import csv, gzip, json, re, sys, time, urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROBA = ROOT / "podaci" / "raw" / "ta_beograd_spisak_proba.json"
IZLAZ = ROOT / "podaci" / "obradjeni" / "wayback_pokrivenost.csv"

LISTE_2022 = [
    "https://web.archive.org/web/20220603id_/https://www.tripadvisor.com/Restaurants-g294472-Belgrade.html",
    "https://web.archive.org/web/20220603id_/https://www.tripadvisor.com/Restaurants-g294472-oa30-Belgrade.html",
]
URL_RE = re.compile(r"Restaurant_Review-(g\d+)-(d\d+)-Reviews-([^\"#?/]+)\.html")
GODINE = range(2021, 2027)


def preuzmi(url, pokusaji=4):
    for i in range(pokusaji):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "praksa-istrazivanje/1.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                data = r.read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            return data.decode("utf-8", "replace")
        except Exception as e:
            print(f"  greška ({e}), pokušaj {i + 1}/{pokusaji}", file=sys.stderr)
            time.sleep(5 * (i + 1))
    return None


def kandidati():
    """Vraća {d_id: (g_id, slug, izvor)}."""
    k = {}
    for url in LISTE_2022:
        html = preuzmi(url) or ""
        for g, d, slug in URL_RE.findall(html):
            k.setdefault(d, (g, slug, "lista_2022"))
        time.sleep(1)
    if PROBA.exists():
        for x in json.loads(PROBA.read_text(encoding="utf-8")):
            m = URL_RE.search(x.get("webUrl") or "")
            if m:
                g, d, slug = m.groups()
                k.setdefault(d, (g, slug, "apify_proba"))
    return k


def snimci(g, d):
    """Datumi (YYYYMMDD) uspešnih Wayback snimaka stranice restorana, po jedan dnevno."""
    url = (
        "https://web.archive.org/cdx/search/cdx?matchType=prefix&fl=timestamp"
        "&filter=statuscode:200&collapse=timestamp:8&from=2021&to=2026"
        f"&url=tripadvisor.com/Restaurant_Review-{g}-{d}-"
    )
    txt = preuzmi(url)
    if txt is None:
        return None
    return sorted({line[:8] for line in txt.split() if line[:4].isdigit()})


def main():
    k = kandidati()
    print(f"Kandidata: {len(k)}  {dict(Counter(v[2] for v in k.values()))}")
    IZLAZ.parent.mkdir(parents=True, exist_ok=True)
    redovi = []
    for i, (d, (g, slug, izvor)) in enumerate(sorted(k.items()), 1):
        ts = snimci(g, d)
        red = {"d_id": d, "g_id": g, "naziv": slug.replace("_", " "), "izvor": izvor,
               "greska": ts is None}
        ts = ts or []
        for god in GODINE:
            red[f"n_{god}"] = sum(t.startswith(str(god)) for t in ts)
        red["prvi_2022"] = next((t for t in ts if t.startswith("2022")), "")
        red["poslednji"] = ts[-1] if ts else ""
        red["ima_2022"] = red["n_2022"] > 0
        red["ima_2025_26"] = red["n_2025"] + red["n_2026"] > 0
        red["ima_oba"] = red["ima_2022"] and red["ima_2025_26"]
        redovi.append(red)
        print(f"[{i}/{len(k)}] {red['naziv'][:40]:40} 2022={red['n_2022']} 2025-26={red['n_2025'] + red['n_2026']}")
        time.sleep(1)

    with IZLAZ.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(redovi[0]))
        w.writeheader()
        w.writerows(redovi)

    n = len(redovi)
    print(f"\nUkupno {n} | ima 2022: {sum(r['ima_2022'] for r in redovi)} | "
          f"ima 2025/26: {sum(r['ima_2025_26'] for r in redovi)} | "
          f"ima OBA: {sum(r['ima_oba'] for r in redovi)} | greške: {sum(r['greska'] for r in redovi)}")
    print(f"Upisano: {IZLAZ.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
