# Plan: kohorta 89 beogradskih restorana (TripAdvisor, 2018 → 2026)

Zasnovano na uputstvu mentora: [`docs/uputstvo_mentora.md`](docs/uputstvo_mentora.md).

## Pitanje
Da li **kompozitni rang koji ponderiše kredibilitet recenzenata** bolje predviđa kasniji uspeh restorana
od ranga koji je prikazivao TripAdvisor?

## Dizajn
| | Period | Šta |
|---|---|---|
| **Trening** | recenzije **do 31. 12. 2018.** | prikazani TA rang (prosek) vs. kompozitni rang (+ intervali poverenja za rang) |
| **Provera** | recenzije **od 1. 1. 2019. do 2026.** | ocene i obim novih recenzija, zatvaranje |

- **Kohorta:** 89 restorana iz rada Jelene Ristanović (2019), fiksirana 2018, pre perioda provere.
  Iz tog rada uzimamo **samo spisak**, ne rang i ne metodu.
- **Kompozit i intervale poverenja daje mentor**; naš deo je prikupljanje i provera podataka.

### Zašto baš ovako (iz uputstva)
- **Ne „top 100 iz 2022“:** TA ne čuva stare rangove; lista napravljena iz današnjih podataka sadrži samo preživele → uzorak izabran po uspehu.
- **Ne samo trenutno stanje:** današnja TA ocena je kumulativna (sadrži i recenzije iz trening perioda) → prediktor i ishod bi delili podatke. Čisti su samo zatvaranje i prirast broja recenzija.
- **Ne Ristanovićev rang:** sabira ocenu (1–5) sa percentilima (0–1) i bonusom konzistentnosti → nagrađuje restorane sa malo recenzija; nije valjan ni za poređenje.

## Korak 1: spisak i trenutno stanje (odmah, ≈ $0.50)
**1a. `podaci/restorani_89.csv`:** uparivanje naziva sa TA stranicama

| kolona | opis |
|---|---|
| `id_2018` | redni broj iz rada, 1–89 (kolona `KONACNI RANG`, samo kao jednoznačan ID) |
| `name_2018` | naziv kako stoji u radu |
| `tripadvisor_url` | tačan URL stranice restorana |
| `tripadvisor_location_id` | broj iz URL-a, bez slova `d` (npr. `8447925`; isto kao polje `id` u Apify izlazu) |
| `match_note` | napomena ako je uparivanje nesigurno; `NOT_FOUND` ako nije nađen (red se ne preskače) |

✅ **Urađeno 17. 10. 2026** (`skripte/02_upari_url.py`): **89/89 upareno**, 89 različitih TA ID-jeva, nijedan `NOT_FOUND`.
- Izvori: TA lista Beograda sa Wayback-a iz 2018 (rangovi 1–120), Wayback CDX spisak svih arhiviranih stranica restorana u Beogradu, a za 5 restorana pretraga weba.
- Ručna uparivanja sa obrazloženjem: `podaci/izvor/uparivanje_rucno.csv` (14 restorana).
- *Burrito Madre* ×2: TA #14 = d9844651, TA #27 = d7112940 (uparen po broju recenzija na TA listi 26. 7. 2018: 125 i 466 prema 125 i 470 u radu).
- *Kafana Question Mark* (d3411420) i *Znak Pitanja* (d8427347) su dva TA unosa iste kafane „?“, u radu dva reda → zadržana oba, navedeno u `match_note`.
- Greške u nazivima u radu: „Soga“ = Sofa Lounge bar, „Communale“ = Comunale, „Star_Koliba“ = Stara Koliba, „Careva_Cupija“ = Careva Ćuprija.
- Provera: za 79 restorana sa liste iz 2018 broj recenzija se slaže sa radom (odstupanje > 15% samo kod 2, oba sa ranijeg snimka iz januara 2018) → Ristanovićevi podaci su sa kraja jula 2018.
- *Restaurant Žabar* (Zemun): pretraga pominje „CLOSED“ i novi naziv „Naš Žabar“ → proveriti u 1b.

**1b. Trenutno stanje** (Apify `maxcopell/tripadvisor`, `startUrls` = 89 URL-ova), dodaje se u istu tabelu:

| kolona | opis |
|---|---|
| `status` | `open` / `closed` / `not_found` |
| `rating_now` | prikazana ocena danas |
| `n_reviews_now` | ukupan broj recenzija danas |
| `rank_now` | pozicija na beogradskoj listi, ako je prikazana |
| `price_range`, `cuisine` | kako su prikazani (kontrolne varijable) |
| `date_checked` | datum provere |
| `rank_list` | *(dodato)* na kojoj TA listi je rang (Zemun i „Bars & Pubs“ imaju svoje liste) |
| `status_note` | *(dodato)* izvor statusa za restorane koje Apify nije vratio |

Zatvorene i nenađene **proveriti ručno** (TA ih nekad označi „Closed“, a nekad obriše stranicu).

✅ **Urađeno 18. 10. 2026** (`skripte/03_trenutno_stanje.py`, Apify run `lHqGf8kfgYLCmKlPS`, ≈ $0.38):
- Apify vratio 74 od 89 (14 stranica nije uspeo da učita, Znak Pitanja vraćen kao Kafana Question Mark).
- Ručna provera u pregledaču (18. 10.) za svih 15: `podaci/izvor/provera_1b_rucno.csv`. Kontrole: Casa Nova (otvoren) i Little Bay (zatvoren) se normalno otvaraju.
- **open 72 · closed 3 · not_found 14**
  - **closed (3)**, TA stranica postoji, označena kao zatvorena: Little Bay, Bistro Grad, Terminal Gastro Bar;
  - **not_found (14)**, TA je **obrisao stranicu** (URL preusmerava na listu restorana Beograda/Zemuna): Salaš 034, Podrum Wine Art, Žabar, OMB Larder + Lounge, Mala Fabrika Ukusa, Red Bread, Splav Kota 70, Gnezdo Organic, Mala Gostionica, Burrito Madre (Karađorđeva), Tribeca, Via del Gusto, Supermarket, Vapiano. Za većinu keširani snimci u pretrazi weba pokazuju „CLOSED“ pre brisanja;
  - **Znak Pitanja** → TA je spojio unos sa Kafana Question Mark (d3411420) → `open`, bez sopstvenih brojeva (ne brojati dvaput).
- Ukupno **17 od 89 (19%) restorana više ne radi** po TripAdvisoru (3 closed + 14 obrisanih).
- Preimenovani, isti TA ID: Hotel Moskva Restaurant → Restaurant Tchaikovsky, Salon 5 → Salon 5a (sada Zemun), Walter → Walter – TC BEO, Burger House → Burger House Bros.

**1c. Procena troška koraka 2** = Σ `n_reviews_now` × cena po recenziji → poslati mentoru.

✅ Σ `n_reviews_now` = **41.256** recenzija za 74 restorana čije stranice postoje (72 otvorena + 3 zatvorena; Znak Pitanja je u Kafana Question Mark):

| Apify cena po recenziji | Procena |
|---|---|
| FREE plan, $0.005 | ≈ $206 |
| plaćeni plan (BRONZE), $0.0019 | ≈ $78 (+ mesečna pretplata plana) |
| SILVER, $0.0015 | ≈ $62 |

⚠️ **Rizik za korak 2 (javiti mentoru):** za **14 obrisanih stranica** TripAdvisor više ne prikazuje recenzije, pa ih Apify ne može skinuti. Upravo zatvoreni restorani bi tako ostali bez istorije recenzija (pristrasnost preživljavanja u „trening“ delu). Moguće dopune: Wayback snimci stranica sa recenzijama (delimično), ili tretirati ih samo kroz ishod „zatvaranje“. Proba u koraku 2 treba da uključi bar jedan zatvoren restoran čija stranica postoji (Little Bay), da se vidi da li se njegove recenzije skidaju.

## Korak 2: sve recenzije (posle mentorovog odobrenja i uplate)
Apify `maxcopell/tripadvisor-reviews`. Podešavanja (najčešće mesto greške):

| podešavanje | vrednost | zašto |
|---|---|---|
| `maxItemsPerQuery` | `1000000` | sve recenzije, i one iz 2010. |
| `reviewsLanguages` | `["ALL_REVIEW_LANGUAGES"]` | podrazumevano često samo engleski |
| `disableMachineTranslations` | `true` | originalni tekst, ne mašinski prevod |
| `scrapeReviewerInfo` | `true` | ID i broj doprinosa recenzenta (lični podaci → sirovi JSON ne ide u git) |
| `lastReviewDate` | ne postavljati | ne sme da preseče istoriju |

Prvo **proba** (najjeftinija provera podešavanja), pa tek onda svih 74 restorana čije stranice postoje.
Sirov JSON se čuva **kakav jeste** (`podaci/raw/`), CSV se pravi iz njega.

✅ **Pripremljeno 18. 10. 2026** (sve spremno za pokretanje):
| korak | unos / skripta | šta | trošak |
|---|---|---|---|
| proba A | `apify/03a_recenzije_proba.json` | ABC Restoran + Burger House Bros, **cela istorija** (≈ 126 recenzija) → potpunost, jezici, najstariji datum, polja | ≈ $0.63 (FREE) |
| proba B | `apify/03b_recenzije_proba_zatvoren.json` | Little Bay (zatvoren), **20 recenzija** → da li se recenzije zatvorenih skidaju | ≈ $0.10 (FREE) |
| puna obrada | `apify/04_recenzije_89.json` | 74 restorana, ≈ 41.256 recenzija | ≈ $78 (BRONZE) |
| CSV | `skripte/05_recenzije_csv.py` | sirov JSON → `podaci/recenzije_89.csv` (kolone iz tabele ispod; duplikati i recenzije van kohorte izbačeni) | – |
| provere | `skripte/06_provere_recenzija.py` | 5 provera iz uputstva → `podaci/provera_recenzija.md` | – |

Unose pravi `skripte/04_apify_unos_recenzije.py` iz `restorani_89.csv` (bez 14 obrisanih stranica i spojenog Znaka Pitanja).
Probe staju u besplatni Apify kredit → mogu i pre mentorove uplate.
Skripte 05 i 06 testirane na izmišljenim podacima u formatu aktora (duplikat, recenzija van kohorte, nepotpun restoran, tekst sa zarezima/navodnicima/novim redovima).
`podaci/recenzije_*.csv` nisu u gitu (lični podaci recenzenata), šalju se mentoru direktno.

**`podaci/recenzije_89.csv`**

| kolona | izvor u Apify izlazu |
|---|---|
| `id_2018`, `tripadvisor_location_id` | iz `restorani_89.csv` / `locationId` |
| `review_id` | `id` |
| `review_date` | `publishedDate` (ISO, `2018-03-21`) |
| `rating` | `rating` |
| `reviewer_id` / `reviewer_username` | `user.userId` / `user.username` |
| `reviewer_contributions` | `user.contributions.totalContributions` |
| `reviewer_helpful_votes` | ⚠️ **nema u izlazu ovog aktora** — javiti mentoru |
| `review_helpful_votes` | `helpfulVotes` |
| `language` | `originalLanguage` (i `lang`) |
| `trip_type` | `tripType` |
| `title`, `text` | `title`, `text` |

## Provere pre slanja mentoru
1. Broj recenzija po restoranu u `recenzije_89.csv` vs. `n_reviews_now` — znatno manje = limit ili jezik.
2. Najstariji datum po restoranu seže godinama unazad, ne samo do 2024.
3. `review_id` bez duplikata.
4. Udeo recenzija do 31. 12. 2018. (trening) je značajan.
5. Poslati: `restorani_89.csv`, `recenzije_89.csv`, sirov JSON.

## Ograničenja (za rad)
- `reviewer_contributions` je **današnja** vrednost sa profila, ne iz trenutka pisanja recenzije (isto ograničenje kao prethodna analiza → uporedivo).
- TA briše i filtrira recenzije → istorija skinuta 2026. nije identična onome što se videlo 2018.
- Period provere obuhvata COVID (2020–2021) → zatvaranje nije čist signal kvaliteta.
- n = 89 → umerena statistička moć.
