# Dnevnik rada

Hronološki zapis odluka i koraka. Detalji odluka su u `plan_beograd_2022_2026.md`.

## 2026-10-16
- Pregledan plan (Beograd TripAdvisor 2022 → 2026).
- Wayback provera: za 2022 postoje samo strane 1–2 TA liste za Beograd (top 60, snimak 3.6.2022); strane 3–4 (rang 61–100) nisu arhivirane na .com.
- **Odluka:** umesto top 100 — stratifikovan nasumičan uzorak od 100 restorana po oceni iz 2022 (kriterijumi u planu). Razlog: suženi raspon ocena kod top 100 i nedostupan Wayback.
- Pripremljeni Apify unosi za korak 1 (`apify/01_*`).
- Projekat premešten u `project/`, pa vraćen u koren repoa; `materijali/` ostaje samo lokalno (u `.gitignore`).
- **Proba spiska** (`maxcopell/tripadvisor`, unos `01_spisak_restorana_proba.json`) → `podaci/raw/ta_beograd_spisak_proba.json`:
  - 46 restorana (traženo 50), bez duplikata, svi `type = RESTAURANT`, nijedan `isNearbyResult`.
  - TA kaže: **1.915 restorana u Beogradu** → ceo spisak ≈ 1.900–2.000 stavki.
  - Polja koja trebaju postoje: `id`, `webUrl`, `numberOfReviews`, `rating`, `rankingPosition`/`rankingString`, `isClosed`, `isLongClosed`, `subcategories`, `establishmentTypes`, `cuisines`, `ratingHistogram`, `rawRanking`.
  - Redosled nije po rangu (TA „featured“ sortiranje).
  - `rankingString` nije uvek „Restaurants in Belgrade“: 2 iz **Zemuna** (zasebna TA lokacija, svoj rang) i 1 rangiran kao „Bars & Pubs“. → rang ne porediti preko različitih lista; tip filtrirati preko `establishmentTypes`/`subcategories`.
  - Nijedan zatvoren (`isClosed`/`isLongClosed` = false) — očekivano za top restorane; da li aktor vraća zatvorene vidi se tek na celom spisku.
  - Sve trenutne vrednosti (`rating`, `numberOfReviews`, `ratingHistogram`) su stanje 2026 → **ne koriste se za izbor uzorka**, samo za grubo filtriranje kandidata.
