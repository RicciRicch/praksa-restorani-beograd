# Dnevnik rada

Hronološki zapis odluka i koraka. Detalji odluka su u `plan_ristanovic_2018_2026.md` (ranije `plan_beograd_2022_2026.md`).

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
- **Budžet:** Apify FREE plan naplaćuje $0.005 po restoranu i $0.005 po recenziji → skidanje svih recenzija za 100 restorana ≈ $80–200. Budžeta nema → **plan sa recenzijama otpada**. Ceo spisak (3000) nije pokrenut.
- **Wayback alternativa** (`skripte/01_wayback_pokrivenost.py` → `podaci/obradjeni/wayback_pokrivenost.csv`): stranica restorana iz 2022 sadrži ocenu, ukupan broj recenzija, broj po jezicima i raspodelu ocena (samo engleski). Od 93 kandidata (72 sa TA liste 2022 + 21 iz probe): snimak 2022 ima 58, 2025/26 ima 57, **oba samo 41** → premalo za glavni uzorak.
- **Ristanović 2019** (`materijali/Diplomski rad verzija 3.doc`): top 100 Beograd (TA, ~avg. 2018), 33.093 recenzije; filter recenzent ≥10 ukupnih TA recenzija (20.091) i restoran ≥10 takvih → 89 restorana. Ocena korigovana percentilima (broj recenzija recenzenta; odstupanje od proseka recenzenta), konačna ocena = prosek „naše ocene“ + (1 − CV). Samo opisno poređenje sa TA rangom, bez provere predviđanja.
- Iz `.doc` izvučena cela tabela rezultata (89 restorana) → `podaci/obradjeni/ristanovic_2019_tabela.csv` (zbirovi se slažu sa tekstom: 32.324 / 19.906 recenzija).
- **Novi pravac usvojen:** pratiti tih 89 restorana do 2026 (Apify spisak za 89 ≈ $0.45) i testirati da li je Ristanovićev rang iz 2018 bolje predvideo uspeh od TA ranga. → `plan_ristanovic_2018_2026.md` (v2).
- Želja: top 100 iz 2022, rang Ristanovićevom metodom na recenzijama do 2022, provera na 2023–2026 (opcija 1). Zahteva sve pojedinačne recenzije → ≈ $100–150 (Apify Starter); besplatno ≈ 2–3 restorana mesečno. Sopstveni skrejper odbačen (TA blokira; zaobilaženje zaštite krši uslove korišćenja).
- Mentoru poslate dve opcije: (1) top 100 iz 2022 uz finansiranje, (2) Ristanovićevih 89 iz 2018 (≈ $0.45). **Čeka se odgovor.**
