# Odgovor mentora (19. 10. 2026)

Na poruku sa rezultatima koraka 1 i probe koraka 2.

## #1 Obrisane stranice (14 restorana)
Proveriti da li radi dopuna recenzija iz Wayback arhive (moguće da je sačuvana samo prva strana sa deset recenzija).

Predlog, dva sloja:
- **Prvi sloj:** svih 89 restorana sa podacima iz 2018 koje već imamo na nivou restorana, i zatvaranje kao ishod; obrisani restorani su tu najvažniji deo uzorka.
- **Drugi sloj:** restorani sa živim stranicama (72 otvorena + 3 zatvorena sa stranicom), sa punim recenzijama; meri se ocena i obim novih recenzija posle 2018.
- Wayback dopuna: za svih 89 naći snimak stranice restorana najbliži julu 2018 i prepisati prikazanu ocenu, ukupan broj recenzija i histogram ocena (Excellent, Very good, Average, Poor, Terrible). To daje stanje 2018 za sve, uključujući obrisane, i nezavisnu proveru brojeva iz rada.

## #2 Nepotpuna istorija (Burger House i slični)
Plan je u redu. Dodati kolonu `history_complete_ratio` = broj skinutih recenzija do kraja 2018 / broj iz rada iz 2018. Restorani sa odnosom ispod 0,9 idu samo u prvi sloj. Dodati i kolonu `entity_note` (preimenovan, spojen, preseljen), jer je kod preimenovanja pitanje da li je to isti restoran.

## #3 Korisni glasovi recenzenta
Može bez njih. Kao meru kredibiliteta recenzenta koristimo `contributions` (u podacima iz 2018 se skoro poklapala sa korisnim glasovima). Korisne glasove na samoj recenziji zadržati (druga mera: koliko je recenzija pomogla drugima). Ako aktor vraća korisničko ime ili link profila recenzenta, sačuvati i to.

## #4 Dupli unos kafane „?“
U analizi se spajaju u jedan restoran → kohorta ima **88 jedinstvenih lokala**.

## #5 Datum zatvaranja
Za 17 restorana koji ne rade dodati `closure_date_est` i `closure_source` (poslednja recenzija iz keširanog snimka, TA oznaka, vest). Godina i mesec su dovoljni.

## #6 Trošak
U redu je uzeti plaćeni mesec pa otkazati pretplatu. Proveriti da li može da se koristi aktor iz Filipovog diplomskog (Dušan ga je koristio za NYC; naplaćuje vreme izvršavanja, a ne po rezultatu). Ako ne, koristiti dosadašnji. Javiti iznos i broj računa za uplatu.

Kad podaci stignu: poslati sirov JSON i CSV tabele, plus kratak zapis podešavanja aktora (koji aktor, koji parametri) za prilog rada.
