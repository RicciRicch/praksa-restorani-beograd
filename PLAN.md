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

Zatvorene i nenađene **proveriti ručno** (TA ih nekad označi „Closed“, a nekad obriše stranicu).

**1c. Procena troška koraka 2** = Σ `n_reviews_now` × cena po recenziji → poslati mentoru.

## Korak 2: sve recenzije (posle mentorovog odobrenja i uplate)
Apify `maxcopell/tripadvisor-reviews`. Podešavanja (najčešće mesto greške):

| podešavanje | vrednost | zašto |
|---|---|---|
| `maxItemsPerQuery` | `1000000` | sve recenzije, i one iz 2010. |
| `reviewsLanguages` | `["ALL_REVIEW_LANGUAGES"]` | podrazumevano često samo engleski |
| `disableMachineTranslations` | `true` | originalni tekst, ne mašinski prevod |
| `scrapeReviewerInfo` | `true` | ID i broj doprinosa recenzenta (lični podaci → sirovi JSON ne ide u git) |
| `lastReviewDate` | ne postavljati | ne sme da preseče istoriju |

Prvo **proba na 2–3 restorana** (najjeftinija provera podešavanja), pa tek onda svih 89.
Sirov JSON se čuva **kakav jeste** (`podaci/raw/`), CSV se pravi iz njega.

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
