# Apify unosi

Svaki pokrenuti aktor ima svoj unos ovde, da bi skidanje bilo ponovljivo.
Unosi sa listom URL-ova prave se skriptom iz `podaci/restorani_89.csv` (posle koraka 1a).

| Fajl | Aktor | Izlaz (`podaci/raw/`) | Korak |
|---|---|---|---|
| `02_trenutno_stanje_89.json` | `maxcopell/tripadvisor` | `trenutno_stanje_89.json` | 1b, 89 URL-ova, ≈ $0.50 (pravi ga `skripte/02_upari_url.py`) |
| `03a_recenzije_proba.json` | `maxcopell/tripadvisor-reviews` | `recenzije_proba.json` | 2, proba: ABC Restoran + Burger House Bros, cela istorija (≈ 126 rec., ≈ $0.63 FREE) |
| `03b_recenzije_proba_zatvoren.json` | `maxcopell/tripadvisor-reviews` | `recenzije_proba_zatvoren.json` | 2, proba: Little Bay (zatvoren), 20 rec. (≈ $0.10 FREE) |
| `04_recenzije_89.json` | `maxcopell/tripadvisor-reviews` | `recenzije_89.json` | 2, 74 restorana sa stranicom, ≈ 41.256 rec. (≈ $78 BRONZE; posle odobrenja) |

Unose 03a, 03b i 04 pravi `skripte/04_apify_unos_recenzije.py`.

Obavezna podešavanja za recenzije (vidi `PLAN.md`, korak 2):
`maxItemsPerQuery: 1000000`, `reviewsLanguages: ["ALL_REVIEW_LANGUAGES"]`,
`disableMachineTranslations: true`, `scrapeReviewerInfo: true`, bez `lastReviewDate`.

## Pokretanja
| Datum | Unos | Run ID | Dataset | Rezultat | Cena |
|---|---|---|---|---|---|
| 2026-10-18 | `02_trenutno_stanje_89.json` | `lHqGf8kfgYLCmKlPS` | `fD0hruEEb3J6hOWWg` | 75 stavki (74 jedinstvene), 14 neuspelih stranica | ≈ $0.38 |
| 2026-10-18 | `03a_recenzije_proba.json` | `TkevWdelMVCgm8JzB` | `sCce6AskwXnYfQd5F` | 126 recenzija (ABC 74, Burger House 52) | ≈ $0.63 |
| 2026-10-18 | `03b_recenzije_proba_zatvoren.json` | `2KWnJ6MGRYhSM8Rp4` | `xFCVefh1NbhFm3xcY` | 20 recenzija (Little Bay) | ≈ $0.10 |

Posle svakog pokretanja zapisati u `DNEVNIK.md`: datum, ID pokretanja (run ID), broj rezultata, cenu.
