# Predviđanje uspeha restorana: kohorta 89 beogradskih restorana (TripAdvisor, 2018 → 2026)

Da li kompozitni rang koji ponderiše kredibilitet recenzenata bolje predviđa kasniji uspeh restorana
od ranga koji prikazuje TripAdvisor? Rang se gradi na recenzijama do 31. 12. 2018,
a proverava na recenzijama od 2019. do 2026.

- **Plan:** [`PLAN.md`](PLAN.md)
- **Uputstvo mentora** (osnova plana): [`docs/uputstvo_mentora.md`](docs/uputstvo_mentora.md)
- **Dnevnik rada:** [`DNEVNIK.md`](DNEVNIK.md)

## Stanje
| Korak | Status |
|---|---|
| Spisak 89 restorana iz rada (2019) | ✅ `podaci/izvor/ristanovic_2019_tabela.csv` |
| 1a. Uparivanje sa TA URL-ovima → `podaci/restorani_89.csv` | ✅ 89/89 |
| 1b. Trenutno stanje (Apify, ≈ $0.38) | ✅ open 72 · closed 3 · not_found 14 (TA obrisao stranicu; provereno u pregledaču) |
| 1c. Procena troška koraka 2 → mentor | ✅ ≈ 41.000 recenzija → ≈ $78 (BRONZE) / $206 (FREE); ⏳ slanje mentoru |
| 2. Sve recenzije → `podaci/recenzije_89.csv` | 🛠️ unosi i skripte spremni; proba (≈ $0.73, besplatni kredit) može odmah; puna obrada čeka odobrenje |

## Struktura
| Putanja | Sadržaj | U gitu |
|---|---|---|
| `PLAN.md`, `DNEVNIK.md` | plan i hronologija odluka | da |
| `docs/` | uputstvo mentora | da |
| `apify/` | tačni unosi za Apify aktore (ponovljivost) | da |
| `skripte/` | Python skripte, numerisane redom izvršavanja | da |
| `podaci/izvor/` | ulazni podaci iz prethodnih radova | da |
| `podaci/restorani_89.csv` | konačna tabela restorana (koraci 1a i 1b) | da |
| `podaci/recenzije_*.csv` | konačna tabela recenzija (korak 2) | **ne** (lični podaci recenzenata; ide mentoru direktno) |
| `podaci/provera_recenzija.md` | izveštaj provera (samo zbirni brojevi) | da |
| `podaci/raw/` | sirovi Apify JSON, kakav jeste | **ne** (veličina, lični podaci recenzenata) |
| `materijali/` | prethodni radovi, concept note | **ne** (tuđi radovi) |

## Pokretanje
```bash
python skripte/01_izvuci_spisak_ristanovic.py
python skripte/02_upari_url.py
python skripte/03_trenutno_stanje.py 2026-10-18
python skripte/04_apify_unos_recenzije.py
# korak 2, posle Apify pokretanja (sirov JSON sačuvati u podaci/raw/):
python skripte/05_recenzije_csv.py podaci/raw/recenzije_89.json
python skripte/06_provere_recenzija.py
```
Skripta 03 čita `podaci/raw/trenutno_stanje_89.json` (izvoz Apify dataseta `fD0hruEEb3J6hOWWg`, van gita).
Za probu: `05_recenzije_csv.py podaci/raw/recenzije_proba.json --izlaz podaci/recenzije_proba.csv`, pa `06_provere_recenzija.py --proba podaci/recenzije_proba.csv --izvestaj podaci/provera_recenzija_proba.md`.
Skripte se pokreću iz korena repoa. Potreban je Python 3.10+ (bez dodatnih paketa za sada).
