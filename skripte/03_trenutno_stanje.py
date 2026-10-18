"""
Korak 1b: trenutno stanje 89 restorana (Apify `maxcopell/tripadvisor`) → dopuna `podaci/restorani_89.csv`.

Ulazi:
  podaci/restorani_89.csv               iz koraka 1a (skripta 02)
  podaci/raw/trenutno_stanje_89.json    Apify izlaz (izvoz dataseta kao JSON; dovoljna su polja ispod)
  podaci/izvor/provera_1b_rucno.csv     ručna provera restorana koje Apify nije vratio (status + izvor)

Dodaje kolone (vidi PLAN.md):
  status          open / closed / not_found  (closed = isClosed ili isLongClosed; not_found = nema u izlazu)
  rating_now      rating
  n_reviews_now   numberOfReviews
  rank_now        rankingPosition, samo ako je lista „Restaurants in Belgrade“
  rank_list       na kojoj TA listi je rang (npr. „Restaurants in Zemun“, „Bars & Pubs in Belgrade“)
  price_range     priceLevel
  cuisine         cuisines, spojeno sa „; “
  date_checked    datum Apify pokretanja (argument, podrazumevano danas)
  status_note     izvor statusa za restorane koje Apify nije vratio (iz ručne provere)

Uparivanje je po TA location ID (`id` u Apify izlazu = `tripadvisor_location_id`).
Na kraju ispisuje procenu troška koraka 2 (Σ n_reviews_now × cena po recenziji).

Pokretanje (iz korena repoa):
  python skripte/03_trenutno_stanje.py [YYYY-MM-DD]
"""
import csv, datetime, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESTORANI = ROOT / "podaci" / "restorani_89.csv"
APIFY = ROOT / "podaci" / "raw" / "trenutno_stanje_89.json"
RUCNO = ROOT / "podaci" / "izvor" / "provera_1b_rucno.csv"
CENE = {"FREE ($0.005)": 0.005, "BRONZE ($0.0019)": 0.0019, "SILVER ($0.0015)": 0.0015}

KOLONE_1A = ["id_2018", "name_2018", "tripadvisor_url", "tripadvisor_location_id", "match_note"]
KOLONE_1B = ["status", "rating_now", "n_reviews_now", "rank_now", "rank_list",
             "price_range", "cuisine", "date_checked", "status_note"]


def main():
    datum = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
    redovi = list(csv.DictReader(RESTORANI.open(encoding="utf-8")))
    stavke = {str(x["id"]): x for x in json.loads(APIFY.read_text(encoding="utf-8"))}
    rucno = {r["tripadvisor_location_id"]: r for r in csv.DictReader(RUCNO.open(encoding="utf-8"))}

    for r in redovi:
        x = stavke.get(r["tripadvisor_location_id"])
        if x is None:
            p = rucno.get(r["tripadvisor_location_id"], {})
            r.update({k: "" for k in KOLONE_1B}, status=p.get("status", "not_found"), date_checked=datum,
                     status_note=p.get("status_note", "Apify nije vratio stranicu; nije ručno provereno"))
            continue
        lista = re.sub(r"^#[\d,]+ of [\d,]+ ", "", x.get("rankingString") or "")
        r.update({
            "status": "closed" if (x.get("isClosed") or x.get("isLongClosed")) else "open",
            "rating_now": x.get("rating") if x.get("rating") is not None else "",
            "n_reviews_now": x.get("numberOfReviews") if x.get("numberOfReviews") is not None else "",
            "rank_now": x.get("rankingPosition") if lista == "Restaurants in Belgrade" else "",
            "rank_list": lista,
            "price_range": x.get("priceLevel") or "",
            "cuisine": "; ".join(x.get("cuisines") or []),
            "date_checked": datum,
            "status_note": "",
        })

    with RESTORANI.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KOLONE_1A + KOLONE_1B, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(redovi)

    # Pregled
    vise = set(stavke) - {r["tripadvisor_location_id"] for r in redovi}
    po_statusu = {s: [r["name_2018"] for r in redovi if r["status"] == s] for s in ("open", "closed", "not_found")}
    print(f"Apify stavki: {len(stavke)} (van kohorte: {sorted(vise) or 'nema'})")
    for s, imena in po_statusu.items():
        print(f"  {s:9} {len(imena):3}" + (f"  {imena}" if s != "open" else ""))
    ostale_liste = sorted({r["rank_list"] for r in redovi if r["rank_list"] not in ("", "Restaurants in Belgrade")})
    print(f"Rang nije sa beogradske liste restorana: {ostale_liste or 'nema'}")

    ukupno = sum(int(r["n_reviews_now"]) for r in redovi if r["n_reviews_now"] != "")
    print(f"\nΣ n_reviews_now = {ukupno:,} recenzija → procena troška koraka 2 (Apify reviews):")
    for plan, cena in CENE.items():
        print(f"  {plan:18} ≈ ${ukupno * cena:,.2f}")
    print(f"Upisano: {RESTORANI.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
