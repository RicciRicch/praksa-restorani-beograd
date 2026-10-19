"""
Recenzije i datum zatvaranja za restorane čije su TA stranice obrisane (mentor, 19. 10. 2026, tačke #1 i #5).

Za svaki restoran sa `status = not_found`:
  - Wayback CDX: svi sačuvani snimci TA stranice (glavna strana i strane recenzija -orNN, svi godine, .com, Beograd/Zemun)
  - iz snimaka se skupljaju sve recenzije (jedinstvene po ID-ju): datum, ocena, ID i korisničko ime recenzenta,
    broj doprinosa recenzenta *u trenutku snimka*, naslov
  - poslednji snimak stranice + najnovija recenzija na njemu → procena datuma zatvaranja

Ulaz:   podaci/restorani_89.csv, podaci/izvor/ristanovic_2019_tabela.csv
Keš:    podaci/raw/wayback/obrisani/  (van gita)
Izlazi:
  podaci/recenzije_wayback_obrisani.csv   recenzije (lični podaci recenzenata → van gita, kao ostale recenzije_*.csv)
  podaci/wayback_obrisani.csv             po restoranu: broj snimaka, vraćene recenzije (ukupno i do 2018) vs. rad 2018,
                                          poslednji snimak, najnovija recenzija, oznaka CLOSED

Pokretanje (iz korena repoa):
  python -u skripte/08_wayback_obrisani.py [--max-po-strani 3]
"""
import argparse, csv, datetime as dt, gzip, hashlib, re, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESTORANI = ROOT / "podaci" / "restorani_89.csv"
RISTANOVIC = ROOT / "podaci" / "izvor" / "ristanovic_2019_tabela.csv"
KES = ROOT / "podaci" / "raw" / "wayback" / "obrisani"
IZLAZ_REC = ROOT / "podaci" / "recenzije_wayback_obrisani.csv"
IZLAZ_RES = ROOT / "podaci" / "wayback_obrisani.csv"
GEO = ["g294472", "g1898555"]
PAUZA = 3  # sekundi između zahteva, da Wayback ne vrati 503
MESECI = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August",
                                       "September", "October", "November", "December"], 1)}


def preuzmi(url, putanja, pokusaji=4):
    if putanja.exists():
        return putanja.read_text(encoding="utf-8", errors="replace")
    for i in range(pokusaji):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "praksa-istrazivanje/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            if data[:2] == b"\x1f\x8b":
                data = gzip.decompress(data)
            txt = data.decode("utf-8", "replace")
            if "Temporarily Offline" in txt[:2000] or txt.strip() == "Gateway":
                raise IOError("Wayback privremeno nedostupan")
            putanja.write_text(txt, encoding="utf-8")
            return txt
        except Exception as e:
            print(f"    greška ({e}), pokušaj {i + 1}/{pokusaji}")
            time.sleep(30 * (i + 1))  # Wayback ograničava broj zahteva (503)
    return None


def snimci(d):
    out = []
    for g in GEO:
        url = (f"http://web.archive.org/cdx/search/cdx?url=tripadvisor.com/Restaurant_Review-{g}-d{d}-"
               f"&matchType=prefix&fl=timestamp,original&filter=statuscode:200")
        txt = preuzmi(url, KES / f"cdx_{g}_d{d}.txt") or ""
        out += [tuple(l.split(" ", 1)) for l in txt.splitlines() if l[:1].isdigit() and " " in l]
        time.sleep(PAUZA)
    return out


def izaberi(sn, max_po_strani):
    """Po svakoj strani (glavna, -or10, -or20…) do N snimaka, raspoređenih kroz vreme."""
    po_strani = {}
    for ts, orig in sorted(sn):
        m = re.search(r"-Reviews-(or\d+-)?", orig)
        po_strani.setdefault(m.group(1) if m else "", []).append((ts, orig))
    izbor = []
    for lista in po_strani.values():
        if len(lista) <= max_po_strani:
            izbor += lista
        else:
            korak = (len(lista) - 1) / (max_po_strani - 1)
            izbor += [lista[round(i * korak)] for i in range(max_po_strani)]
    return sorted(set(izbor))


def recenzije(h):
    out = []
    for blok in h.split('class="review-container"')[1:]:
        rid = re.search(r'data-reviewId="(\d+)"', blok)
        dat = re.search(r"ratingDate[^>]*title=['\"]([A-Z][a-z]+) (\d{1,2}), (20\d\d)['\"]", blok)
        if not (rid and dat and dat.group(1) in MESECI):
            continue
        ocena = re.search(r"ui_bubble_rating bubble_(\d)0", blok)
        uid = re.search(r'UID_([0-9A-F]{32})', blok)
        ime = re.search(r'class="[^"]*scrname[^"]*"[^>]*>([^<]+)<', blok)
        dopr = re.search(r'pencil-paper"></span><span class="badgetext">([\d,]+)<', blok)
        naslov = re.search(r"class='noQuotes'>([^<]*)<", blok)
        out.append({"review_id": rid.group(1),
                    "review_date": dt.date(int(dat.group(3)), MESECI[dat.group(1)], int(dat.group(2))).isoformat(),
                    "rating": ocena.group(1) if ocena else "",
                    "reviewer_id": uid.group(1) if uid else "",
                    "reviewer_username": ime.group(1).strip() if ime else "",
                    "reviewer_contributions_at_snapshot": dopr.group(1).replace(",", "") if dopr else "",
                    "title": naslov.group(1) if naslov else ""})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-po-strani", type=int, default=3)
    a = ap.parse_args()
    KES.mkdir(parents=True, exist_ok=True)
    restorani = [r for r in csv.DictReader(RESTORANI.open(encoding="utf-8")) if r["status"] == "not_found"]
    rad = {r["KONACNI RANG"]: int(r["brojSvihRecenz"]) for r in csv.DictReader(RISTANOVIC.open(encoding="utf-8"))}

    sve_rec, po_res = [], []
    for i, x in enumerate(restorani, 1):
        d = x["tripadvisor_location_id"]
        sn = snimci(d)
        izbor = izaberi(sn, a.max_po_strani)
        rec, poslednji, closed = {}, None, False
        for ts, orig in izbor:
            h = preuzmi(f"http://web.archive.org/web/{ts}id_/{orig}", KES / f"d{d}_{ts}_{hashlib.md5(orig.encode()).hexdigest()[:8]}.html")
            if h is None:
                continue
            for r in recenzije(h):
                r.setdefault("snapshot_ts", ts)
                rec.setdefault(r["review_id"], r)
            if "-Reviews-or" not in orig and (poslednji is None or ts > poslednji[0]):
                poslednji = (ts, h)
            time.sleep(PAUZA)
        najnovija_na_poslednjem = ""
        if poslednji:
            dat = [r["review_date"] for r in recenzije(poslednji[1])]
            najnovija_na_poslednjem = max(dat) if dat else ""
            closed = bool(re.search(r"CLOSED|[Pp]ermanently closed", re.sub(r"<[^>]+>", " ", poslednji[1])[:6000]))
        do_2018 = [r for r in rec.values() if r["review_date"] <= "2018-12-31"]
        datumi = sorted(r["review_date"] for r in rec.values())
        po_res.append({
            "id_2018": x["id_2018"], "name_2018": x["name_2018"], "tripadvisor_location_id": d,
            "wb_snimaka_ukupno": len(sn), "wb_snimaka_obradjeno": len(izbor),
            "wb_recenzija": len(rec), "wb_recenzija_do_2018": len(do_2018),
            "rad_n_reviews_2018": rad.get(x["id_2018"], ""),
            "wb_udeo_rada": f"{len(do_2018) / rad[x['id_2018']]:.2f}" if rad.get(x["id_2018"]) else "",
            "wb_najstarija": datumi[0] if datumi else "", "wb_najnovija": datumi[-1] if datumi else "",
            "wb_poslednji_snimak": poslednji[0][:8] if poslednji else (max(s[0] for s in sn)[:8] if sn else ""),
            "wb_najnovija_na_poslednjem": najnovija_na_poslednjem, "wb_closed_na_poslednjem": closed,
        })
        for r in rec.values():
            sve_rec.append({"id_2018": x["id_2018"], "tripadvisor_location_id": d, **r})
        p = po_res[-1]
        print(f"[{i}/{len(restorani)}] {x['name_2018'][:28]:28} snimaka {len(sn):3} → recenzija {len(rec):4} "
              f"(do 2018: {len(do_2018)}, rad: {p['rad_n_reviews_2018']}) poslednji {p['wb_poslednji_snimak']}")

    with IZLAZ_RES.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(po_res[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(po_res)
    kolone = ["id_2018", "tripadvisor_location_id", "review_id", "review_date", "rating", "reviewer_id",
              "reviewer_username", "reviewer_contributions_at_snapshot", "title", "snapshot_ts"]
    sve_rec.sort(key=lambda r: (int(r["id_2018"]), r["review_date"]))
    with IZLAZ_REC.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=kolone, lineterminator="\n")
        w.writeheader()
        w.writerows(sve_rec)
    print(f"\nRecenzija vraćeno: {len(sve_rec):,} (do 2018: {sum(r['review_date'] <= '2018-12-31' for r in sve_rec):,})")
    print(f"Upisano: {IZLAZ_RES.relative_to(ROOT)}, {IZLAZ_REC.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
