# Plan v2: Ristanovićevih 89 restorana, 2018 → 2026

> Zamenjuje `plan_beograd_2022_2026.md` (odbačen: skidanje svih recenzija ≈ $80–200, budžeta nema).

## Pitanje
Da li je **Ristanovićev rang iz 2018** (ocena korigovana za kredibilitet i strogost recenzenta + konzistentnost)
**bolje predvideo uspeh restorana do 2026** od onoga što je TripAdvisor prikazivao 2018?

To je test koji Ristanović nije uradio: njegov rad samo pokazuje da se rangovi *razlikuju*, ne i koji je *bolji*.

## Uzorak
- **89 beogradskih restorana** iz Ristanovićevog rada (top 100 TA, podaci ~avgust 2018, posle filtera ≥10 kredibilnih recenzija).
- Izvor: `podaci/obradjeni/ristanovic_2019_tabela.csv` (izvučeno iz `materijali/Diplomski rad verzija 3.doc`).
- Ne biramo restorane sami → nema pitanja „zašto baš ovi“; zatvoreni ostaju u uzorku (zatvaranje = ishod).

## Polazno stanje 2018 (već imamo, besplatno)
Iz tabele, za svaki restoran: TA rang, broj svih recenzija, prosek i SD svih recenzija, broj i prosek recenzija
kredibilnih recenzenata (≥10 ukupnih TA recenzija), prosek i SD „naše ocene“, 1 − CV, konačna ocena i rang.

## Prediktori (svi iz tabele 2018)
| | Prediktor | Kolona |
|---|---|---|
| P0 | TA rang 2018 / prosek svih recenzija | `RangTA`, `MeanSvihRecenzija` |
| P1 | Bayesov (skupljen) prosek | iz `brojSvihRecenz` + `MeanSvihRecenzija` |
| P2 | Ristanovićeva konačna ocena | `KONACNA OCENA` |
| P3 | prosek kredibilnih recenzenata; „naša ocena“ (korekcija za strogost) | `MeanRecenzijaVece10`, `MeanNasaOcenaVece10` |
| P4 | I-distance kompozit iz kolona tabele | prosek kredibilnih, „naša ocena“, 1 − CV, log broja kredibilnih, udeo kredibilnih |

Otpada u odnosu na plan v1: bootstrap CI ranga i skorašnjost (traže pojedinačne recenzije).

## Ishodi 2026 (Apify spisak za 89 URL-ova ≈ $0.45, staje u besplatni kredit)
- (a) **prosek novih recenzija 2018 → 2026** = (N₂₀₂₆·m₂₀₂₆ − N₂₀₁₈·m₂₀₁₈) / (N₂₀₂₆ − N₂₀₁₈); m₂₀₂₆ tačno iz `ratingHistogram`
- (b) **broj novih recenzija** N₂₀₂₆ − N₂₀₁₈ (i po godini postojanja)
- (c) **zatvaranje** (`isClosed`/`isLongClosed`, stranica nestala → ručna provera)
- (d) TA rang 2026 (`rankingPosition`) — sporedno

## Statistika
- Spearman svakog prediktora sa (a), (b), (d); logistička regresija / AUC za (c)
- Ključni test: **P2/P3/P4 vs P0** — Steiger test zavisnih korelacija ili bootstrap razlike (resampling restorana)
- Holm korekcija; osetljivost: bez restorana sa < 30 novih recenzija; ponderisanje brojem novih recenzija

## Rizici i ograničenja
- **Jezici:** nije poznato da li je Ristanović skidao sve jezike ili samo engleski → proveriti na Wayback snimku iz 2018 (ukupan broj vs engleski) pre računanja (a)
- **Brisanje recenzija na TA:** N₂₀₂₆ − N₂₀₁₈ može biti potcenjeno ili negativno → označiti, isključiti u osetljivosti
- **Zatvaranje 2018–2026 obuhvata COVID** → zatvaranje nije čist signal kvaliteta; navesti
- **n = 89** → umerena moć za razliku dve korelacije; tumačiti veličinu efekta, ne samo p
- Uzorak je top 100 → suženi raspon ocena (prosek 3.95–4.81; 51–1.853 recenzija) → korelacije prirodno niže
- Tačan datum Ristanovićevog prikupljanja nije naveden (reference: 15.8.2018) → polazna tačka „sredina 2018“

## Koraci
1. **Spajanje naziva sa TA URL-ovima** — nazivi u tabeli su TA slugovi (npr. `Cevap_kod_Dekija`); URL-ove naći preko Wayback CDX liste arhiviranih stranica restorana u Beogradu (besplatno); nepronađene ručno
2. **Provera jezika** na 3–5 Wayback snimaka iz 2018 (besplatno)
3. **Apify** (`maxcopell/tripadvisor`, `startUrls` = 89 URL-ova) → stanje 2026 (≈ $0.45, uz odobrenje)
4. Ručna provera nestalih/zatvorenih
5. Prediktori P0–P4, ishodi, testovi, osetljivost
6. Pisanje rezultata
