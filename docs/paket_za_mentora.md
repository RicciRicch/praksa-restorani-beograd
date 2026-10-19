# Paket podataka: kohorta 89 beogradskih restorana (TripAdvisor, 2018 → 2026)

Prikupljeno 18–19. 10. 2026. Postupak i podešavanja aktora: `podesavanja_aktora.md`.

## Tabele (CSV, UTF-8)
| fajl | red = | opis |
|---|---|---|
| `restorani_89.csv` | restoran (89) | uparivanje sa TA, trenutno stanje (2026), stanje 2018 sa Wayback-a (`wb2018_*`), `entity_id`/`entity_note`, `closure_date_est`/`closure_source`, `rad_n_reviews_2018`, `history_complete_ratio`, `sloj` |
| `recenzije_89.csv` | recenzija (41.256) | sve recenzije 74 restorana sa živim stranicama: `id_2018`, `tripadvisor_location_id`, `review_id`, `review_date`, `rating`, `reviewer_id`, `reviewer_username`, `reviewer_profile_url`, `reviewer_contributions`, `review_helpful_votes`, `language`, `is_machine_translated`, `trip_type`, `title`, `text` |
| `wayback/wayback_2018.csv` | restoran (89) | snimak TA stranice najbliži 31. 7. 2018: datum i udaljenost, ocena, broj recenzija, raspodela ocena (% svi jezici; brojevi za engleski), rang, adresa |
| `wayback/wayback_obrisani.csv` | restoran (14) | obrisane stranice: broj snimaka, vraćene recenzije (ukupno / do 2018) vs. rad, poslednji snimak i recenzija |
| `wayback/recenzije_wayback_obrisani.csv` | recenzija (250) | recenzije obrisanih restorana sa Wayback snimaka (delimično; broj doprinosa recenzenta *u trenutku snimka*) |
| `provera_recenzija.md` | – | rezultat provera iz uputstva (potpunost, najstariji datum, duplikati, udeo do 2018, jezici, poređenje sa radom) |

## Sirovi podaci
`raw/recenzije_89_kaix/deo_00000.json … deo_40000.json` — izlaz aktora `kaix/tripadvisor-reviews-scraper` kakav jeste (9 delova po 5.000, ukupno 41.256 recenzija).

## Ključni brojevi
- 89 restorana = **88 lokala** (Znak Pitanja i Kafana Question Mark: `entity_id` 84).
- Danas: 72 otvorena, 3 zatvorena (stranica postoji), 14 obrisanih stranica.
- **Sloj 2** (pune recenzije, `history_complete_ratio` ≥ 0,9): 73 lokala. **Samo sloj 1**: 14 obrisanih + Burger House (TA ne prikazuje recenzije pre 2021).
- Recenzije: 41.256; do 31. 12. 2018: 30.482 (73,9%); 42% nije na engleskom; 1,7% teksta (700) mašinski prevedeno (`is_machine_translated`).
- Stanje 2018 sa Wayback-a: 73/89 restorana (12/14 obrisanih).
- Rekonstrukcija 2018 iz skinutih recenzija (do 31. 7. 2018) se za većinu restorana slaže sa brojevima iz rada na 97–99% (`provera_recenzija.md`, kolona „% rada“).
- Datum zatvaranja: procenjen za 13/17 (donja granica), 4 nepoznato.

## Napomene
- `history_complete_ratio` = recenzije do 31. 12. 2018 / broj iz rada (kraj jula 2018) → vrednosti > 1 su očekivane (medijan 1,05).
- `reviewer_contributions` je današnja vrednost; `reviewer_helpful_votes` aktor ne vraća (prazno).
- `recenzije_*.csv` i sirov JSON sadrže lične podatke recenzenata (ID, korisničko ime, link profila).
