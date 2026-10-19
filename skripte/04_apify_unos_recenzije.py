"""
Korak 2 (priprema): pravi Apify unose za `maxcopell/tripadvisor-reviews`.

Ulaz:  podaci/restorani_89.csv (koraci 1a i 1b)
Izlazi:
  apify/03a_recenzije_proba.json  proba, cela istorija: ABC Restoran + Burger House Bros (mali, otvoreni; ≈ 126 recenzija)
                                   → provera potpunosti, jezika, najstarijeg datuma i polja
  apify/03b_recenzije_proba_zatvoren.json  proba: Little Bay (zatvoren, stranica postoji), samo 20 recenzija
                                   → da li se recenzije zatvorenih restorana uopšte skidaju
  apify/04_recenzije_89.json      svi restorani čija TA stranica postoji (status open/closed, sa sopstvenim brojevima)
  apify/04_recenzije_89_kaix.json isto, za `kaix/tripadvisor-reviews-scraper` (izabran za punu obradu, 19. 10. 2026:
                                   na probi identičan maxcopell-u, ≈ $0.05 / 1.000 recenzija)

Restorani sa `status = not_found` (TA obrisao stranicu) se ne šalju: recenzije im nisu dostupne.
Znak Pitanja nema sopstvene brojeve (spojen sa Kafana Question Mark) → recenzije dolaze preko tog unosa.

Podešavanja (PLAN.md, korak 2): sve recenzije, svi jezici, originalni tekst, podaci o recenzentu, bez datumskog reza.

Pokretanje (iz korena repoa):
  python skripte/04_apify_unos_recenzije.py
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESTORANI = ROOT / "podaci" / "restorani_89.csv"
PROBA = ROOT / "apify" / "03a_recenzije_proba.json"
PROBA_Z = ROOT / "apify" / "03b_recenzije_proba_zatvoren.json"
SVI = ROOT / "apify" / "04_recenzije_89.json"
SVI_KAIX = ROOT / "apify" / "04_recenzije_89_kaix.json"
KAIX = {"maxReviews": 0, "sortBy": "recent", "language": "all", "proxyConfiguration": {"useApifyProxy": True}}
PROBA_ID = ["810065", "4458196"]  # ABC Restoran, Burger House Bros
PROBA_Z_ID = ["1159647"]  # Little Bay (zatvoren)

PODESAVANJA = {
    "maxItemsPerQuery": 1000000,
    "reviewsLanguages": ["ALL_REVIEW_LANGUAGES"],
    "reviewRatings": ["ALL_REVIEW_RATINGS"],
    "disableMachineTranslations": True,
    "scrapeReviewerInfo": True,
}


def unos(redovi, limit=None):
    u = {"startUrls": [{"url": r["tripadvisor_url"]} for r in redovi], **PODESAVANJA}
    if limit:
        u["maxItemsPerQuery"] = limit
    return u


def main():
    redovi = list(csv.DictReader(RESTORANI.open(encoding="utf-8")))
    za_skidanje = [r for r in redovi if r["status"] in ("open", "closed") and r["n_reviews_now"] != ""]
    izaberi = lambda ids: [r for i in ids for r in redovi if r["tripadvisor_location_id"] == i]

    for putanja, izbor, limit in ((PROBA, izaberi(PROBA_ID), None), (PROBA_Z, izaberi(PROBA_Z_ID), 20),
                                  (SVI, za_skidanje, None)):
        putanja.write_text(json.dumps(unos(izbor, limit), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        n = sum(min(int(r["n_reviews_now"]), limit or 10**9) for r in izbor)
        print(f"{putanja.relative_to(ROOT)}: {len(izbor)} restorana, ≈ {n:,} recenzija "
              f"(≈ ${n * 0.0019:,.2f} BRONZE / ${n * 0.005:,.2f} FREE)")
    kaix = {"businesses": [r["tripadvisor_url"] for r in za_skidanje], **KAIX}
    SVI_KAIX.write_text(json.dumps(kaix, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    n = sum(int(r["n_reviews_now"]) for r in za_skidanje)
    print(f"{SVI_KAIX.relative_to(ROOT)}: {len(za_skidanje)} restorana, ≈ {n:,} recenzija (≈ ${n * 0.00005:,.2f})")
    print(f"Izostavljeno (stranica obrisana ili spojena): {len(redovi) - len(za_skidanje)}")


if __name__ == "__main__":
    main()
