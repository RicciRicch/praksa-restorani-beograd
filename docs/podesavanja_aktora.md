# Prikupljanje podataka: Apify aktori i podešavanja (prilog rada)

Svi podaci prikupljeni su preko platforme Apify (https://apify.com) u oktobru 2026.
Za svaki korak naveden je aktor, tačni ulazni parametri (JSON), oznaka pokretanja (run ID) i rezultat,
kako bi postupak mogao da se ponovi. Ulazni fajlovi su u folderu `apify/` repozitorijuma.

## 1. Trenutno stanje restorana (18. 10. 2026)

**Aktor:** `maxcopell/tripadvisor` (Tripadvisor Scraper, Apify) · **run:** `lHqGf8kfgYLCmKlPS`

```json
{
  "startUrls": [{ "url": "https://www.tripadvisor.com/Restaurant_Review-g294472-d8447925-Reviews-Cevap_kod_Dekija-Belgrade.html" }, "… ukupno 89 URL-ova (apify/02_trenutno_stanje_89.json)"],
  "maxItemsPerQuery": 89,
  "includeRestaurants": true,
  "includeHotels": false,
  "includeAttractions": false,
  "includeNearbyResults": false,
  "includeTags": false,
  "includeAiReviewsSummary": false,
  "maxPhotosPerPlace": 0,
  "maximumLeadsEnrichmentRecords": 0,
  "language": "en",
  "currency": "EUR"
}
```

Rezultat: 74 od 89 stranica; za 14 restorana TripAdvisor je obrisao stranicu (ručno provereno u pregledaču),
a jedan unos (Znak Pitanja) je spojen sa drugim (Kafana Question Mark).

## 2. Sve recenzije (19. 10. 2026)

**Aktor:** `kaix/tripadvisor-reviews-scraper` (TripAdvisor Reviews Scraper — Most Comprehensive) · **run:** `XmrN7J2tzBl2igxmc`

```json
{
  "businesses": ["https://www.tripadvisor.com/Restaurant_Review-g294472-d8447925-Reviews-Cevap_kod_Dekija-Belgrade.html", "… ukupno 74 URL-a (apify/04_recenzije_89_kaix.json)"],
  "maxReviews": 0,
  "sortBy": "recent",
  "language": "all",
  "proxyConfiguration": { "useApifyProxy": true }
}
```

| parametar | vrednost | značenje |
|---|---|---|
| `businesses` | 74 URL-a | svi restorani kohorte čija TA stranica postoji (72 otvorena + 3 zatvorena; Znak Pitanja je u Kafana Question Mark) |
| `maxReviews` | `0` | bez ograničenja — cela istorija recenzija |
| `language` | `"all"` | recenzije na svim jezicima |
| `sortBy` | `"recent"` | od najnovije ka najstarijoj |
| bez `since` | – | nema datumskog reza |

Rezultat: **41.256 recenzija** (jednako zbiru `numberOfReviews` na TA za 74 restorana), bez duplikata, najstarija iz decembra 2007.
Korišćena polja izlaza: `id`, `locationId`, `publishedDateISO`, `rating`, `helpfulVotes`, `originalLanguage`, `isTranslated`,
`tripType`, `title`, `text`, `author.userId`, `author.username`, `author.profileUrl`, `author.totalContributions`.

**Napomene za rad:**
- 1,7% tekstova (700 od 41.256) aktor vraća mašinski prevedeno na engleski (`isTranslated = true`); originalni jezik je u `originalLanguage`.
  Ocene, datumi i podaci o recenzentu nisu pogođeni.
- `author.totalContributions` je današnji broj doprinosa recenzenta (stanje u oktobru 2026), ne u trenutku pisanja recenzije.
- Broj korisnih glasova recenzenta (na nivou profila) aktor ne vraća; kao mera kredibiliteta koristi se broj doprinosa.

**Provera aktora (proba, 18–19. 10. 2026):** isti restorani skinuti i aktorom `maxcopell/tripadvisor-reviews`
(Apify; runs `TkevWdelMVCgm8JzB`, `2KWnJ6MGRYhSM8Rp4`, podešavanja: `maxItemsPerQuery: 1000000`,
`reviewsLanguages: ["ALL_REVIEW_LANGUAGES"]`, `disableMachineTranslations: true`, `scrapeReviewerInfo: true`).
Svih 146 zajedničkih recenzija se poklapa po ID-ju, oceni, datumu, korisnim glasovima, jeziku i recenzentu.
Za zatvoreni restoran Little Bay kaix vraća svih 1.113 recenzija; broj do 31. 7. 2018 (789) se slaže sa
brojem iz rada J. Ristanović (805) na 98%.

## 3. Stanje 2018 i obrisani restorani (Wayback Machine)

Bez Apify-ja. Snimci TA stranica restorana sa Internet Archive Wayback Machine (CDX API + `id_` snimci):
- `skripte/07_wayback_2018.py`: snimak najbliži 31. 7. 2018 (prozor ±12 meseci) za svih 89 restorana → ocena,
  broj recenzija, raspodela ocena, rang, adresa;
- `skripte/08_wayback_obrisani.py`: sve sačuvane strane recenzija za 14 restorana čije su stranice obrisane.

## Trošak
| korak | trošak |
|---|---|
| trenutno stanje (89 restorana) | ≈ $0.38 |
| probe (oba aktora) | ≈ $0.80 |
| sve recenzije (kaix, 41.256) | ≈ $2.06 |
| **ukupno** | **≈ $3.3** (besplatni Apify kredit) |
