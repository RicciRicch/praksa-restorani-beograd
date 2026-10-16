# Apify unosi

Svaki pokrenuti aktor ima svoj unos ovde, da bi skidanje bilo ponovljivo.

| Fajl | Aktor | Izlaz (`podaci/raw/`) | Napomena |
|---|---|---|---|
| `01_spisak_restorana_proba.json` | `maxcopell/tripadvisor` | `ta_beograd_spisak_proba.json` | proba, 50 restorana |
| `01_spisak_restorana.json` | `maxcopell/tripadvisor` | `ta_beograd_spisak.json` | ceo spisak Beograda (`g294472`) |

Posle svakog pokretanja zapisati u `DNEVNIK.md`: datum, ID pokretanja (run ID), broj rezultata, cenu.
