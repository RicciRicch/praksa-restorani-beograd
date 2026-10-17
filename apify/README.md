# Apify unosi

Svaki pokrenuti aktor ima svoj unos ovde, da bi skidanje bilo ponovljivo.
Unosi sa listom URL-ova prave se skriptom iz `podaci/restorani_89.csv` (posle koraka 1a).

| Fajl | Aktor | Izlaz (`podaci/raw/`) | Korak |
|---|---|---|---|
| `02_trenutno_stanje_89.json` | `maxcopell/tripadvisor` | `trenutno_stanje_89.json` | 1b, 89 URL-ova, ≈ $0.50 |
| `03_recenzije_proba.json` | `maxcopell/tripadvisor-reviews` | `recenzije_proba.json` | 2, proba na 2–3 restorana |
| `04_recenzije_89.json` | `maxcopell/tripadvisor-reviews` | `recenzije_89.json` | 2, svih 89 (posle odobrenja) |

Obavezna podešavanja za recenzije (vidi `PLAN.md`, korak 2):
`maxItemsPerQuery: 1000000`, `reviewsLanguages: ["ALL_REVIEW_LANGUAGES"]`,
`disableMachineTranslations: true`, `scrapeReviewerInfo: true`, bez `lastReviewDate`.

Posle svakog pokretanja zapisati u `DNEVNIK.md`: datum, ID pokretanja (run ID), broj rezultata, cenu.
