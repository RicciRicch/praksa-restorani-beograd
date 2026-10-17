"""
Izvlači tabelu rezultata (89 restorana) iz Ristanovićevog diplomskog rada (2019).

Ulaz:  materijali/Diplomski rad verzija 3.doc   (lokalno, nije u gitu)
Izlaz: podaci/izvor/ristanovic_2019_tabela.csv  (17 kolona, kako stoje u radu)

Rad je u starom .doc formatu; tekst je zapisan kao UTF-16LE, a ćelije tabele su
razdvojene kontrolnim znakovima. Tabela počinje zaglavljem „RangTA“ i ima 17 kolona.
Iz tabele koristimo SAMO spisak restorana (kohorta fiksirana 2018), ne rang — vidi PLAN.md.

Provera: zbir `brojSvihRecenz` = 32.324 i `brojRecenzVece10` = 19.906
(tekst rada: 33.093 i 20.091 za svih 100, od čega 11 restorana nije prošlo filter).

Pokretanje (iz korena repoa):
  python skripte/01_izvuci_spisak_ristanovic.py
"""
import csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ULAZ = ROOT / "materijali" / "Diplomski rad verzija 3.doc"
IZLAZ = ROOT / "podaci" / "izvor" / "ristanovic_2019_tabela.csv"
BROJ_KOLONA = 17


def main():
    b = ULAZ.read_bytes()
    i = b.find("RangTA".encode("utf-16le"))
    if i < 0:
        raise SystemExit("Zaglavlje tabele 'RangTA' nije nađeno.")
    tekst = b[i:i + 60000].decode("utf-16le", "replace")
    celije = re.sub(r"[^\x20-\x7eĀ-ſ]+", "|", tekst).split("|")

    zaglavlje, redovi, j = celije[:BROJ_KOLONA], [], BROJ_KOLONA
    while j + BROJ_KOLONA <= len(celije) and celije[j].isdigit() and celije[j + BROJ_KOLONA - 1].isdigit():
        redovi.append(celije[j:j + BROJ_KOLONA])
        j += BROJ_KOLONA

    IZLAZ.parent.mkdir(parents=True, exist_ok=True)
    with IZLAZ.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(zaglavlje)
        w.writerows(redovi)

    svi = sum(int(r[2]) for r in redovi)
    kred = sum(int(r[6]) for r in redovi)
    print(f"{len(redovi)} restorana | recenzija: {svi} (očekivano 32324) | kredibilnih: {kred} (očekivano 19906)")
    print(f"Upisano: {IZLAZ.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
