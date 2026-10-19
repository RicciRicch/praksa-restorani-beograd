# Dnevnik rada

Hronološki zapis odluka i koraka. Aktuelni plan: [`PLAN.md`](PLAN.md).
Odbačeni planovi i skripte ostaju u istoriji gita (`git log`).

## 2026-10-19: Wayback 2018, obrisani restorani i zatvaranje (mentor #1, #5)
- `skripte/07_wayback_2018.py`, dva prolaza (±12 meseci, pa 2016–2020 za ostale): **snimak za 73/89**, od toga **12/14 obrisanih**; 31 snimak ≤ 6 meseci, 40 ≤ 12 meseci od 31. 7. 2018 (udaljenost u `wb_days_from_2018_07_31`). Broj recenzija na snimku / rad: medijan 1,08 (nezavisna potvrda brojeva iz rada). Raspodela u % samo na izgledu iz 2018 (27 restorana); na izgledu iz 2019 samo brojevi za filter „English“. Bez snimka 2016–2020: 16 restorana. → `podaci/wayback_2018.csv`.
- `skripte/08_wayback_obrisani.py`: sa svih sačuvanih snimaka 14 obrisanih stranica vraćeno samo **250 recenzija (162 do 2018)** od ≈ 3.900 iz rada (3–14% po restoranu; Wayback je uglavnom čuvao prvu stranu) → recenzije obrisanih nisu upotrebljive za drugi sloj; ostaju u prvom sloju. → `podaci/wayback_obrisani.csv`, `podaci/recenzije_wayback_obrisani.csv` (van gita).
- `closure_date_est` / `closure_source` za **13/17** (donja granica: posle poslednje poznate recenzije); 4 nepoznato (Salaš 034, Gnezdo Organic, Burrito Madre – Karađorđeva, Vapiano: na snimcima nema recenzija). Ručne dopune iz keširanih snimaka u pretrazi weba (OMB 2024, Splav Kota 70 2022, Via del Gusto 2025-05) u `podaci/izvor/zatvaranje_rucno.csv`.

## 2026-10-19: korak 2 — puna obrada recenzija (kaix)
- Mentoru javljeno: promena aktora, trošak ≈ $2, uplata nije potrebna.
- Apify `kaix/tripadvisor-reviews-scraper` (run `XmrN7J2tzBl2igxmc`, dataset `5yQgI1vBDuoND5SDR`, unos `apify/04_recenzije_89_kaix.json`, ≈ 4 min, ≈ $2.06): **41.256 recenzija** za 74 restorana, sve sa jedinstvenim ID-jem.
- Sirov JSON (kakav jeste, ugnežđen `author{...}`) u 9 delova: `podaci/raw/recenzije_89_kaix/deo_*.json` (≈ 80 MB, van gita).
- `podaci/recenzije_89.csv` (van gita, lični podaci) + izveštaj `podaci/provera_recenzija.md`:
  1. nepotpunih restorana (< 90% od `n_reviews_now`): **0** — svih 74 je 100%;
  2. bez recenzija do 2018: **1** (Burger House);
  3. duplikata: **0**;
  4. recenzija do 31. 12. 2018: **73,9%** (30.482); nijedan restoran nema < 10;
  5. 42,3% neengleskih (sr 4.458, it, tr, ru, de, fr, el…); prazan `reviewer_id` kod 62 recenzije;
  6. ispod 80% Ristanovićevog broja do 31. 7. 2018: **1** (Burger House).
- `history_complete_ratio` (mentorova definicija: do 31. 12. 2018 / rad 2018): medijan 1,05; > 1 je očekivano (rad je s kraja jula 2018); jedini < 0,9: Burger House (0). Za kafanu „?“ računato na nivou lokala (imenilac 609 + 107).
- **Slojevi:** sloj 2 = 73 lokala (74 reda, Znak Pitanja deli red sa Kafana Question Mark); samo sloj 1 = 15 (14 obrisanih + Burger House).

## 2026-10-19: odgovor mentora, Wayback 2018, izbor aktora
- Odgovor mentora sačuvan: `docs/odgovor_mentora_2026-10-19.md` (dva sloja, Wayback stanje 2018 za svih 89, `history_complete_ratio` ≥ 0,9 za drugi sloj, `entity_note`, 88 lokala, `closure_date_est`/`closure_source`, provera Filipovog aktora).
- **Filipov aktor**: u radu (Prilog 2) navedeni su samo parametri (`locationIds`, `maxReviewsPerLocation`, `sinceDate`, `includeTranslated`, `includeLocationRow`), ne ime; nijedan javni aktor u Apify Store-u nema te parametre → verovatno iznajmljen/privatan.
- **`kaix/tripadvisor-reviews-scraper`** (predložio Dušan; parametri se ne poklapaju sa Filipovim, ali naplata ≈ $0.05 / 1.000 recenzija): proba (run `BLykezMZaZVq8GSND`, ≈ $0.06) na ABC, Burger House i celom Little Bay-u → 1.239 / 1.239 recenzija; svih 146 recenzija iz maxcopell probe identične (ocena, datum, korisni glasovi, jezik, recenzent; broj doprinosa razlikuje se kod 1). Little Bay do 31. 7. 2018: 789 prema Ristanovićevih 805 (98%). Vraća i link profila recenzenta; 1,3% tekstova mašinski prevedeno (oznaka `is_machine_translated`, `language` ostaje originalni).
- **Izbor:** kaix za punu obradu → ≈ 41.256 recenzija ≈ **$2**, staje u besplatni kredit (mentor ne mora da uplaćuje). Unos `apify/04_recenzije_89_kaix.json`; skripta 05 podržava oba formata.
- Poslednje recenzije zatvorenih sa stranicom: Terminal 2025-08-12, Bistro Grad 2025-07-28 (Apify run `shtD0j40uliAFllLM`), Little Bay 2025-09-10.
- Nove skripte: `07_wayback_2018.py` (stanje 2018 za svih 89; radi sporo zbog Wayback ograničenja 503), `08_wayback_obrisani.py` (recenzije i zatvaranje za 14 obrisanih), `09_dopune_restorani.py` (entity_id/entity_note, sloj, closure_*, wb2018_*, history_complete_ratio). Ručne tabele: `podaci/izvor/entiteti_rucno.csv`, `podaci/izvor/zatvaranje_rucno.csv`.

## 2026-10-18: proba koraka 2 (besplatni kredit, ≈ $0.73)
- Proba A (run `TkevWdelMVCgm8JzB`): ABC Restoran 74/74 recenzija, najstarija 2008; do 31. 7. 2018 ima 64 prema Ristanovićevih 66 (97%) → rekonstrukcija stanja 2018 radi.
- Proba A: **Burger House Bros 52/52, ali najstarija iz 2021**; Ristanović je 2018 imao 214 → TA je izgubio/resetovao staru istoriju (restoran preimenovan). Mentorove provere 1–4 to ne hvataju → dodata **provera 6** (do 31. 7. 2018 vs. Ristanović, prag 80%).
- Proba B (run `2KWnJ6MGRYhSM8Rp4`): Little Bay (zatvoren) 20/20 → recenzije zatvorenih restorana čija stranica postoji se skidaju.
- Svi jezici stižu (28% neengleskih), nema mašinskog prevoda, broj doprinosa recenzenta popunjen, nema duplikata.
- Polja sačuvana u `podaci/raw/recenzije_proba*.json` (bez naslova, teksta i korisničkog imena; pun sirov JSON može da se izveze iz Apify konzole). CSV `podaci/recenzije_proba.csv` (van gita), izveštaj `podaci/provera_recenzija_proba.md`.

## 2026-10-18: priprema koraka 2 (dok se čeka mentor)
- `skripte/04_apify_unos_recenzije.py` → Apify unosi: proba A (ABC Restoran + Burger House Bros, cela istorija, ≈ 126 rec.), proba B (Little Bay, zatvoren, 20 rec.), puna obrada (74 restorana, ≈ 41.256 rec.).
- Prvobitni predlog probe (Ambar + Little Bay) odbačen: ≈ 3.400 recenzija ≈ $6.5–17. Nova proba ≈ $0.73 → staje u besplatni kredit.
- `skripte/05_recenzije_csv.py` (sirov JSON → `recenzije_89.csv`) i `skripte/06_provere_recenzija.py` (5 provera iz uputstva → `provera_recenzija.md`), testirane na izmišljenim podacima; test je otkrio da se 0 doprinosa upisivalo kao prazno → ispravljeno.
- `podaci/recenzije_*.csv` dodat u `.gitignore` (lični podaci recenzenata).

## 2026-10-18: provera 15 restorana u pregledaču (ispravka 1b)
- Svih 15 restorana koje Apify nije vratio otvoreno u pregledaču; kontrole Casa Nova (otvoren) i Little Bay (zatvoren) se otvaraju normalno.
- **14 TA stranica je obrisano** (URL preusmerava na listu restorana Beograda/Zemuna) → `not_found`. Među njima je i 8 restorana koje je pretraga weba prethodno pokazivala kao „CLOSED“; to su bili keširani snimci pre brisanja.
- **Znak Pitanja** preusmerava na Kafana Question Mark (d3411420) → TA je spojio unose; vodi se kao `open` bez sopstvenih brojeva.
- Konačno: **open 72 · closed 3 · not_found 14**; 17/89 (19%) restorana više ne radi po TA.
- Procena koraka 2 ispravljena na ≈ 41.000 recenzija (≈ $78 BRONZE / $206 FREE), jer recenzije obrisanih stranica nisu dostupne.
- ⚠️ Za mentora: zatvoreni restorani sa obrisanim stranicama ostaju bez istorije recenzija → rizik pristrasnosti preživljavanja.

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
