"""
Stanje 2018 sa Wayback Machine-a za svih 89 restorana (mentor, 19. 10. 2026, tačka #1).

Za svaki restoran: snimak TA stranice restorana najbliži 31. 7. 2018 (prozor ±12 meseci),
pa iz njega prikazana ocena, ukupan broj recenzija, raspodela ocena i rang.
Daje stanje 2018 i za restorane čije su stranice danas obrisane, i nezavisnu proveru brojeva iz rada.

Ulaz:   podaci/restorani_89.csv, podaci/izvor/ristanovic_2019_tabela.csv
Keš:    podaci/raw/wayback/2018/  (CDX odgovori i HTML snimci; van gita)
Izlaz:  podaci/wayback_2018.csv

Kolone izlaza:
  wb_snapshot_ts, wb_snapshot_url, wb_days_from_2018_07_31
  wb_rating                 prikazana ocena (svi jezici)
  wb_n_reviews              ukupan broj recenzija (svi jezici)
  wb_pct_5 … wb_pct_1       raspodela ocena u % (svi jezici; Excellent … Terrible), kako je prikazana
  wb_n_en, wb_en_5 … wb_en_1  broj engleskih recenzija i njihova raspodela po ocenama (filter na stranici je bio „English“)
  wb_rank, wb_rank_list     rang i lista („Restaurants in Belgrade“…)
  wb_closed                 da li je stranica tada bila označena kao zatvorena
  wb_address                adresa iz 2018 (za proveru preimenovanja/preseljenja, `entity_note`)
  wb_page_reviews, wb_page_newest, wb_page_oldest   recenzije na prvoj strani snimka (broj i raspon datuma)
  rad_n_reviews_2018        `brojSvihRecenz` iz Ristanovićeve tabele (kraj jula 2018), za poređenje
  wb_note                   napomena (nema snimka, delimično parsirano…)

Pokretanje (iz korena repoa; traje dugo zbog sporog Wayback-a, keš omogućava nastavak):
  python -u skripte/07_wayback_2018.py
"""
import csv, datetime as dt, gzip, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESTORANI = ROOT / "podaci" / "restorani_89.csv"
RISTANOVIC = ROOT / "podaci" / "izvor" / "ristanovic_2019_tabela.csv"
KES = ROOT / "podaci" / "raw" / "wayback" / "2018"
IZLAZ = ROOT / "podaci" / "wayback_2018.csv"

CILJ = dt.date(2018, 7, 31)
OD, DO = "20170731", "20190731"
DOMENI = ["tripadvisor.com", "tripadvisor.co.uk"]
GEO = ["g294472", "g1898555"]  # Beograd, Zemun (neki restorani su promenili geo, npr. Salon 5)
OCENE = ["Excellent", "Very good", "Average", "Poor", "Terrible"]
PAUZA = 3  # sekundi između zahteva, da Wayback ne vrati 503
MESECI = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                       "September", "October", "November", "December"], 1)}


def preuzmi(url, putanja=None, pokusaji=4):
    if putanja and putanja.exists():
        return putanja.read_text(encoding="utf-8", errors="replace")
    for i in range(pokusaji):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "praksa-istrazivanje/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            txt = data.decode("utf-8", "replace")
            if "Temporarily Offline" in txt[:2000]:
                raise IOError("Wayback privremeno nedostupan")
            if putanja:
                putanja.write_text(txt, encoding="utf-8")
            return txt
        except Exception as e:
            print(f"    greška ({e}), pokušaj {i + 1}/{pokusaji}")
            time.sleep(30 * (i + 1))  # Wayback ograničava broj zahteva (503)
    return None


def snimci(d):
    """Svi uspešni snimci glavne stranice restorana (ne -orNN strane) u prozoru, sa svih domena i geo-a."""
    nadjeno = []
    for domen in DOMENI:
        for g in GEO:
            kes = KES / f"cdx_{domen}_{g}_d{d}.txt"
            url = (f"http://web.archive.org/cdx/search/cdx?url={domen}/Restaurant_Review-{g}-d{d}-"
                   f"&matchType=prefix&from={OD}&to={DO}&fl=timestamp,original&filter=statuscode:200")
            txt = preuzmi(url, kes)
            if txt is None:
                continue
            for linija in txt.splitlines():
                deo = linija.split(" ", 1)
                if len(deo) == 2 and deo[0].isdigit() and "-Reviews-or" not in deo[1]:
                    nadjeno.append((deo[0], deo[1]))
            time.sleep(PAUZA)
        if nadjeno:  # dovoljno je prvi domen na kom ima snimaka
            break
    return nadjeno


def dani(ts):
    return abs((dt.date(int(ts[:4]), int(ts[4:6]), int(ts[6:8])) - CILJ).days)


def broj(s):
    return int(s.replace(",", "")) if s else ""


def parsiraj(h):
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h))
    r = {}
    m = re.search(r'"ratingValue"\s*(?::|content=)\s*"([\d.]+)"', h)
    r["wb_rating"] = m.group(1) if m else ""
    m = re.search(r'"reviewCount"\s*:\s*"?([\d,]+)', h)
    r["wb_n_reviews"] = broj(m.group(1)) if m else ""
    for k, lab in zip((5, 4, 3, 2, 1), OCENE):
        m = re.search(lab + r" (\d+)%", t)
        r[f"wb_pct_{k}"] = m.group(1) if m else ""
        m = re.search(lab + r" ([\d,]+) (?!%)", t)
        r[f"wb_en_{k}"] = broj(m.group(1)) if m else ""
    m = re.search(r"English \(([\d,]+)\)", t)
    r["wb_n_en"] = broj(m.group(1)) if m else ""
    m = re.search(r"#([\d,]+) of [\d,]+ ((?:Restaurants|Bars & Pubs|Coffee & Tea) in [A-Z][A-Za-z]*)", t)
    r["wb_rank"], r["wb_rank_list"] = (broj(m.group(1)), m.group(2)) if m else ("", "")
    m = re.search(r'"streetAddress"\s*:\s*"([^"]*)"', h) or re.search(r'class="street-address">([^<]*)<', h)
    r["wb_address"] = m.group(1).strip() if m else ""
    r["wb_closed"] = bool(re.search(r"CLOSED|[Pp]ermanently closed", t[:5000]))
    datumi = []
    for mes, dan, god in re.findall(r"ratingDate[^>]*title=['\"]([A-Z][a-z]+) (\d{1,2}), (20\d\d)['\"]", h):
        if mes in MESECI:
            datumi.append(dt.date(int(god), MESECI[mes], int(dan)).isoformat())
    r["wb_page_reviews"] = len(datumi)
    r["wb_page_newest"] = max(datumi) if datumi else ""
    r["wb_page_oldest"] = min(datumi) if datumi else ""
    return r


def main():
    KES.mkdir(parents=True, exist_ok=True)
    restorani = list(csv.DictReader(RESTORANI.open(encoding="utf-8")))
    rad = {r["KONACNI RANG"]: r["brojSvihRecenz"] for r in csv.DictReader(RISTANOVIC.open(encoding="utf-8"))}

    izlaz = []
    for i, x in enumerate(restorani, 1):
        d = x["tripadvisor_location_id"]
        red = {"id_2018": x["id_2018"], "name_2018": x["name_2018"], "tripadvisor_location_id": d,
               "rad_n_reviews_2018": rad.get(x["id_2018"], "")}
        sn = snimci(d)
        if not sn:
            red["wb_note"] = "nema snimka u prozoru 31. 7. 2017 – 31. 7. 2019"
        else:
            ts, orig = min(sn, key=lambda s: dani(s[0]))
            red.update(wb_snapshot_ts=ts, wb_snapshot_url=f"https://web.archive.org/web/{ts}/{orig}",
                       wb_days_from_2018_07_31=dani(ts))
            h = preuzmi(f"http://web.archive.org/web/{ts}id_/{orig}", KES / f"d{d}_{ts}.html")
            if h is None:
                red["wb_note"] = "snimak nije preuzet (Wayback greška)"
            else:
                red.update(parsiraj(h))
                fale = [k for k in ("wb_rating", "wb_n_reviews", "wb_pct_5", "wb_en_5") if red.get(k) in ("", None)]
                red["wb_note"] = f"nije parsirano: {', '.join(fale)}" if fale else ""
        izlaz.append(red)
        print(f"[{i}/{len(restorani)}] {x['name_2018'][:30]:30} {red.get('wb_snapshot_ts', '–'):14} "
              f"n={red.get('wb_n_reviews', '')} rad={red['rad_n_reviews_2018']} {red.get('wb_note', '')}")
        time.sleep(PAUZA)

    kolone = ["id_2018", "name_2018", "tripadvisor_location_id", "wb_snapshot_ts", "wb_snapshot_url",
              "wb_days_from_2018_07_31", "wb_rating", "wb_n_reviews",
              "wb_pct_5", "wb_pct_4", "wb_pct_3", "wb_pct_2", "wb_pct_1",
              "wb_n_en", "wb_en_5", "wb_en_4", "wb_en_3", "wb_en_2", "wb_en_1",
              "wb_rank", "wb_rank_list", "wb_closed", "wb_address", "wb_page_reviews", "wb_page_newest", "wb_page_oldest",
              "rad_n_reviews_2018", "wb_note"]
    with IZLAZ.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolone, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(izlaz)

    sa = [r for r in izlaz if r.get("wb_snapshot_ts")]
    print(f"\nSa snimkom: {len(sa)}/{len(izlaz)} | potpuno parsirano: {sum(not r.get('wb_note') for r in sa)}")
    print(f"Upisano: {IZLAZ.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
