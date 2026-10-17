# Dnevnik rada

Hronološki zapis odluka i koraka. Aktuelni plan: [`PLAN.md`](PLAN.md).
Odbačeni planovi i skripte ostaju u istoriji gita (`git log`).

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
