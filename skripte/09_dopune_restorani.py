"""
Dopune tabele `podaci/restorani_89.csv` po odgovoru mentora (19. 10. 2026, `docs/odgovor_mentora_2026-10-19.md`).
Pokreće se posle skripte 03 (koja tabelu piše iz početka) i posle 07/08 (Wayback), a ponovo i posle koraka 2.

Ulazi (svaki osim restorani_89.csv je opcioni; ako fali, kolone ostaju prazne):
  podaci/restorani_89.csv                koraci 1a i 1b
  podaci/izvor/entiteti_rucno.csv         entity_id, entity_note (#2, #4)
  podaci/izvor/zatvaranje_rucno.csv       closure_date_est, closure_source za zatvorene sa stranicom (#5)
  podaci/wayback_obrisani.csv             poslednji znak života obrisanih stranica (skripta 08) (#5)
  podaci/wayback_2018.csv                 stanje 2018 sa Wayback-a (skripta 07) (#1)
  podaci/izvor/ristanovic_2019_tabela.csv broj recenzija iz rada (2018)
  podaci/recenzije_89.csv                 skinute recenzije (korak 2) → history_complete_ratio (#2)

Dodaje kolone:
  entity_id, entity_note          jedinstveni lokal (kafana „?“ = 84 → 88 lokala) i napomena o preimenovanju/spajanju
  closure_date_est, closure_source   za restorane koji ne rade (YYYY-MM i izvor)
  wb2018_*                        ocena, broj recenzija i raspodela ocena (%) sa snimka najbližeg 31. 7. 2018
  rad_n_reviews_2018              broj recenzija iz Ristanovićevog rada (kraj jula 2018)
  history_complete_ratio          skinute recenzije do 31. 12. 2018 / rad_n_reviews_2018 (definicija mentora);
                                  prazno za obrisane stranice; za spojeni lokal (kafana „?“) imenilac je zbir oba unosa iz rada;
                                  rad je sa kraja jula 2018, pa odnos > 1 kod restorana koji su rasli u drugoj polovini 2018
  sloj                            1 = samo prvi sloj (nivo restorana, ishod zatvaranje)
                                  2 = i drugi sloj (živa stranica, pune recenzije, history_complete_ratio ≥ 0,9)

Pokretanje (iz korena repoa):
  python skripte/09_dopune_restorani.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P = ROOT / "podaci"
RESTORANI = P / "restorani_89.csv"
PRAG_ISTORIJE = 0.9

KOLONE_1AB = ["id_2018", "name_2018", "tripadvisor_url", "tripadvisor_location_id", "match_note", "status",
              "rating_now", "n_reviews_now", "rank_now", "rank_list", "price_range", "cuisine", "date_checked",
              "status_note"]
KOLONE_NOVE = ["entity_id", "entity_note", "closure_date_est", "closure_source",
               "wb2018_snapshot", "wb2018_rating", "wb2018_n_reviews",
               "wb2018_pct_5", "wb2018_pct_4", "wb2018_pct_3", "wb2018_pct_2", "wb2018_pct_1", "wb2018_address",
               "rad_n_reviews_2018", "history_complete_ratio", "sloj"]


def citaj(putanja, kljuc="id_2018"):
    if not putanja.exists():
        return {}
    return {r[kljuc]: r for r in csv.DictReader(putanja.open(encoding="utf-8"))}


def main():
    redovi = list(csv.DictReader(RESTORANI.open(encoding="utf-8")))
    entiteti = citaj(P / "izvor" / "entiteti_rucno.csv")
    zatv = citaj(P / "izvor" / "zatvaranje_rucno.csv")
    obrisani = citaj(P / "wayback_obrisani.csv")
    wb = citaj(P / "wayback_2018.csv")
    rad = citaj(P / "izvor" / "ristanovic_2019_tabela.csv", "KONACNI RANG")

    do_2018 = {}
    rec = P / "recenzije_89.csv"
    if rec.exists():
        for r in csv.DictReader(rec.open(encoding="utf-8")):
            if r["review_date"] and r["review_date"] <= "2018-12-31":
                do_2018[r["id_2018"]] = do_2018.get(r["id_2018"], 0) + 1

    for r in redovi:
        i = r["id_2018"]
        e = entiteti.get(i, {})
        r["entity_id"] = e.get("entity_id", i)
        r["entity_note"] = e.get("entity_note", "")

        # #5 zatvaranje
        r["closure_date_est"] = r["closure_source"] = ""
        if i in zatv:
            r["closure_date_est"], r["closure_source"] = zatv[i]["closure_date_est"], zatv[i]["closure_source"]
        elif r["status"] == "not_found" and i in obrisani:
            o = obrisani[i]
            poslednja = o.get("wb_najnovija", "")
            r["closure_date_est"] = poslednja[:7]
            r["closure_source"] = (f"TA stranica obrisana (provera 18.10.2026); Wayback: poslednja sačuvana recenzija "
                                   f"{poslednja or '–'}, poslednji snimak {o.get('wb_poslednji_snimak') or '–'}, "
                                   f"oznaka CLOSED na poslednjem snimku: {'da' if o.get('wb_closed_na_poslednjem') == 'True' else 'ne'}"
                                   f" → zatvaranje posle poslednje recenzije (donja granica)")

        # #1 stanje 2018 sa Wayback-a
        w = wb.get(i, {})
        r["wb2018_snapshot"] = w.get("wb_snapshot_ts", "")[:8]
        r["wb2018_rating"] = w.get("wb_rating", "")
        r["wb2018_n_reviews"] = w.get("wb_n_reviews", "")
        for k in (5, 4, 3, 2, 1):
            r[f"wb2018_pct_{k}"] = w.get(f"wb_pct_{k}", "")
        r["wb2018_address"] = w.get("wb_address", "")

        # #2 potpunost istorije i sloj
        n_rad = int(rad[i]["brojSvihRecenz"]) if i in rad else 0
        r["rad_n_reviews_2018"] = n_rad or ""
        ziva = r["status"] in ("open", "closed") and r["n_reviews_now"] != ""
        # odnos samo za restorane čije su recenzije skidane; spojeni lokal: zbir svih unosa iz rada
        clanovi = [k for k, v in entiteti.items() if v.get("entity_id") == r["entity_id"]] or [i]
        n_rad_lokal = sum(int(rad[k]["brojSvihRecenz"]) for k in clanovi if k in rad)
        r["history_complete_ratio"] = (f"{do_2018.get(i, 0) / n_rad_lokal:.3f}"
                                       if (do_2018 and ziva and n_rad_lokal) else "")
        if not ziva:
            r["sloj"] = 1
        elif r["history_complete_ratio"] == "":
            r["sloj"] = "2?"  # pre koraka 2: kandidat za drugi sloj
        else:
            r["sloj"] = 2 if float(r["history_complete_ratio"]) >= PRAG_ISTORIJE else 1

    # spojeni unos (Znak Pitanja) deli sloj sa svojim entitetom
    po_id = {r["id_2018"]: r for r in redovi}
    for r in redovi:
        if r["entity_id"] != r["id_2018"] and r["entity_id"] in po_id:
            r["sloj"] = po_id[r["entity_id"]]["sloj"]

    with RESTORANI.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=KOLONE_1AB + KOLONE_NOVE, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(redovi)

    lokala = len({r["entity_id"] for r in redovi})
    sloj = {s: sum(str(r["sloj"]) == s for r in redovi) for s in ("1", "2", "2?")}
    print(f"Restorana: {len(redovi)} | jedinstvenih lokala: {lokala} | sloj: {sloj}")
    print(f"Zatvaranje procenjeno: {sum(bool(r['closure_date_est']) for r in redovi)} od "
          f"{sum(r['status'] != 'open' for r in redovi)} | Wayback 2018: {sum(bool(r['wb2018_snapshot']) for r in redovi)}"
          f" | history_complete_ratio: {sum(r['history_complete_ratio'] != '' for r in redovi)}")


if __name__ == "__main__":
    main()
