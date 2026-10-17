# Prikupljanje podataka: 89 beogradskih restorana sa TripAdvisora

Komentar na predložene opcije:

**Opcija 2 (trenutno stanje).** Trenutna TripAdvisor ocena je kumulativna, od otvaranja restorana do danas. To znači da sadrži i recenzije iz kojih bismo pravili rang iz 2018. Ako prediktor i ishod dele iste podatke, test ne govori ništa. Od „trenutnog stanja" su čisti samo zatvaranje i prirast broja recenzija. To ipak vredi prikupiti.

**Opcija 1 (top 100 iz 2022).** TripAdvisor ne čuva stare rangove. Ako bismo listu „top 100 iz 2022" napravili iz današnje liste, u uzorak bi ušli samo restorani koji su preživeli i dobro stoje danas. Tada bismo predviđali uspeh na uzorku koji je već izabran po uspehu.

**Rang iz rada Jelene Ristanović ne koristimo.** Metoda sabira ocenu (skala 1–5) sa percentilima (0–1) i bonusom konzistentnosti, pa nagrađuje restorane sa malo recenzija. Nije loša ideja, ali kao rang nije valjan ni za poređenje. Iz tog rada uzimamo samo **spisak 89 restorana**, jer je napravljen 2018, pre perioda koji ćemo posmatrati. To je ono što nam treba: kohorta fiksirana unapred.

## Plan u dva koraka

**Korak 1 (odmah, oko $0.50).** Za svih 89 restorana skinuti trenutno stanje. Dobijamo zatvaranja i prirast obima kao prve ishode i vidimo koliko je kohorte preživelo.

**Korak 2 (posle tvoje procene troška - javi mi i broj računa da ti uplatim).** Za istih 89 skinuti sve pojedinačne recenzije sa datumima. Rang gradimo na recenzijama do 31. 12. 2018, a proveravamo na recenzijama od 2019. do 2026. Poredimo prikazani TripAdvisor rang sa kompozitnim rangom koji ponderiše kredibilitet recenzenata (taj kompozit dobijate od mene, zajedno sa intervalima poverenja za rang).

## Korak 1: spisak i trenutno stanje

Prvo napraviti tabelu `restorani_89.csv` sa kolonama:

| kolona | opis |
|---|---|
| `id_2018` | redni broj iz rada (1–89, po koloni „KONAČNI RANG" ili „RangTA", samo da bude jednoznačno) |
| `name_2018` | naziv kako stoji u radu |
| `tripadvisor_url` | tačan URL stranice restorana na TripAdvisoru |
| `tripadvisor_location_id` | broj iz URL-a (deo posle `d`, npr. `d1234567`) |
| `match_note` | napomena ako je uparivanje bilo nesigurno |

Na šta obratiti pažnju pri uparivanju imena sa URL-ovima:
- U radu se neki nazivi javljaju dvaput jer su različite lokacije: *Burrito Madre* (dva puta) i *Smokvica* / *Smokvica Molerova*. Upariti po lokaciji, ne po imenu.
- Nazivi u radu imaju donje crte umesto razmaka i bez dijakritika (`Cevap_kod_Dekija`), pa pretraživati po smislu.
- Ako restoran ne možete da nađete, upisati `NOT_FOUND` u `match_note`, ne preskakati red. Nenađen restoran je verovatno zatvoren i obrisan, što je sam po sebi podatak.

Zatim za svaki URL skinuti (Apify actor za TripAdvisor restorane, ili ručno ako je brže):

| kolona | opis |
|---|---|
| `status` | `open` / `closed` / `not_found` |
| `rating_now` | prikazana ocena danas |
| `n_reviews_now` | ukupan broj recenzija danas |
| `rank_now` | pozicija na beogradskoj listi, ako je prikazana |
| `price_range`, `cuisine` | kako su prikazani (dobro dođe kasnije kao kontrola) |
| `date_checked` | datum kada ste proverili |

Zatvorene restorane proveriti ručno: TripAdvisor ih ponekad označi „Closed", a ponekad obriše stranicu.

## Korak 2: sve recenzije

Apify actor za TripAdvisor recenzije (npr. „TripAdvisor Reviews Scraper" ili sličan). Pre pokretanja proverite podešavanja, ovo je mesto gde se najčešće greši:

- **Sve recenzije**, bez limita po restoranu (`maxReviews` na dovoljno veliki broj ili bez limita). Nama trebaju i one iz 2010., ne samo poslednjih 100.
- **Svi jezici**, ne samo engleski. Beogradski restorani imaju mnogo recenzija na srpskom i drugim jezicima; podrazumevano podešavanje često vuče samo engleski.
- **Sortiranje po datumu** ako postoji opcija, da lakše proverite da li je istorija kompletna.
- Sačuvajte **sirov JSON izlaz** kakav jeste, pa tek onda pravite CSV. Ako nešto zatreba kasnije (tekst recenzije, naslov), ne skidamo ponovo.

Kolone koje nam trebaju u konačnoj tabeli `recenzije_89.csv`:

| kolona | opis | zašto |
|---|---|---|
| `id_2018` | iz tabele iz koraka 1 | uparivanje |
| `tripadvisor_location_id` | iz URL-a | uparivanje |
| `review_id` | jedinstveni id recenzije | uklanjanje duplikata |
| `review_date` | datum objave (ISO format, `2018-03-21`) | vremenski rez 2018 / 2019+ |
| `rating` | ocena 1–5 | osnovna mera |
| `reviewer_id` ili `reviewer_username` | identifikator recenzenta | isti recenzent kroz više restorana |
| `reviewer_contributions` | broj doprinosa recenzenta | kredibilitet (aktivnost) |
| `reviewer_helpful_votes` | broj korisnih glasova recenzenta | kredibilitet (korisnost) |
| `review_helpful_votes` | korisni glasovi na samoj recenziji, ako postoji | dopunski |
| `language` | jezik recenzije | kontrola |
| `trip_type` | solo / couple / family / business, ako postoji | kontrola |
| `title`, `text` | naslov i tekst | za kasniju tekstualnu analizu, ne briše se |

Važno: `reviewer_contributions` i `reviewer_helpful_votes` su **današnje** vrednosti sa profila recenzenta, a ne vrednosti u trenutku pisanja recenzije. To je ograničenje koje ćemo navesti u radu; isto ga je imala i prethodna analiza, pa je rezultat uporediv.

## Provere pre nego što mi pošaljete

1. Broj recenzija po restoranu u Vašoj tabeli naspram `n_reviews_now` iz koraka 1. Ako je Vaš broj znatno manji, nešto je ograničilo preuzimanje (limit ili jezik).
2. Najstariji datum po restoranu: treba da seže godinama unazad, ne samo u 2024.
3. `review_id` bez duplikata.
4. Udeo recenzija sa datumom do 31. 12. 2018: to je naš „trening" deo, treba da bude značajan.
5. Pošaljite mi `restorani_89.csv`, `recenzije_89.csv` i sirov JSON.

Pre pokretanja koraka 2 javite mi procenu troška. Ako Apify ponudi probu na par restorana, uradite nju prvo, to je najjeftiniji način da proverite podešavanja.

