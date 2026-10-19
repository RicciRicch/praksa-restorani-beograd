"""
Korak 2: sirov Apify JSON → `podaci/recenzije_89.csv`.
Podržana su dva aktora (format se prepoznaje po stavci):
  - `kaix/tripadvisor-reviews-scraper` (izabran za punu obradu: `author{...}`, `publishedDateISO`, `isTranslated`)
  - `maxcopell/tripadvisor-reviews` (proba: `user{...}`, `publishedDate`)
Ravna polja sa tačkom (npr. `author.userId`, kako ih vraća Apify MCP sa `fields=`) se takođe prihvataju.

Ulazi:
  podaci/restorani_89.csv          za id_2018 (uparivanje po TA location ID)
  podaci/raw/<ime>.json            sirov izvoz Apify dataseta, kakav jeste (jedan ili više fajlova)

Izlaz:
  podaci/recenzije_89.csv          kolone iz uputstva mentora (vidi PLAN.md, korak 2); jedan red = jedna recenzija
                                   (sadrži lične podatke recenzenata → nije u gitu)

- `reviewer_helpful_votes` nijedan aktor ne vraća → kolona ostaje prazna (mentor: dovoljno je `contributions`).
- `is_machine_translated`: kaix za mali deo recenzija vraća mašinski prevod teksta na engleski; `language` je uvek originalni jezik.
- Duplikati po `review_id` se izbacuju (zadržava se prvi), broj se ispisuje.
- Recenzije čiji `locationId` nije u kohorti se ne upisuju, broj se ispisuje.
- Datum je `publishedDate` skraćen na ISO datum (YYYY-MM-DD).

Pokretanje (iz korena repoa):
  python skripte/05_recenzije_csv.py podaci/raw/recenzije_89.json [podaci/raw/drugi_deo.json ...]
  python skripte/05_recenzije_csv.py podaci/raw/recenzije_proba.json --izlaz podaci/recenzije_proba.csv
"""
import argparse, csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESTORANI = ROOT / "podaci" / "restorani_89.csv"
IZLAZ = ROOT / "podaci" / "recenzije_89.csv"

KOLONE = ["id_2018", "tripadvisor_location_id", "review_id", "review_date", "rating",
          "reviewer_id", "reviewer_username", "reviewer_profile_url", "reviewer_contributions",
          "reviewer_helpful_votes", "review_helpful_votes", "language", "is_machine_translated",
          "trip_type", "title", "text"]


def ugnezdeno(x, *kljucevi):
    if ".".join(kljucevi) in x:  # ravno polje iz Apify MCP-a, npr. "author.userId"
        return x[".".join(kljucevi)]
    for k in kljucevi:
        x = x.get(k) if isinstance(x, dict) else None
    return x


def prvo(*vrednosti):
    return next((v for v in vrednosti if v not in (None, "")), None)


def ili_prazno(v):
    return "" if v is None else v


def red(x, id_2018):
    loc = str(x.get("locationId") or ugnezdeno(x, "placeInfo", "id") or "")
    return {
        "id_2018": id_2018.get(loc, ""),
        "tripadvisor_location_id": loc,
        "review_id": str(x.get("id") or ""),
        "review_date": (prvo(x.get("publishedDateISO"), x.get("publishedDate")) or "")[:10],
        "rating": ili_prazno(x.get("rating")),
        "reviewer_id": ili_prazno(prvo(ugnezdeno(x, "author", "userId"), ugnezdeno(x, "user", "userId"))),
        "reviewer_username": ili_prazno(prvo(ugnezdeno(x, "author", "username"), ugnezdeno(x, "user", "username"))),
        "reviewer_profile_url": ili_prazno(prvo(ugnezdeno(x, "author", "profileUrl"), ugnezdeno(x, "user", "link"))),
        "reviewer_contributions": ili_prazno(prvo(ugnezdeno(x, "author", "totalContributions"),
                                                  ugnezdeno(x, "user", "contributions", "totalContributions"))),
        "reviewer_helpful_votes": "",
        "review_helpful_votes": ili_prazno(x.get("helpfulVotes")),
        "language": x.get("originalLanguage") or x.get("lang") or "",
        "is_machine_translated": ili_prazno(prvo(x.get("isTranslated"), x.get("isMachineTranslated"))),
        "trip_type": (x.get("tripType") or "").upper(),  # kaix: "Business", maxcopell: "BUSINESS"
        "title": x.get("title") or "",
        "text": x.get("text") or "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ulazi", nargs="+", type=Path)
    ap.add_argument("--izlaz", type=Path, default=IZLAZ)
    a = ap.parse_args()

    restorani = list(csv.DictReader(RESTORANI.open(encoding="utf-8")))
    id_2018 = {r["tripadvisor_location_id"]: r["id_2018"] for r in restorani}

    stavke = []
    for f in a.ulazi:
        podaci = json.loads(f.read_text(encoding="utf-8"))
        stavke += podaci if isinstance(podaci, list) else [podaci]

    redovi, vidjeni, dupl, van = [], set(), 0, 0
    for x in stavke:
        r = red(x, id_2018)
        if r["review_id"] in vidjeni:
            dupl += 1
            continue
        if not r["id_2018"]:
            van += 1
            continue
        vidjeni.add(r["review_id"])
        redovi.append(r)

    redovi.sort(key=lambda r: (int(r["id_2018"]), r["review_date"], r["review_id"]))
    a.izlaz.parent.mkdir(parents=True, exist_ok=True)
    with a.izlaz.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KOLONE, lineterminator="\n")
        w.writeheader()
        w.writerows(redovi)

    print(f"Ulaznih stavki: {len(stavke):,} | upisano: {len(redovi):,} | duplikata izbačeno: {dupl} | van kohorte: {van}")
    print(f"Restorana sa recenzijama: {len({r['id_2018'] for r in redovi})}")
    print(f"Upisano: {a.izlaz}")


if __name__ == "__main__":
    main()
