"""
Korak 2: provere iz uputstva mentora pre slanja (`docs/uputstvo_mentora.md`, „Provere pre nego što mi pošaljete“).

Ulazi:  podaci/recenzije_89.csv (skripta 05), podaci/restorani_89.csv (koraci 1a i 1b)
Izlaz:  podaci/provera_recenzija.md (samo zbirni brojevi, bez ličnih podataka → može u git)

Provere:
  1. broj recenzija po restoranu vs. `n_reviews_now` (znatno manje = limit ili jezik)
  2. najstariji datum po restoranu (kohorta je bila u top 100 u 2018 → mora imati recenzije ≤ 2018)
  3. `review_id` bez duplikata
  4. udeo recenzija do 31. 12. 2018 („trening“ deo)
  5. (dodatno) jezici — da li su stigli svi, ne samo engleski; prazna polja recenzenta i datuma
  6. (dodatno) rekonstrukcija 2018: broj recenzija do 31. 7. 2018 vs. `brojSvihRecenz` iz Ristanovićeve tabele
     (njegovi podaci su sa kraja jula 2018) → hvata restorane kojima je TA obrisao staru istoriju

Pokretanje (iz korena repoa):
  python skripte/06_provere_recenzija.py                       # puna obrada (očekuje sve restorane iz 04_recenzije_89.json)
  python skripte/06_provere_recenzija.py --proba podaci/recenzije_proba.csv   # samo restorani prisutni u fajlu
"""
import argparse, csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESTORANI = ROOT / "podaci" / "restorani_89.csv"
RECENZIJE = ROOT / "podaci" / "recenzije_89.csv"
IZVESTAJ = ROOT / "podaci" / "provera_recenzija.md"
RISTANOVIC = ROOT / "podaci" / "izvor" / "ristanovic_2019_tabela.csv"
DATUM_2018 = "2018-07-31"
PRAG_2018 = 0.80         # manje od 80% Ristanovićevog broja → istorija nepotpuna
REZ = "2018-12-31"
PRAG_POTPUNOSTI = 0.90   # ispod 90% od n_reviews_now → upozorenje
MIN_TRENING = 10         # restoran sa manje recenzija do 2018 → upozorenje


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--proba", type=Path, help="CSV probe; proveravaju se samo restorani prisutni u njemu")
    ap.add_argument("--izvestaj", type=Path, default=IZVESTAJ)
    a = ap.parse_args()
    ulaz = a.proba or RECENZIJE

    restorani = {r["id_2018"]: r for r in csv.DictReader(RESTORANI.open(encoding="utf-8"))}
    rad_2018 = {r["KONACNI RANG"]: int(r["brojSvihRecenz"]) for r in csv.DictReader(RISTANOVIC.open(encoding="utf-8"))}
    rec = list(csv.DictReader(ulaz.open(encoding="utf-8")))
    po = defaultdict(list)
    for r in rec:
        po[r["id_2018"]].append(r)

    ocekivani = [i for i, r in restorani.items() if r["status"] in ("open", "closed") and r["n_reviews_now"]]
    if a.proba:
        ocekivani = [i for i in ocekivani if i in po]
    nedostaju = [restorani[i]["name_2018"] for i in ocekivani if i not in po]

    L = [f"# Provera recenzija ({ulaz.name})", "",
         f"Recenzija: **{len(rec):,}** · restorana sa recenzijama: **{len(po)}** · očekivano restorana: {len(ocekivani)}", ""]
    if nedostaju:
        L += [f"⚠️ Bez ijedne recenzije ({len(nedostaju)}): {', '.join(nedostaju)}", ""]

    # 1, 2, 4 po restoranu
    L += ["## Po restoranu", "",
          "| id_2018 | restoran | skinuto | n_reviews_now | % | najstariji | do 2018 | udeo do 2018 | do 7/2018 | rad 2018 | % rada | upozorenje |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    upoz = Counter()
    for i in sorted(ocekivani, key=int):
        rr = po.get(i, [])
        n_now = int(restorani[i]["n_reviews_now"])
        datumi = sorted(r["review_date"] for r in rr if r["review_date"])
        trening = sum(d <= REZ for d in datumi)
        do_jula = sum(d <= DATUM_2018 for d in datumi)
        rad = rad_2018.get(i, 0)
        pct = len(rr) / n_now if n_now else 0
        u = []
        if pct < PRAG_POTPUNOSTI:
            u.append("nepotpuno"); upoz["1 nepotpuno"] += 1
        if not datumi or datumi[0] > REZ:
            u.append("nema recenzija ≤ 2018"); upoz["2 najstariji > 2018"] += 1
        elif trening < MIN_TRENING:
            u.append(f"< {MIN_TRENING} do 2018"); upoz["4 malo trening recenzija"] += 1
        if rad and do_jula < PRAG_2018 * rad:
            u.append("istorija 2018 nepotpuna"); upoz["6 istorija 2018"] += 1
        L.append(f"| {i} | {restorani[i]['name_2018']} | {len(rr)} | {n_now} | {pct:.0%} | "
                 f"{datumi[0] if datumi else '–'} | {trening} | {trening / len(rr) if rr else 0:.0%} | "
                 f"{do_jula} | {rad} | {do_jula / rad if rad else 0:.0%} | {', '.join(u)} |")

    # 3 duplikati
    dupl = sum(c - 1 for c in Counter(r["review_id"] for r in rec).values() if c > 1)
    # 4 ukupno
    sa_datumom = [r for r in rec if r["review_date"]]
    trening_uk = sum(r["review_date"] <= REZ for r in sa_datumom)
    # 5 jezici i prazna polja
    jezici = Counter(r["language"] or "?" for r in rec)
    prazno = {k: sum(not r[k] for r in rec) for k in ("review_date", "rating", "reviewer_id", "reviewer_contributions")}
    po_godini = Counter(r["review_date"][:4] for r in sa_datumom)

    L += ["", "## Zbirno", "",
          f"1. Nepotpuno skinutih restorana (< {PRAG_POTPUNOSTI:.0%} od `n_reviews_now`): **{upoz['1 nepotpuno']}**",
          f"2. Restorana bez recenzija do 2018: **{upoz['2 najstariji > 2018']}**",
          f"3. Duplikata `review_id`: **{dupl}**",
          f"4. Udeo recenzija do 31. 12. 2018: **{trening_uk / len(sa_datumom) if sa_datumom else 0:.1%}** "
          f"({trening_uk:,} od {len(sa_datumom):,}); restorana sa < {MIN_TRENING} takvih: {upoz['4 malo trening recenzija']}",
          f"5. Jezici (top 8): " + ", ".join(f"{j} {n:,}" for j, n in jezici.most_common(8)),
          f"   Udeo neengleskih: {1 - jezici.get('en', 0) / len(rec) if rec else 0:.1%}",
          f"   Prazna polja: " + ", ".join(f"{k} {v:,}" for k, v in prazno.items()),
          f"6. Restorana sa < {PRAG_2018:.0%} Ristanovićevog broja recenzija do 31. 7. 2018: **{upoz['6 istorija 2018']}**",
          "", "## Recenzije po godini", "", "| godina | broj |", "|---|---|"]
    L += [f"| {g} | {n:,} |" for g, n in sorted(po_godini.items())]

    a.izvestaj.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[L.index("## Zbirno"):L.index("## Recenzije po godini")]))
    print(f"\nIzveštaj: {a.izvestaj}")


if __name__ == "__main__":
    main()
