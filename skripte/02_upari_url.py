"""
Korak 1a: uparivanje 89 restorana iz rada (2018) sa TripAdvisor stranicama.

Ulazi:
  podaci/izvor/ristanovic_2019_tabela.csv   spisak 89 restorana (skripta 01)
  podaci/izvor/uparivanje_rucno.csv         ručna uparivanja sa obrazloženjem (prednost)
  podaci/raw/wayback/l2018_*.html           TA lista Beograda iz 2018 (Wayback), rang 1–120
  podaci/raw/wayback/cdx_restorani_g294472.txt  sve arhivirane stranice restorana u Beogradu (Wayback CDX)
  (ako fajlova iz raw/wayback nema, skripta ih preuzima sa Wayback-a)

Izlazi:
  podaci/restorani_89.csv                   id_2018, name_2018, tripadvisor_url, tripadvisor_location_id, match_note
  apify/02_trenutno_stanje_89.json          unos za Apify (korak 1b)

Postupak: naziv iz rada je TA „slug“ (npr. Cevap_kod_Dekija) → poređenje bez razmaka, interpunkcije
i velikih slova; prvo sa TA listom iz 2018, pa sa CDX listom. Ako ima više TA unosa istog imena,
skripta staje i traži ručno uparivanje. Provera: broj recenzija na listi 2018 vs. broj u radu.

Pokretanje (iz korena repoa):
  python skripte/02_upari_url.py
"""
import csv, gzip, json, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABELA = ROOT / "podaci" / "izvor" / "ristanovic_2019_tabela.csv"
RUCNO = ROOT / "podaci" / "izvor" / "uparivanje_rucno.csv"
WAYBACK = ROOT / "podaci" / "raw" / "wayback"
IZLAZ = ROOT / "podaci" / "restorani_89.csv"
APIFY = ROOT / "apify" / "02_trenutno_stanje_89.json"

TA = "https://www.tripadvisor.com/"
LISTE_2018 = {  # fajl -> Wayback snimak TA liste Beograda
    "l2018_20180726.html": "20180726/" + TA + "Restaurants-g294472-Belgrade.html",
    "l2018_20180724-oa30.html": "20180724/" + TA + "Restaurants-g294472-oa30-Belgrade.html",
    "l2018_20180131-oa60.html": "20180131/" + TA + "Restaurants-g294472-oa60-Belgrade.html",
    "l2018_20190121-oa60.html": "20190121/" + TA + "Restaurants-g294472-oa60-Belgrade.html",
    "l2018_20180724-oa90.html": "20180724/" + TA + "Restaurants-g294472-oa90-Belgrade.html",
}
CDX = ("cdx_restorani_g294472.txt",
       "http://web.archive.org/cdx/search/cdx?url=tripadvisor.com/Restaurant_Review-g294472-"
       "&matchType=prefix&collapse=urlkey&fl=original&limit=200000")
URL_RE = re.compile(r"Restaurant_Review-(g\d+)-d(\d+)-Reviews-(?:or\d+-)?([^\"#?/]+?)-([A-Za-z_]+)\.html")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def preuzmi(url, putanja):
    for i in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            putanja.write_bytes(data)
            return
        except Exception as e:
            print(f"  greška ({e}), pokušaj {i + 1}/4")
            time.sleep(10 * (i + 1))
    raise SystemExit(f"Nije uspelo preuzimanje: {url}")


def izvori():
    WAYBACK.mkdir(parents=True, exist_ok=True)
    for fajl, snimak in LISTE_2018.items():
        if not (WAYBACK / fajl).exists():
            ts, url = snimak.split("/", 1)
            preuzmi(f"http://web.archive.org/web/{ts}id_/{url}", WAYBACK / fajl)
    if not (WAYBACK / CDX[0]).exists():
        preuzmi(CDX[1], WAYBACK / CDX[0])


def kandidati():
    """norm(slug) -> {location_id: url}; posebno za liste 2018 i za CDX. Plus podaci sa liste 2018."""
    lista, cdx, lista_info = {}, {}, {}
    lista_ids = set()
    for fajl in LISTE_2018:
        h = (WAYBACK / fajl).read_text(encoding="utf-8", errors="replace")
        for g, d, slug, mesto in URL_RE.findall(h):
            lista.setdefault(norm(slug), {})[d] = f"{TA}Restaurant_Review-{g}-d{d}-Reviews-{slug}-{mesto}.html"
            lista_ids.add(d)
            blok = h[h.find(f'id="eatery_{d}"'):][:6000] if f'id="eatery_{d}"' in h else ""
            rec = re.search(r"([\d,]+) reviews", blok)
            rang = re.search(r"#([\d,]+) of [\d,]+", blok)
            if rec and d not in lista_info:
                lista_info[d] = (int(rec.group(1).replace(",", "")), rang and rang.group(0), fajl[6:14])
    for linija in (WAYBACK / CDX[0]).read_text(encoding="utf-8", errors="replace").split():
        m = URL_RE.search(linija)
        if m:
            g, d, slug, mesto = m.groups()
            cdx.setdefault(norm(slug), {})[d] = f"{TA}Restaurant_Review-{g}-d{d}-Reviews-{slug}-{mesto}.html"
    return lista, cdx, lista_info, lista_ids


def main():
    izvori()
    lista, cdx, lista_info, lista_ids = kandidati()
    rucno = {(r["rang_ta_2018"], r["name_2018"]): r for r in csv.DictReader(RUCNO.open(encoding="utf-8"))}
    redovi = list(csv.DictReader(TABELA.open(encoding="utf-8")))

    izlaz = []
    for r in redovi:
        ime, rang_ta = r["Restoran"], r["RangTA"]
        kljuc = (rang_ta, ime)
        if kljuc in rucno:
            url, napomena = rucno[kljuc]["tripadvisor_url"], rucno[kljuc]["match_note"]
        else:
            url = napomena = None
            for izvor, opis in ((lista, ""), (cdx, "nije na Wayback listama 2018; nađen u Wayback arhivi stranica")):
                c = izvor.get(norm(ime)) or izvor.get(re.sub("zemun$", "", norm(ime)))
                if c:
                    if len(c) > 1:
                        raise SystemExit(f"Više TA unosa za {ime} ({sorted(c)}) → dodati u uparivanje_rucno.csv")
                    url = next(iter(c.values()))
                    slug = URL_RE.search(url).group(3)
                    if izvor is cdx and URL_RE.search(url).group(2) in lista_ids:
                        opis = "na Wayback listi 2018 pod drugim slugom"
                    napomena = "; ".join(x for x in (opis, f"slug na TA: {slug}" if slug != ime else "") if x)
                    break
        if url is None:
            url, napomena = "", "NOT_FOUND"
        loc = URL_RE.search(url).group(2) if url else ""
        izlaz.append({"id_2018": int(r["KONACNI RANG"]), "name_2018": ime, "tripadvisor_url": url,
                      "tripadvisor_location_id": loc, "match_note": napomena,
                      "_rec_rad": int(r["brojSvihRecenz"]), "_rang_ta": rang_ta})

    izlaz.sort(key=lambda x: x["id_2018"])
    kolone = ["id_2018", "name_2018", "tripadvisor_url", "tripadvisor_location_id", "match_note"]
    with IZLAZ.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolone, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(izlaz)

    urls = [x["tripadvisor_url"] for x in izlaz if x["tripadvisor_url"]]
    unos = json.loads(json.dumps({
        "startUrls": [{"url": u} for u in urls], "maxItemsPerQuery": len(urls),
        "includeRestaurants": True, "includeHotels": False, "includeAttractions": False,
        "includeNearbyResults": False, "includeTags": False, "includeAiReviewsSummary": False,
        "maxPhotosPerPlace": 0, "maximumLeadsEnrichmentRecords": 0, "language": "en", "currency": "EUR"}))
    APIFY.write_text(json.dumps(unos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Provere
    nf = [x["name_2018"] for x in izlaz if x["match_note"] == "NOT_FOUND"]
    dup = {x["tripadvisor_location_id"] for x in izlaz if x["tripadvisor_location_id"]}
    print(f"Upareno: {len(urls)}/{len(izlaz)} | NOT_FOUND: {nf} | jedinstvenih location_id: {len(dup)}")
    print("Provera broja recenzija (TA lista 2018 vs. rad), razlika > 15%:")
    na_listi = 0
    for x in izlaz:
        info = lista_info.get(x["tripadvisor_location_id"])
        if not info:
            continue
        na_listi += 1
        rec, rang, datum = info
        if abs(rec - x["_rec_rad"]) > 0.15 * x["_rec_rad"]:
            print(f"  {x['name_2018']:32} rad: TA #{x['_rang_ta']}, {x['_rec_rad']} rec. | lista {datum}: {rang}, {rec} rec.")
    print(f"  ({na_listi} restorana ima podatke sa liste 2018)")
    print(f"Upisano: {IZLAZ.relative_to(ROOT)}, {APIFY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
