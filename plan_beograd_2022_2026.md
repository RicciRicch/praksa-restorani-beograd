# Plan: Beograd TripAdvisor 2022 → 2026 (predviđanje uspeha restorana)

> **ODBAČEN 16.10.2026** — zamenjen planom `plan_ristanovic_2018_2026.md` (skidanje svih recenzija preko Apify-ja je preskupo, budžeta nema). Ostavljen radi istorije odluka.

## Odluke (16.10.2026)
- Uzorak: **100 beogradskih restorana sa TripAdvisora, stratifikovano po oceni iz 2022** (ne top 100 — vidi „Izbor uzorka“).
  - Razlog: top 100 ima suženo raspon ocena (~4.5–5) → slabe korelacije; Wayback za 2022 ima samo strane 1–2 liste (top 60, snimak 3.6.2022).
- Google Maps: **ne** (samo TripAdvisor).
- Vremenski dizajn: **2022 je polazna tačka, 2026 krajnja.**
  - Prediktori: **sve recenzije do 31.12.2022** (kumulativno, isto ono na čemu je počivao rang iz 2022 — kao kod Ivljanin/Ristanović).
  - Glavni ishod: **sve recenzije od 1.1.2023 do trenutka prikupljanja 2026.**
  - Dodatno (isti podaci, bez dodatnog skidanja):
    - ishod samo iz 2026 → direktno uporedivo sa Filipovim radom;
    - ishod posebno za 2023, 2024, 2025, 2026 → koliko predviđanje slabi sa udaljenošću.
  - Zašto ne samo 2022–2023 vs 2024–2026: izbacivanje recenzija pre 2022 slabi prediktore, a rang iz 2022 je i sam bio zasnovan na celoj istoriji.

## Izbor uzorka
- Uključenje (sve mereno **samo na recenzijama ≤ 31.12.2022**):
  1. prva recenzija ≤ 2021 (restoran postojao pre 2022);
  2. ≥ 30 recenzija do 31.12.2022;
  3. TA tip „Restaurant“ (ne kafić/pekara/poslastičarnica). Hoteli i lanci: otvoreno pitanje.
- **Zabranjeno:** bilo kakav uslov na aktivnost posle 2022 (izbacio bi zatvorene → pristrasnost preživljavanja).
- Stratifikacija po proseku do 2022 (okvirno): ≥ 4.5 → 40, 4.0–4.49 → 35, < 4.0 → 25; unutar sloja **nasumičan izbor** (fiksni seed).
- Zatvoreni restorani: proveriti da li ih TA/Apify još prikazuje; ako ne, dopuniti okvir iz Wayback snimaka 2022.

## Podaci
- Apify TripAdvisor reviews actor, **svi jezici**, cela istorija (bez sinceDate).
- Polja: ocena, datum objave, ID recenzenta, contributions, helpful votes, jezik, status restorana (Closed).
- Zatvoreni restorani ostaju u uzorku (zatvaranje = ishod).
- Stari radovi (Ivljanin, Ristanović) nemaju datume recenzija → stanje 2022 se rekonstruiše iz novog skupa po datumu.

## Prediktori (na recenzijama ≤ 31.12.2022)
- P0 običan prosek (prikazana ocena)
- P1 Bayesov (skupljen) prosek
- P2 Ristanović formula (naša ocena + 1 − CV)
- P3 ocena korigovana za strogost recenzenta, filter ≥10 recenzija
- P4 I-distance kompozit (indikatori iz concept note-a, uklj. skorašnjost) + bootstrap CI ranga

## Ishodi
- (a) prosečna ocena novih recenzija (glavni: 2023–2026; dodatno: 2026; po godinama)
- (b) broj novih recenzija
- (c) zatvaranje do 2026 (TripAdvisor status + ručna provera)

## Statistika
- Spearman po prediktoru; logistička regresija / AUC za zatvaranje
- Ključni test: P3/P4 vs P0 — bootstrap razlika korelacija na istim restoranima (ili Steiger)
- Holm korekcija; osetljivost: ≥10 kredibilnih recenzija u oba perioda, ponderisanje brojem recenzija
- COVID (2020–2021): proveriti da li isključivanje tog perioda iz prediktora menja rezultate

## Ograničenja
- Contributions/helpful recenzenta su snimak iz 2026 (curenje iz budućnosti) — strogost računati iz recenzija u skupu
- Ishod je na istoj platformi kao prediktor (nema spoljne provere bez Google Maps)
- ~100 restorana → umerena moć za razliku dve korelacije
- 2026 nije cela godina
- Rekonstruisano stanje 2022 ≠ ono što je TA prikazivao 2022 (brisanje/filtriranje recenzija) — proveriti na Wayback snimcima (ocena, broj recenzija) gde postoje
- P3: većina recenzenata ima malo recenzija unutar skupa → prag ≥10 možda neizvodljiv; razmotriti skupljanje ka proseku ili skidanje profila

## Koraci
1. Apify: spisak svih restorana u Beogradu na TA (naziv, URL, location ID, broj recenzija, status, tip) — bez recenzija
2. Gruba selekcija (tip, broj recenzija) → ~200–300 kandidata; provera zatvorenih (+ Wayback dopuna ako treba)
3. Apify skidanje recenzija kandidata → primena kriterijuma ≤ 2022 → stratifikovan nasumičan izbor 100
4. Čišćenje, podela po datumu
5. P0–P4, testovi, osetljivost
6. Pisanje rezultata
