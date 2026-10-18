# Dnevnik rada

Hronološki zapis odluka i koraka. Aktuelni plan: [`PLAN.md`](PLAN.md).
Odbačeni planovi i skripte ostaju u istoriji gita (`git log`).

## 2026-10-18: korak 1b završen (trenutno stanje) i procena troška
- Apify `maxcopell/tripadvisor` za 89 URL-ova (run `lHqGf8kfgYLCmKlPS`, dataset `fD0hruEEb3J6hOWWg`, ≈ $0.38): 75 stavki, 14 stranica neuspelo, Znak Pitanja (d8427347) vraćen kao Kafana Question Mark (d3411420) → TA je verovatno spojio unose.
- Potrebna polja sačuvana u `podaci/raw/trenutno_stanje_89.json` (van gita; pun izvoz dataseta može da zameni fajl, skripta radi isto).
- `skripte/03_trenutno_stanje.py` → dopunjen `podaci/restorani_89.csv`: **open 71 · closed 11 · not_found 7**.
- Ručna provera 15 restorana koje Apify nije vratio (pretraga weba, naslovi TA stranica) → `podaci/izvor/provera_1b_rucno.csv`: 8 zatvorenih, 7 ostaje za proveru u pregledaču.
- **Obrazac:** Apify ne uspeva da učita stranice zatvorenih restorana → rizik da u koraku 2 nedostaje istorija zatvorenih (pristrasnost preživljavanja) → uključiti u probu.
- **Procena koraka 2:** Σ `n_reviews_now` = 41.256 (74 restorana) + ≈ 3.500–4.000 zatvorenih → ≈ 45.000 recenzija ≈ **$85** (BRONZE) / **$225** (FREE).
- **Ispravka koraka 1a:** `match_note` je greškom imao „na Wayback listi 2018 pod drugim slugom“ i kod restorana nađenih direktno na listi (greška u `02_upari_url.py`). Ispravljeno; URL-ovi i ID-jevi nepromenjeni.
- Preimenovani (isti TA ID): Hotel Moskva Restaurant → Restaurant Tchaikovsky, Salon 5 → Salon 5a (Zemun), Walter → Walter – TC BEO, Burger House → Burger House Bros.

## 2026-10-17: korak 1a završen (uparivanje URL-ova)
- `skripte/02_upari_url.py` → `podaci/restorani_89.csv`: **89/89 upareno**, 89 jedinstvenih TA ID-jeva, nijedan `NOT_FOUND`.
- Izvori (besplatno): TA lista Beograda sa Wayback-a iz 2018 (snimci 31.1., 24.7., 26.7.2018 i 21.1.2019; rangovi 1–120), Wayback CDX spisak 785 arhiviranih stranica restorana u Beogradu, pretraga weba za 5 restorana kojih nema u arhivi (Salaš 034, Žabar, Careva Ćuprija, MYDAN, Cantina de Frida).
- Ručna uparivanja sa obrazloženjem: `podaci/izvor/uparivanje_rucno.csv` (duplikati imena, greške u nazivima u radu, Zemun).
- Provera: broj recenzija na TA listi 2018 se slaže sa radom (79 restorana) → Ristanovićevi podaci su sa kraja jula 2018.
- Napravljen Apify unos za korak 1b: `apify/02_trenutno_stanje_89.json` (89 URL-ova).
- Wayback je povremeno bio nedostupan („Temporarily Offline“); izvori su keširani u `podaci/raw/wayback/` (van gita), skripta ih ponovo preuzima ako fale.

## 2026-10-17: dizajn određen (mentor)
- Mentor odredio dizajn ([`docs/uputstvo_mentora.md`](docs/uputstvo_mentora.md)):
  - **kohorta = 89 restorana iz rada Jelene Ristanović (2019)**, samo spisak, ne rang ni metoda;
  - **trening:** recenzije do 31. 12. 2018; **provera:** 2019–2026;
  - poređenje: prikazani TA rang vs. kompozitni rang sa kredibilitetom recenzenata (kompozit i intervale poverenja daje mentor);
  - korak 1 odmah (trenutno stanje, ≈ $0.50), korak 2 (sve recenzije) posle procene troška; trošak pokriva mentor.
- Odbačeno uz obrazloženje: „top 100 iz 2022“ (pristrasnost preživljavanja), samo trenutno stanje (ocena kumulativna → prediktor i ishod dele podatke), Ristanovićev rang (sabira skale 1–5 i 0–1, nagrađuje male restorane).
- Repo sređen prema tome: uklonjeni stari planovi, Wayback provera i Apify unosi za ceo Beograd; dodati `PLAN.md`, `docs/uputstvo_mentora.md`, `skripte/01_izvuci_spisak_ristanovic.py`.
- Provera kohorte: 89 jedinstvenih redova; *Burrito Madre* ×2 i *Smokvica* / *Smokvica – Molerova* (kako je mentor naveo); dodatno *Kafana Question Mark* i *Znak Pitanja* verovatno ista kafana „?“ → proveriti pri uparivanju.
- Provera aktora `maxcopell/tripadvisor-reviews`: ima sva tražena polja osim **`reviewer_helpful_votes`** (na nivou recenzenta postoji samo `contributions`) → javiti mentoru.

## 2026-10-16: istraživanje opcija (sažetak)
- Prvi plan (Beograd 2022 → 2026, sve recenzije) pokazao se preskupim na Apify FREE planu ($0.005 po recenziji).
- Wayback Machine: za 2022 sačuvan samo top 60 beogradske TA liste; od 93 restorana samo 41 ima snimak stranice i iz 2022 i iz 2025/26 → Wayback nije dovoljan izvor.
- Proba Apify spiska (46 restorana Beograda): aktor vraća `id`, `webUrl`, `numberOfReviews`, `rating`, `rankingPosition`, `isClosed`, `ratingHistogram`, `priceLevel`, `cuisines`… Zemun ima zaseban TA rang.
- U Ristanovićevom radu (`materijali/Diplomski rad verzija 3.doc`) nađena kompletna tabela 89 restorana (top 100 TA, ~avg. 2018) → `podaci/izvor/ristanovic_2019_tabela.csv`; zbirovi se slažu sa tekstom rada (32.324 / 19.906 recenzija).
- Mentoru poslate opcije; odgovor 17. 10. (gore).
- Postavljen git repo (privatni GitHub `RicciRicch/praksa-restorani-beograd`); `materijali/` i `podaci/raw/` van gita.
