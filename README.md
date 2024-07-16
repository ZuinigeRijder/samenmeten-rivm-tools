- [Inleiding](#inleiding)
- [Python script gemeente\_station\_namen.py](#python-script-gemeente_station_namenpy)
  - [Voorbeeld van uitvoer voor gemeente Heusden (797)](#voorbeeld-van-uitvoer-voor-gemeente-heusden-797)
- [Python script station\_data\_naar\_csv.py](#python-script-station_data_naar_csvpy)
  - [Voorbeeld van (gedeeltelijke uitvoer), gebruik makend van meetstation namen in \_GemeenteHeusden.txt](#voorbeeld-van-gedeeltelijke-uitvoer-gebruik-makend-van-meetstation-namen-in-_gemeenteheusdentxt)
  - [Voorbeeld van (gedeeltelijke) inhoud van zo een csv bestand, bijvoorbeeld LTD\_54329](#voorbeeld-van-gedeeltelijke-inhoud-van-zo-een-csv-bestand-bijvoorbeeld-ltd_54329)
- [Python script samenvatting.py](#python-script-samenvattingpy)
  - [Voorbeeld voor genereren samenvatting van \_GemeenteHeusden.txt](#voorbeeld-voor-genereren-samenvatting-van-_gemeenteheusdentxt)
  - [Voorbeelden van filteren opties](#voorbeelden-van-filteren-opties)
  - [Gegenereerd .kml bestand](#gegenereerd-kml-bestand)
  - [Voorbeeld van Google Maps op basis van .kml uitvoer](#voorbeeld-van-google-maps-op-basis-van-kml-uitvoer)
  - [Voorbeeld van gegenereerd PM2.5 .csv bestand: \_GemeenteHeusden.txt.pm25.csv](#voorbeeld-van-gegenereerd-pm25-csv-bestand-_gemeenteheusdentxtpm25csv)
  - [Voorbeeld van gegenereerd PM10 .csv bestand: \_GemeenteHeusden.txt.pm10.csv](#voorbeeld-van-gegenereerd-pm10-csv-bestand-_gemeenteheusdentxtpm10csv)
- [Hoe Python, pakketten te installeren](#hoe-python-pakketten-te-installeren)



---
# Inleiding
In [gemeente Heusden](https://samenmeten.rivm.nl/dataportaal/gemeente_tijdreeks.php?gem_id=797) is er ook een samenmeten project en ik wilde weten in hoeverre de fijnstof uitstoot van PM10 en PM2.5 voldoet aan de WHO (World Health Organization) of EU richtlijnen en/of hoever we daarvan af zitten. Ik kon bij de RIVM wel historische data vinden, maar geen actuele informatie. Daarnaast wilde ik gebruik maken van gekalibreerde uurwaardes om zo te berekenen of een meetstation of een groep van meetstations op (lopende) jaarbasis wel of niet aan de richtlijnen voldoen. Daarom heb ik deze python scripts gemaakt en deze beschikbaar gesteld, zodat die door andere ook gebruikt kunnen worden. En eventuele verbeteringen aangebracht kunnen worden.

Er zijn 3 python scripts:
- gemeente_station_namen.py: hiermee kun je meetstation namen van een gemeente achterhalen
- station_data_naar_csv.py: hiermee kun je de uurwaardes van een meeststation of een groep van meetstations ophalen en toevoegen aan reeds beschikbare .csv bestanden
- samenvatting.py: genereert een samenvatting van de jaar waardes (en optioneel maand, week, dag) van een meetstation of groep van meetstations en schrijft deze ook naar een kml bestand, zodat je die in [Google My Maps](https://mymaps.google.com) kunt importeren.

Voorbeeld van de [resultaten van fijnstof van de jaren 2021 tot en met 2024 van gemeente Heusden kun je vinden op Google My Maps](https://www.google.com/maps/d/edit?mid=1nyoEbCk_SXPRRWx5NF0R1Hr0dcx_big&usp=sharing).

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/GemeenteHeusdenFijnstof.png)

Python als programmeertaal heeft het voordeel dat het draait op Windows, Linux en Mac. De python scripts maken gebruik van [https://api-samenmeten.rivm.nl/v1.0](https://samenmeten.nl/dataportaal/api-application-programming-interface) voor het ophalen van de gegevens.

---
# Python script gemeente_station_namen.py
De andere python scripts gebruiken als invoer een bestand met lijst van meetstation namen. In plaats van de meetstation namen van een gemeente allemaal op te zoeken en over te typen, kun je dit script gebruiken als hulpmiddel.

Voer het volgende commando uit voor hulp:
```
python gemeente_station_namen.py

Gebruik  : python gemeente_station_namen.py gemeente_code [debug]
Voorbeeld: python gemeente_station_namen.py 797
PARAMETER: gemeente_code
           b.v. gemeente heusden is code 797
           Zie GemeentenAlfabetisch2022.csv voor de codes voor iedere gemeente.
UITVOER  : namen van stations
```

Zoek in [GemeentenAlfabetisch2022.csv](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/GemeentenAlfabetisch2022.csv) de gemeentecode op en voer dan het volgende commando uit voor een overzicht van stationnamen bij een gemeente.

## Voorbeeld van uitvoer voor gemeente Heusden (797)
```
python gemeente_station_namen.py 797
LTD_78470
LTD_75241
LTD_73365
LTD_73353
LTD_73155
LTD_69527
LTD_68565
LTD_67379
LTD_66698
LTD_66653
LTD_66012
LTD_65989
LTD_65769
LTD_65562
LTD_65341
LTD_65145
LTD_64753
LTD_64764
LTD_64544
LTD_64499
LTD_64345
LTD_64332
LTD_64160
LTD_64106
LTD_63545
GLB_1732427
LTD_63321
LTD_58544
LTD_58547
LTD_58098
LTD_57197
LTD_56098
LTD_56928
LTD_55358
LTD_56607
LTD_55458
LTD_55107
LTD_54636
LTD_54653
LTD_54447
LTD_54329
LTD_54311
LTD_54165
LTD_54087
LTD_51080
LTD_42281
LTD_41242
LTD_41345
```

Deze namen kun je in een bestand zetten, bijvoorbeeld _GemeenteHeusden.txt, die je in de volgende scripts als invoer gebruikt. Natuurlijk kun je hier meetstations uit verwijderen en/of toevoegen van bijvoorbeeld andere gemeentes.


---
# Python script station_data_naar_csv.py
Dit script update per meetstation uit het invoer bestand met meetstation namen een .csv bestand. De eerste keer zal deze alle data ophalen, de volgende keren zal deze nieuwe data toevoegen aan de .csv bestanden per meetstation.

Voer het volgende commando uit voor hulp:
```
python station_data_naar_csv.py

Gebruik  : python station_data_naar_csv.py bestand_met_station_namen.txt [debug]
Voorbeeld: python station_data_naar_csv.py _GemeenteHeusden.txt
INVOER   : bestand_met_station_namen.txt
UITVOER  : voor iedere station in bestand_met_station_namen.txt schrijf .csv bestand

Opmerking: station namen van een gemeente kun je opvragen met:
           python gemeente_station_namen.py gemeente_code
```

## Voorbeeld van (gedeeltelijke uitvoer), gebruik makend van meetstation namen in _GemeenteHeusden.txt
```
python station_data_naar_csv.py _GemeenteHeusden.txt
Ophalen station data voor GLB_1732427
Laatste datum locale tijd: 2024-01-27 11:00 -> iso8601 utc: 2024-01-27T10:00:00.000Z
Uitvoer csv bestand: GLB_1732427.csv
Ophalen data voor type: pm10_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(36530)/Observations
Ophalen data voor type: pm10 https://api-samenmeten.rivm.nl/v1.0/Datastreams(36529)/Observations
Ophalen data voor type: pm25_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(36528)/Observations
Ophalen data voor type: pm25 https://api-samenmeten.rivm.nl/v1.0/Datastreams(36527)/Observations
Geen nieuwe data gevonden sinds 2024-01-27T10:00:00.000Z

Ophalen station data voor LTD_56607
Laatste datum locale tijd: 2024-07-11 14:00 -> iso8601 utc: 2024-07-11T12:00:00.000Z
Uitvoer csv bestand: LTD_56607.csv
Ophalen data voor type: rh https://api-samenmeten.rivm.nl/v1.0/Datastreams(32216)/Observations
Ophalen data voor type: temp https://api-samenmeten.rivm.nl/v1.0/Datastreams(32215)/Observations
Ophalen data voor type: pm10_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(32214)/Observations
Ophalen data voor type: pm10 https://api-samenmeten.rivm.nl/v1.0/Datastreams(32213)/Observations
Ophalen data voor type: pm25_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(32212)/Observations
Ophalen data voor type: pm25 https://api-samenmeten.rivm.nl/v1.0/Datastreams(32211)/Observations
Toevoegen 92 resultaten aan csv bestand

Ophalen station data voor LTD_54329
Laatste datum locale tijd: 2024-07-11 14:00 -> iso8601 utc: 2024-07-11T12:00:00.000Z
Uitvoer csv bestand: LTD_54329.csv
Ophalen data voor type: rh https://api-samenmeten.rivm.nl/v1.0/Datastreams(30665)/Observations
Ophalen data voor type: temp https://api-samenmeten.rivm.nl/v1.0/Datastreams(30664)/Observations
Ophalen data voor type: pm10_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(30663)/Observations
Ophalen data voor type: pm10 https://api-samenmeten.rivm.nl/v1.0/Datastreams(30662)/Observations
Ophalen data voor type: pm25_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(30661)/Observations
Ophalen data voor type: pm25 https://api-samenmeten.rivm.nl/v1.0/Datastreams(30660)/Observations
Toevoegen 92 resultaten aan csv bestand

Ophalen station data voor LTD_57197
Laatste datum locale tijd: 2024-04-26 16:00 -> iso8601 utc: 2024-04-26T14:00:00.000Z
Uitvoer csv bestand: LTD_57197.csv
Ophalen data voor type: rh https://api-samenmeten.rivm.nl/v1.0/Datastreams(32584)/Observations
Ophalen data voor type: temp https://api-samenmeten.rivm.nl/v1.0/Datastreams(32583)/Observations
Ophalen data voor type: pm10_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(32582)/Observations
Ophalen data voor type: pm10 https://api-samenmeten.rivm.nl/v1.0/Datastreams(32581)/Observations
Ophalen data voor type: pm25_kal https://api-samenmeten.rivm.nl/v1.0/Datastreams(32580)/Observations
Ophalen data voor type: pm25 https://api-samenmeten.rivm.nl/v1.0/Datastreams(32579)/Observations
Geen nieuwe data gevonden sinds 2024-04-26T14:00:00.000Z
.....
```

## Voorbeeld van (gedeeltelijke) inhoud van zo een csv bestand, bijvoorbeeld LTD_54329
```
datetime,pm10 kal,pm10,pm2.5 kal,pm2.5,rh%,temp
2021-11-21 13:00,6.942,8.88,2.574,1.76,68.32,12.33
2021-11-21 14:00,10.3,10.04,2.988,1.78,76.87,9.77
2021-11-21 15:00,8.32,6.42,,1.38,80.07,8.98
2021-11-21 16:00,10.2,7.47,2.828,1.38,77.91,8.64
2021-11-21 17:00,10.439,7.26,2.52,1.41,79.73,8.05
2021-11-21 18:00,8.82,7.01,2.048,1.63,80.76,7.18
2021-11-21 19:00,6.88,7.99,,2.5,81.3,6.54
2021-11-21 20:00,8.736,10.38,4.096,3.19,81.34,5.22
...
2023-09-17 04:00,12.015,13.5,8.091,8.69,97.26,17.62
2023-09-17 05:00,11.543,11.94,6.12,8.48,95.51,17.03
2023-09-17 06:00,12.556,14.19,4.949,9.92,99.93,16.2
2023-09-17 07:00,9.384,18.38,5.13,13.48,100.0,15.71
2023-09-17 08:00,10.812,21.17,7.009,16.3,100.0,15.84
```

---
# Python script samenvatting.py
Dit script genereert een samenvatting per meetstation uit het invoer bestand met meetstation namen en gebruikt hiervoor de .csv bestanden die geupdate zijn uit het vorige script. Daarnaast wordt er ook een .kml bestand gemaakt, die je in [Google My Maps](https://mymaps.google.com) kunt importeren. Om een mooie spreadsheet grafiek te maken, wordt er ook een PM2.5.csv en PM10.csv bestand gegenereerd.

Voer het volgende commando uit voor hulp:
```
python samenvatting.py
Onbekend invoer bestand:

Gebruik  : python samenvatting.py STATION_LIJST.txt
Voorbeeld: python samenvatting.py _GemeenteHeusden.txt
Opties   : [uur] [dag] [week] [maand] [j2000-3000] [m1-12] [u0-23]

Opm.1: Wilt u meer details zien, gebruik parameter uur/dag/week/maand
Opm.2: Wilt u alleen bepaalde jaren mee te nemen,
       kunt u filteren met optie [j2000-3000]:
       bijvoorbeeld alleen jaren 2021 tot en met 2022: j2021-2022
Opm.3: Wilt u alleen bepaalde maanden mee te nemen,
       kunt u filteren met optie [m1-12]:
       bijvoorbeeld alleen de maanden november tot en met maart: m11-3
Opm.4: Wilt u alleen bepaalde uren mee te nemen,
       kunt u filteren met optie [u0-23]:
       bijvoorbeeld alleen de uren van 18:00 tot en met 02:00: u18-2
Opm.5: station namen van een gemeente kan opgevraagd worden met tool:
            python gemeente_station_namen.py gemeente_code
Opm.6: Voordat dit script gedraaid wordt, moeten de .csv bestanden voor
       deze STATION_LIJST.txt gegenereerd zijn met:
            python station_data_naar_csv.py STATION_LIJST.txt
```

## Voorbeeld voor genereren samenvatting van _GemeenteHeusden.txt
```
python samenvatting.py _GemeenteHeusden.txt
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar
  LTD_54311,  JAAR    36d/   25d, 2021-12-31,    2021,  16.4,    2,   93,    0,    0,  16.7,    2,   91,    18, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54311,  JAAR   334d/  204d, 2022-12-31,    2022,  19.5,    2,  949,   10,    9,  16.5,    1,  732,   143, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54311,  JAAR   341d/  303d, 2023-12-31,    2023,  16.9,    1,  124,    6,    4,  11.9,    1,   90,    73, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54311,  JAAR   180d/  178d, 2024-07-15,    2024,  15.8,    1,  118,    0,    0,  14.0,    1,   93,    63, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54311, ALLES   892d/  713d,           ,   alles,  17.7,    0,  949,   10,    9,  14.0,    0,  732,   143, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_56607,  JAAR   323d/  196d, 2022-12-31,    2022,  15.6,    1,  148,    9,    5,  11.6,    1,   60,    73, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_56607,  JAAR   341d/  304d, 2023-12-31,    2023,  13.4,    1,  104,    3,    1,   8.2,    1,   60,    37, PM2.5 > WHO jaar 5
  LTD_56607,  JAAR   181d/  180d, 2024-07-15,    2024,  12.8,    1,  111,    0,    0,   9.9,    0,   78,    35, PM2.5 > WHO jaar 5
  LTD_56607, ALLES   846d/  681d,           ,   alles,  14.2,    0,  148,    9,    5,   9.7,    0,   78,    73, PM10  > WHO dag #9; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

GLB_1732427,  JAAR   103d/   68d, 2022-12-31,    2022,  39.9,    0, 1000,   12,   12,  41.4,    0, 1000,    40, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5 > EU jaar 25
GLB_1732427,  JAAR   324d/  302d, 2023-12-31,    2023,   8.8,    0,  107,    1,    1,   8.0,    0,   91,    54, PM2.5 > WHO jaar 5
GLB_1732427,  JAAR     1d/   24d, 2024-01-27,    2024,  17.3,    1,   45,    0,    0,   8.6,    0,   64,     3, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
GLB_1732427, ALLES   429d/  395d,           ,   alles,  16.4,    0, 1000,   12,   12,  13.9,    0, 1000,    54, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_54329,  JAAR    36d/   26d, 2021-12-31,    2021,  12.1,    1,   66,    0,    0,   9.3,    1,   69,     7, PM2.5 > WHO jaar 5
  LTD_54329,  JAAR   305d/  188d, 2022-12-31,    2022,  15.5,    2,  144,    0,    0,   8.8,    0,  119,    47, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54329,  JAAR   337d/  300d, 2023-12-31,    2023,  14.1,    1,   88,    0,    0,   6.0,    0,   54,    14, PM2.5 > WHO jaar 5
  LTD_54329,  JAAR   182d/  180d, 2024-07-15,    2024,  12.4,    1,  100,    0,    0,   6.6,    0,   66,    10, PM2.5 > WHO jaar 5
  LTD_54329, ALLES   861d/  695d,           ,   alles,  14.2,    0,  144,    0,    0,   7.1,    0,  119,    47, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_57197,  JAAR   310d/  187d, 2022-12-31,    2022,  18.5,    3,  155,    6,    3,   9.2,    1,   54,    44, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_57197,  JAAR   339d/  302d, 2023-12-31,    2023,  15.7,    2,  193,    1,    0,   6.6,    1,   58,    17, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_57197,  JAAR    37d/   37d, 2024-04-26,    2024,  12.4,    2,   74,    0,    0,   6.1,    1,  136,     4, PM2.5 > WHO jaar 5
  LTD_57197, ALLES   687d/  527d,           ,   alles,  16.9,    0,  193,    6,    3,   7.6,    0,  136,    44, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64753,  JAAR    53d/   33d, 2022-12-31,    2022,  17.7,    4,  143,    1,    0,  10.1,    1,   77,    16, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_64753,  JAAR   340d/  302d, 2023-12-31,    2023,  14.7,    2,  359,    0,    0,   6.3,    0,   96,    18, PM2.5 > WHO jaar 5
  LTD_64753,  JAAR   182d/  180d, 2024-07-15,    2024,  13.4,    1,  101,    0,    0,   7.1,    0,   70,    14, PM2.5 > WHO jaar 5
  LTD_64753, ALLES   576d/  516d,           ,   alles,  14.6,    0,  359,    1,    0,   6.9,    0,   96,    18, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_58098,  JAAR   289d/  173d, 2022-12-31,    2022,  18.8,    1,  101,    9,    5,  11.0,    1,   69,    59, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58098,  JAAR   342d/  304d, 2023-12-31,    2023,  17.5,    2,  171,    7,    6,   8.6,    1,   94,    39, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58098,  JAAR   180d/  179d, 2024-07-15,    2024,  16.5,    2,  113,    1,    0,  10.3,    0,   76,    35, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58098, ALLES   812d/  657d,           ,   alles,  17.8,    0,  171,    9,    6,   9.8,    0,   94,    59, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_65989,  JAAR    19d/   11d, 2022-12-31,    2022,  21.4,    4,   81,    1,    0,  11.8,    1,   50,     7, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65989,  JAAR   342d/  304d, 2023-12-31,    2023,  16.8,    2,  103,    3,    0,   7.6,    1,   81,    28, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65989,  JAAR   182d/  180d, 2024-07-15,    2024,  15.6,    2,  124,    0,    0,   8.5,    0,   74,    23, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65989, ALLES   543d/  496d,           ,   alles,  16.7,    0,  124,    3,    0,   8.1,    0,   81,    28, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_54087,  JAAR    40d/   28d, 2021-12-31,    2021,  12.4,    1,   56,    0,    0,   9.0,    1,   60,     5, PM2.5 > WHO jaar 5
  LTD_54087,  JAAR   334d/  204d, 2022-12-31,    2022,  13.6,    1,  124,    0,    0,   9.2,    0,   67,    49, PM2.5 > WHO jaar 5
  LTD_54087,  JAAR   336d/  299d, 2023-12-31,    2023,  12.3,    1,  164,    0,    0,   6.8,    0,   75,    22, PM2.5 > WHO jaar 5
  LTD_54087,  JAAR   181d/  180d, 2024-07-15,    2024,  11.3,    1,   94,    0,    0,   7.6,    0,   78,    18, PM2.5 > WHO jaar 5
  LTD_54087, ALLES   892d/  713d,           ,   alles,  12.6,    0,  164,    0,    0,   7.9,    0,   78,    49, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64499,  JAAR    66d/   42d, 2022-12-31,    2022,  15.8,    3,   65,    0,    0,   9.8,    1,   45,    16, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_64499,  JAAR   342d/  304d, 2023-12-31,    2023,  14.2,    1,   88,    0,    0,   7.0,    0,   57,    27, PM2.5 > WHO jaar 5
  LTD_64499,  JAAR   182d/  180d, 2024-07-15,    2024,  13.1,    1,  107,    0,    0,   8.0,    0,   79,    18, PM2.5 > WHO jaar 5
  LTD_64499, ALLES   591d/  527d,           ,   alles,  14.1,    0,  107,    0,    0,   7.6,    0,   79,    27, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_54636,  JAAR    29d/   20d, 2021-12-31,    2021,  11.6,    1,   44,    0,    0,   9.0,    1,   37,     4, PM2.5 > WHO jaar 5
  LTD_54636,  JAAR   334d/  204d, 2022-12-31,    2022,  14.1,    1,  249,    0,    0,   9.5,    0,   61,    56, PM2.5 > WHO jaar 5
  LTD_54636,  JAAR   336d/  299d, 2023-12-31,    2023,  12.3,    0,  201,    1,    0,   6.7,    0,   78,    26, PM2.5 > WHO jaar 5
  LTD_54636,  JAAR   182d/  180d, 2024-07-15,    2024,  10.8,    0,  100,    0,    0,   7.4,    0,   65,    19, PM2.5 > WHO jaar 5
  LTD_54636, ALLES   882d/  705d,           ,   alles,  12.7,    0,  249,    1,    0,   7.8,    0,   78,    56, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64106,  JAAR    77d/   48d, 2022-12-31,    2022,  14.4,    2,   62,    0,    0,   8.0,    1,   42,    11, PM2.5 > WHO jaar 5
  LTD_64106,  JAAR   330d/  295d, 2023-12-31,    2023,  13.5,    1,   89,    0,    0,   6.0,    0,   52,    17, PM2.5 > WHO jaar 5
  LTD_64106,  JAAR   181d/  180d, 2024-07-15,    2024,  12.5,    1,  298,    0,    0,   7.0,    0,   62,    14, PM2.5 > WHO jaar 5
  LTD_64106, ALLES   590d/  524d,           ,   alles,  13.4,    0,  298,    0,    0,   6.6,    0,   62,    17, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_73155,  JAAR    83d/   82d, 2023-12-31,    2023,   8.1,    1,   55,    0,    0,   5.0,    1,   56,     0,
  LTD_73155,  JAAR   180d/  179d, 2024-07-15,    2024,   8.8,    1,  126,    0,    0,   5.7,    0,   92,     7, PM2.5 > WHO jaar 5
  LTD_73155, ALLES   264d/  262d,           ,   alles,   8.8,    0,  126,    0,    0,   5.6,    0,   92,     7, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_73365,  JAAR    68d/   68d, 2023-12-31,    2023,   8.1,    1,   42,    0,    0,   4.9,    0,   25,     1,
  LTD_73365,  JAAR   182d/  180d, 2024-07-15,    2024,   9.4,    0,   88,    0,    0,   5.8,    0,   62,    11, PM2.5 > WHO jaar 5
  LTD_73365, ALLES   250d/  249d,           ,   alles,   9.2,    0,   88,    0,    0,   5.7,    0,   62,    11, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_54653,  JAAR    30d/   22d, 2021-12-31,    2021,   9.6,    1,   33,    0,    0,   8.3,    1,   30,     3, PM2.5 > WHO jaar 5
  LTD_54653,  JAAR   197d/  126d, 2022-12-31,    2022,  12.9,    1,  120,    0,    0,   9.9,    0,   51,    43, PM2.5 > WHO jaar 5
  LTD_54653,  JAAR   179d/  143d, 2023-12-31,    2023,  11.1,    1,   80,    0,    0,   7.2,    0,   51,    13, PM2.5 > WHO jaar 5
  LTD_54653,  JAAR   182d/  180d, 2024-07-15,    2024,   9.6,    0,   83,    0,    0,   7.4,    0,   70,    15, PM2.5 > WHO jaar 5
  LTD_54653, ALLES   590d/  472d,           ,   alles,  11.2,    0,  120,    0,    0,   8.1,    0,   70,    43, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_55458,  JAAR     6d/    5d, 2021-12-26,    2021,   5.3,    1,   18,    0,    0,   4.1,    1,   20,     0,
  LTD_55458,  JAAR     0d/    0d, 2022-01-13,    2022,   6.4,    5,    7,    0,    0,   5.0,    5,    5,     0,
  LTD_55458, ALLES     6d/    5d,           ,   alles,  11.3,    0,   18,    0,    0,  12.1,    0,   20,     0, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_55107,  JAAR    15d/   11d, 2021-12-31,    2021,   8.4,    1,   30,    0,    0,   8.6,    2,   31,     2, PM2.5 > WHO jaar 5
  LTD_55107,  JAAR   266d/  162d, 2022-11-01,    2022,  12.1,    1,   74,    0,    0,  10.0,    0,   55,    41, PM2.5 > WHO jaar 5
  LTD_55107,  JAAR   224d/  206d, 2023-12-31,    2023,   9.7,    1,  146,    0,    0,   6.9,    0,   50,    16, PM2.5 > WHO jaar 5
  LTD_55107,  JAAR   181d/  180d, 2024-07-15,    2024,   9.4,    1,   70,    0,    0,   8.2,    0,   64,    22, PM2.5 > WHO jaar 5
  LTD_55107, ALLES   687d/  560d,           ,   alles,  10.6,    0,  146,    0,    0,   8.3,    0,   64,    41, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_58544,  JAAR   269d/  162d, 2022-12-31,    2022,  16.0,    2,  310,    6,    2,  10.5,    1,  125,    53, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58544,  JAAR   246d/  209d, 2023-09-22,    2023,  16.6,    1,  128,    5,    4,   8.8,    1,   76,    33, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58544, ALLES   516d/  371d,           ,   alles,  16.4,    0,  310,    6,    4,   9.6,    0,  125,    53, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_65562,  JAAR    32d/   19d, 2022-12-31,    2022,  15.7,    2,   57,    0,    0,  10.3,    1,   37,    10, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65562,  JAAR   340d/  302d, 2023-12-31,    2023,  10.6,    0,   76,    0,    0,   5.0,    0,   53,     7, PM2.5 > WHO jaar 5
  LTD_65562,  JAAR   182d/  180d, 2024-07-15,    2024,   9.3,    1,   90,    0,    0,   5.6,    0,   61,     7, PM2.5 > WHO jaar 5
  LTD_65562, ALLES   555d/  503d,           ,   alles,  10.5,    0,   90,    0,    0,   5.5,    0,   61,    10, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_41345,  JAAR   327d/  249d, 2021-12-31,    2021,  10.7,    0,  192,    2,    1,   6.0,    0,   66,    28, PM2.5 > WHO jaar 5
  LTD_41345,  JAAR   327d/  200d, 2022-12-31,    2022,  21.4,    2, 1764,   19,   16,  13.8,    0, 1622,    89, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_41345,  JAAR   182d/  159d, 2023-08-27,    2023,  93.7,    2, 1522,   78,   73,  85.5,    1, 1458,   152, PM10  > WHO jaar 15 > EU jaar 40; PM2.5 > WHO jaar 5 > EU jaar 25
  LTD_41345, ALLES   837d/  609d,           ,   alles,  33.1,    0, 1764,   78,   73,  29.5,    0, 1622,   152, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5 > EU jaar 25
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_68565,  JAAR   275d/  263d, 2023-12-31,    2023,   6.8,    1,   63,    0,    0,   4.1,    0,   40,     1,
  LTD_68565,  JAAR   182d/  180d, 2024-07-15,    2024,   6.4,    0,   50,    0,    0,   4.7,    0,   37,     3,
  LTD_68565, ALLES   458d/  443d,           ,   alles,   6.7,    0,   63,    0,    0,   4.4,    0,   40,     3,
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_63545,  JAAR    97d/   64d, 2022-12-31,    2022,  20.4,    3,  117,    2,    1,  11.0,    1,   77,    25, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_63545,  JAAR   314d/  279d, 2023-12-31,    2023,  18.0,    1,  383,    6,    1,   8.3,    1,   70,    33, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_63545,  JAAR   118d/  117d, 2024-05-16,    2024,  17.9,    2,  110,    2,    2,  10.3,    0,   67,    25, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_63545, ALLES   529d/  461d,           ,   alles,  18.5,    0,  383,    6,    2,   9.3,    0,   77,    33, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64160,  JAAR    77d/   48d, 2022-12-31,    2022,  10.8,    2,   43,    0,    0,   6.1,    1,   34,     3, PM2.5 > WHO jaar 5
  LTD_64160,  JAAR   342d/  304d, 2023-12-31,    2023,  10.8,    2,   85,    0,    0,   5.0,    1,   42,     4,
  LTD_64160,  JAAR   182d/  180d, 2024-07-15,    2024,  10.4,    2,   66,    0,    0,   5.8,    0,   44,     4, PM2.5 > WHO jaar 5
  LTD_64160, ALLES   601d/  533d,           ,   alles,  10.8,    0,   85,    0,    0,   5.4,    0,   44,     4, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_51080,  JAAR    17d/   12d, 2021-12-31,    2021,  15.6,    3,   38,    0,    0,  11.6,    1,   61,     8, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_51080,  JAAR   227d/  137d, 2022-12-12,    2022,  14.9,    0,  321,    2,    2,   9.2,    0,  112,    35, PM2.5 > WHO jaar 5
  LTD_51080,  JAAR    73d/   52d, 2023-05-04,    2023,   7.8,    0,   78,    1,    0,   4.1,    0,   57,    10, PM2.5 > WHO dag #10
  LTD_51080, ALLES   318d/  203d,           ,   alles,  13.4,    0,  321,    2,    2,   8.2,    0,  112,    35, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_78470,  JAAR    28d/   27d, 2024-05-30,    2024,   9.1,    1,   58,    0,    0,   6.6,    0,   43,     0, PM2.5 > WHO jaar 5
  LTD_78470, ALLES    28d/   27d,           ,   alles,  10.6,    0,   58,    0,    0,   8.1,    0,   43,     0, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64764,  JAAR    56d/   35d, 2022-12-31,    2022,  13.2,    2,   63,    0,    0,   7.3,    1,   36,     6, PM2.5 > WHO jaar 5
  LTD_64764,  JAAR   262d/  234d, 2023-12-31,    2023,  11.3,    2,   66,    0,    0,   5.1,    0,   43,     5, PM2.5 > WHO jaar 5
  LTD_64764,  JAAR   182d/  180d, 2024-07-15,    2024,  11.8,    2,   95,    0,    0,   6.2,    0,   57,    11, PM2.5 > WHO jaar 5
  LTD_64764, ALLES   501d/  450d,           ,   alles,  11.8,    0,   95,    0,    0,   5.8,    0,   57,    11, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_66653,  JAAR   338d/  302d, 2023-12-31,    2023,  10.8,    1,  107,    0,    0,   5.8,    0,   59,    13, PM2.5 > WHO jaar 5
  LTD_66653,  JAAR   182d/  180d, 2024-07-15,    2024,   9.3,    1,   82,    0,    0,   5.9,    0,   54,     8, PM2.5 > WHO jaar 5
  LTD_66653, ALLES   520d/  483d,           ,   alles,  10.3,    0,  107,    0,    0,   5.9,    0,   59,    13, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_65145,  JAAR    45d/   28d, 2022-12-31,    2022,  16.4,    2,   68,    0,    0,  10.8,    1,   49,    15, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65145,  JAAR   339d/  302d, 2023-12-31,    2023,  11.8,    1,   79,    1,    0,   6.1,    0,   55,    17, PM2.5 > WHO jaar 5
  LTD_65145,  JAAR   181d/  180d, 2024-07-15,    2024,  10.9,    1,  102,    0,    0,   6.8,    0,   64,    14, PM2.5 > WHO jaar 5
  LTD_65145, ALLES   566d/  510d,           ,   alles,  11.9,    0,  102,    1,    0,   6.7,    0,   64,    17, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_54447,  JAAR    34d/   24d, 2021-12-31,    2021,  10.8,    1,   50,    0,    0,   8.6,    1,   36,     5, PM2.5 > WHO jaar 5
  LTD_54447,  JAAR   334d/  205d, 2022-12-31,    2022,  13.8,    1,  701,    0,    0,   9.0,    0,  268,    50, PM2.5 > WHO jaar 5
  LTD_54447,  JAAR   246d/  212d, 2023-12-31,    2023,  12.8,    1,  183,    0,    0,   7.1,    0,   60,    18, PM2.5 > WHO jaar 5
  LTD_54447,  JAAR   153d/  152d, 2024-07-15,    2024,  11.0,    1,   86,    0,    0,   7.3,    0,   62,    15, PM2.5 > WHO jaar 5
  LTD_54447, ALLES   770d/  595d,           ,   alles,  12.9,    0,  701,    0,    0,   7.9,    0,  268,    50, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_54165,  JAAR    33d/   24d, 2021-12-31,    2021,   6.5,    0,   25,    0,    0,   5.4,    1,   23,     1, PM2.5 > WHO jaar 5
  LTD_54165,  JAAR   325d/  198d, 2022-12-19,    2022,   9.0,    1,   42,    0,    0,   6.3,    0,   37,    17, PM2.5 > WHO jaar 5
  LTD_54165,  JAAR   341d/  304d, 2023-12-31,    2023,   8.0,    0,   52,    0,    0,   4.6,    0,   43,     4,
  LTD_54165,  JAAR   182d/  180d, 2024-07-15,    2024,   7.4,    0,   54,    0,    0,   5.1,    0,   33,     4, PM2.5 > WHO jaar 5
  LTD_54165, ALLES   882d/  707d,           ,   alles,   8.2,    0,   54,    0,    0,   5.3,    0,   43,    17, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_55358,  JAAR   303d/  183d, 2022-12-31,    2022,  14.7,    2,  277,    4,    1,  10.0,    0,   66,    56, PM2.5 > WHO jaar 5
  LTD_55358,  JAAR   331d/  294d, 2023-12-31,    2023,  13.2,    1,  160,    0,    0,   7.8,    0,  161,    31, PM2.5 > WHO jaar 5
  LTD_55358,  JAAR   146d/  145d, 2024-07-15,    2024,  12.0,    1,   91,    0,    0,   8.3,    0,   67,    24, PM2.5 > WHO jaar 5
  LTD_55358, ALLES   781d/  623d,           ,   alles,  13.6,    0,  277,    4,    1,   8.7,    0,  161,    56, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64345,  JAAR    70d/   44d, 2022-12-31,    2022,  14.0,    3,   59,    0,    0,   7.6,    1,   35,    10, PM2.5 > WHO jaar 5
  LTD_64345,  JAAR   342d/  304d, 2023-12-31,    2023,  12.3,    2,   67,    0,    0,   5.6,    0,   39,     9, PM2.5 > WHO jaar 5
  LTD_64345,  JAAR   181d/  180d, 2024-07-15,    2024,  11.4,    2,   53,    0,    0,   6.0,    0,   40,     8, PM2.5 > WHO jaar 5
  LTD_64345, ALLES   594d/  529d,           ,   alles,  12.3,    0,   67,    0,    0,   6.0,    0,   40,    10, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_66698,  JAAR   321d/  290d, 2023-12-31,    2023,  16.0,    2,  648,    2,    1,   6.8,    1,  371,    19, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_66698,  JAAR   181d/  180d, 2024-07-15,    2024,  14.1,    2,   86,    0,    0,   7.0,    0,   93,    12, PM2.5 > WHO jaar 5
  LTD_66698, ALLES   503d/  470d,           ,   alles,  15.4,    0,  648,    2,    1,   7.0,    0,  371,    19, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_63321,  JAAR   103d/   68d, 2022-12-31,    2022,  16.3,    2,  722,    1,    1,  10.1,    1,   47,    23, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_63321,  JAAR   337d/  301d, 2023-12-31,    2023,  15.0,    1,  444,    3,    1,   8.2,    0,   98,    41, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_63321,  JAAR   182d/  180d, 2024-07-15,    2024,  13.6,    1,  101,    0,    0,   9.1,    0,   72,    29, PM2.5 > WHO jaar 5
  LTD_63321, ALLES   623d/  551d,           ,   alles,  14.9,    0,  722,    3,    1,   8.8,    0,   98,    41, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_73353,  JAAR    71d/   71d, 2023-12-31,    2023,  11.2,    1,   79,    0,    0,   6.8,    0,   45,     6, PM2.5 > WHO jaar 5
  LTD_73353,  JAAR   181d/  180d, 2024-07-15,    2024,  11.4,    1,  115,    0,    0,   6.7,    0,   54,    13, PM2.5 > WHO jaar 5
  LTD_73353, ALLES   252d/  251d,           ,   alles,  11.5,    0,  115,    0,    0,   6.9,    0,   54,    13, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_75241,  JAAR     0d/    0d, 2023-12-31,    2023,  12.4,    4,   21,    0,    0,   8.6,    2,   22,     0, PM2.5 > WHO jaar 5
  LTD_75241,  JAAR   181d/  179d, 2024-07-15,    2024,  14.6,    1,  120,    1,    0,   9.8,    0,   80,    36, PM2.5 > WHO jaar 5
  LTD_75241, ALLES   181d/  180d,           ,   alles,  14.8,    0,  120,    1,    0,  10.1,    0,   80,    36, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_56928,  JAAR   133d/   79d, 2022-12-10,    2022,  18.7,    3,   90,    2,    1,  12.2,    1,   53,    48, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_56928,  JAAR   242d/  209d, 2023-12-16,    2023,  13.0,    1,  185,    0,    0,   7.2,    1,   58,    23, PM2.5 > WHO jaar 5
  LTD_56928,  JAAR   143d/  141d, 2024-07-15,    2024,  10.7,    1,   67,    0,    0,   7.2,    0,   49,    12, PM2.5 > WHO jaar 5
  LTD_56928, ALLES   519d/  430d,           ,   alles,  13.9,    0,  185,    2,    1,   8.3,    0,   58,    48, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64544,  JAAR    61d/   38d, 2022-12-31,    2022,  13.6,    2,   48,    0,    0,   8.2,    0,   36,    11, PM2.5 > WHO jaar 5
  LTD_64544,  JAAR   312d/  277d, 2023-12-31,    2023,  12.5,    2,  111,    0,    0,   5.9,    0,   61,    14, PM2.5 > WHO jaar 5
  LTD_64544,  JAAR    98d/   97d, 2024-05-25,    2024,  12.7,    2,   98,    0,    0,   8.3,    0,   49,    16, PM2.5 > WHO jaar 5
  LTD_64544, ALLES   472d/  414d,           ,   alles,  12.8,    0,  111,    0,    0,   6.8,    0,   61,    16, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_41242,  JAAR     5d/    5d, 2021-01-24,    2021,   5.5,    1,   17,    0,    0,   2.4,    1,    8,     0,
  LTD_41242, ALLES     5d/    5d,           ,   alles,  12.9,    0,   17,    0,    0,   9.8,    0,    8,     0, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_42281,  JAAR    21d/   21d, 2021-02-18,    2021,  26.1,    4,  216,    3,    1,  15.9,    2,   54,    11, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_42281, ALLES    21d/   21d,           ,   alles,  28.0,    0,  216,    3,    1,  17.8,    0,   54,    11, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_56098,  JAAR     1d/    1d, 2022-03-05,    2022,   6.2,    2,   14,    0,    0,   4.3,    2,   10,     0,
  LTD_56098, ALLES     1d/    1d,           ,   alles,  29.4,    0,   14,    0,    0,  40.0,    0,   10,     0, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5 > EU jaar 25
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_58547,  JAAR   175d/  107d, 2022-12-22,    2022,  15.8,    2,   84,    3,    1,   9.7,    1,   71,    28, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58547,  JAAR     3d/    2d, 2023-01-23,    2023,  12.8,    3,   29,    0,    0,   7.8,    2,   26,     2, PM2.5 > WHO jaar 5
  LTD_58547, ALLES   179d/  109d,           ,   alles,  16.0,    0,   84,    3,    1,  10.0,    0,   71,    28, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_64332,  JAAR    72d/   45d, 2022-12-31,    2022,  15.6,    2,   75,    0,    0,   8.8,    1,   48,    14, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_64332,  JAAR   251d/  215d, 2023-12-31,    2023,  14.4,    2,   98,    0,    0,   6.7,    0,   51,    20, PM2.5 > WHO jaar 5
  LTD_64332,  JAAR   182d/  180d, 2024-07-15,    2024,  13.6,    2,  110,    0,    0,   7.2,    0,   83,    18, PM2.5 > WHO jaar 5
  LTD_64332, ALLES   506d/  442d,           ,   alles,  14.4,    0,  110,    0,    0,   7.2,    0,   83,    20, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_67379,  JAAR   135d/  109d, 2023-06-26,    2023,  12.3,    1,   71,    0,    0,   7.2,    0,   53,     9, PM2.5 > WHO jaar 5
  LTD_67379,  JAAR     1d/    1d, 2024-03-29,    2024,   4.8,    1,   18,    0,    0,   1.5,    0,   11,     0,
  LTD_67379, ALLES   137d/  110d,           ,   alles,  12.6,    0,   71,    0,    0,   7.5,    0,   53,     9, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_65769,  JAAR     7d/    4d, 2022-12-11,    2022,  16.2,    3,   77,    0,    0,   8.5,    1,   34,     2, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65769, ALLES     7d/    4d,           ,   alles,  22.1,    0,   77,    0,    0,  17.8,    0,   34,     2, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_66012,  JAAR    18d/   11d, 2022-12-31,    2022,  13.6,    3,   52,    0,    0,   7.2,    1,   31,     2, PM2.5 > WHO jaar 5
  LTD_66012,  JAAR   205d/  169d, 2023-12-31,    2023,  12.3,    2,   84,    0,    0,   5.6,    1,   68,     4, PM2.5 > WHO jaar 5
  LTD_66012,  JAAR   176d/  175d, 2024-07-15,    2024,  11.1,    2,  124,    0,    0,   5.7,    0,  222,     7, PM2.5 > WHO jaar 5
  LTD_66012, ALLES   400d/  355d,           ,   alles,  11.9,    0,  124,    0,    0,   5.9,    0,  222,     7, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_65341,  JAAR     5d/    3d, 2022-11-26,    2022,  32.9,    6,   85,    2,    0,  20.8,    7,   53,     6, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65341, ALLES     5d/    3d,           ,   alles,  40.1,    0,   85,    2,    0,  31.6,    0,   53,     6, PM10  > WHO jaar 15 > EU jaar 40; PM2.5 > WHO jaar 5 > EU jaar 25
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_69527,  JAAR    95d/   94d, 2023-12-31,    2023,   7.7,    1,   88,    0,    0,   4.4,    0,   60,     1,
  LTD_69527,  JAAR   167d/  165d, 2024-07-15,    2024,   7.5,    1,   89,    0,    0,   4.4,    0,   52,     2,
  LTD_69527, ALLES   262d/  260d,           ,   alles,   7.7,    0,   89,    0,    0,   4.6,    0,   60,     2,
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

 Gemiddelde,  JAAR   636d/  478d,           ,    2021,  11.5,    0,  216,    3,    1,   7.9,    0,   91,    28, PM2.5 > WHO jaar 5
 Gemiddelde,  JAAR  5762d/ 3541d,           ,    2022,  16.0,    0, 1764,   19,   16,  10.8,    0, 1622,   143, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
 Gemiddelde,  JAAR 10568d/ 9396d,           ,    2023,  14.3,    0, 1522,   78,   73,   8.1,    0, 1458,   152, PM10  > WHO dag #78 > EU dag #73; PM2.5 > WHO jaar 5
 Gemiddelde,  JAAR  5982d/ 5960d,           ,    2024,  11.7,    0,  298,    2,    2,   7.3,    0,  222,    63, PM2.5 > WHO jaar 5
 Gemiddelde, ALLES 22949d/19376d,           ,   alles,  14.0,    0, 1764,   78,   73,   8.3,    0, 1622,   152, PM10  > WHO dag #78 > EU dag #73; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar
```

## Voorbeelden van filteren opties
Je kunt ook alleen een samenvatting genereren van een of meerdere volledige jaren, bijvoorbeeld 2021 en 2022:
```
python samenvatting.py j2021-2022 _GemeenteHeusden.txt
```

Je kunt ook alleen een samenvatting genereren van bepaalde maanden, bijvoorbeeld november tot en met maart:
```
python samenvatting.py m11-3 _GemeenteHeusden.txt
```

Je kunt ook alleen een samenvatting genereren van bepaalde uren, bijvoorbeeld van 18:00 tot en met 04:00:
```
python samenvatting.py u18-4 _GemeenteHeusden.txt
```

En je kunt de jaar-, maand- en uur-filters ook combineren.
```
python samenvatting.py j2021-2022 u18-4 m11-3 _GemeenteHeusden.txt
```

## Gegenereerd .kml bestand
Het uitvoer kml bestand (de naam van je invoer bestand met extensie .kml, bijvoorbeeld _GemeenteHeusden.txt.kml) kun je importeren in [Google My Maps](https://mymaps.google.com).

## Voorbeeld van Google Maps op basis van .kml uitvoer
Voorbeeld van de [resultaten van fijnstof over 2021 tot en met 2024 van gemeente Heusden kun je hier vinden op Google My Maps](https://www.google.com/maps/d/edit?mid=1nyoEbCk_SXPRRWx5NF0R1Hr0dcx_big&usp=sharing).

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/GemeenteHeusdenFijnstof.png)

Wanneer een meetstation boven de WHO waardes zit, dan wordt dit weergegeven als ![alt text](https://maps.google.com/mapfiles/kml/shapes/firedept.png) anders als ![alt text](https://maps.google.com/mapfiles/kml/shapes/parks.png) (of als er geen meetdata voor laatste jaar is). De gemiddeldes van alle meetstations uit de lijst wordt ergens in het midden van de coördinaten weergegeven, boven de WHO waardes als ![alt text](https://maps.google.com/mapfiles/kml/shapes/schools.png) anders als ![alt text](https://maps.google.com/mapfiles/kml/shapes/ranger_station.png)


## Voorbeeld van gegenereerd PM2.5 .csv bestand: _GemeenteHeusden.txt.pm25.csv
```
Station,2021,2022,2023,2024
GLB_1732427,,41.4,8.0,8.6
LTD_41242,2.4
LTD_41345,6.0,13.8,85.5
LTD_42281,15.9
LTD_51080,11.6,9.2,4.1
LTD_54087,9.0,9.2,6.8,7.6
LTD_54165,5.4,6.3,4.6,5.1
LTD_54311,16.7,16.5,11.9,14.0
LTD_54329,9.3,8.8,6.0,6.6
LTD_54447,8.6,9.0,7.1,7.3
LTD_54636,9.0,9.5,6.7,7.4
LTD_54653,8.3,9.9,7.2,7.4
LTD_55107,8.6,10.0,6.9,8.2
LTD_55358,,10.0,7.8,8.3
LTD_55458,4.1,5.0
LTD_56098,,4.3
LTD_56607,,11.6,8.2,9.9
LTD_56928,,12.2,7.2,7.2
LTD_57197,,9.2,6.6,6.1
LTD_58098,,11.0,8.6,10.3
LTD_58544,,10.5,8.8
LTD_58547,,9.7,7.8
LTD_63321,,10.1,8.2,9.1
LTD_63545,,11.0,8.3,10.3
LTD_64106,,8.0,6.0,7.0
LTD_64160,,6.1,5.0,5.8
LTD_64332,,8.8,6.7,7.2
LTD_64345,,7.6,5.6,6.0
LTD_64499,,9.8,7.0,8.0
LTD_64544,,8.2,5.9,8.3
LTD_64753,,10.1,6.3,7.1
LTD_64764,,7.3,5.1,6.2
LTD_65145,,10.8,6.1,6.8
LTD_65341,,20.8
LTD_65562,,10.3,5.0,5.6
LTD_65769,,8.5
LTD_65989,,11.8,7.6,8.5
LTD_66012,,7.2,5.6,5.7
LTD_66653,,,5.8,5.9
LTD_66698,,,6.8,7.0
LTD_67379,,,7.2,1.5
LTD_68565,,,4.1,4.7
LTD_69527,,,4.4,4.4
LTD_73155,,,5.0,5.7
LTD_73353,,,6.8,6.7
LTD_73365,,,4.9,5.8
LTD_75241,,,8.6,9.8
LTD_78470,,,,6.6
```

Hiermee kun je een mooie grafiek maken met per station de jaren gegroepeerd. Bijvoorbeeld:

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/_GemeenteHeusden.txt.pm25.png)


## Voorbeeld van gegenereerd PM10 .csv bestand: _GemeenteHeusden.txt.pm10.csv
```
Station,2021,2022,2023,2024
GLB_1732427,,39.9,8.8,17.3
LTD_41242,5.5
LTD_41345,10.7,21.4,93.7
LTD_42281,26.1
LTD_51080,15.6,14.9,7.8
LTD_54087,12.4,13.6,12.3,11.3
LTD_54165,6.5,9.0,8.0,7.4
LTD_54311,16.4,19.5,16.9,15.8
LTD_54329,12.1,15.5,14.1,12.4
LTD_54447,10.8,13.8,12.8,11.0
LTD_54636,11.6,14.1,12.3,10.8
LTD_54653,9.6,12.9,11.1,9.6
LTD_55107,8.4,12.1,9.7,9.4
LTD_55358,,14.7,13.2,12.0
LTD_55458,5.3,6.4
LTD_56098,,6.2
LTD_56607,,15.6,13.4,12.8
LTD_56928,,18.7,13.0,10.7
LTD_57197,,18.5,15.7,12.4
LTD_58098,,18.8,17.5,16.5
LTD_58544,,16.0,16.6
LTD_58547,,15.8,12.8
LTD_63321,,16.3,15.0,13.6
LTD_63545,,20.4,18.0,17.9
LTD_64106,,14.4,13.5,12.5
LTD_64160,,10.8,10.8,10.4
LTD_64332,,15.6,14.4,13.6
LTD_64345,,14.0,12.3,11.4
LTD_64499,,15.8,14.2,13.1
LTD_64544,,13.6,12.5,12.7
LTD_64753,,17.7,14.7,13.4
LTD_64764,,13.2,11.3,11.8
LTD_65145,,16.4,11.8,10.9
LTD_65341,,32.9
LTD_65562,,15.7,10.6,9.3
LTD_65769,,16.2
LTD_65989,,21.4,16.8,15.6
LTD_66012,,13.6,12.3,11.1
LTD_66653,,,10.8,9.3
LTD_66698,,,16.0,14.1
LTD_67379,,,12.3,4.8
LTD_68565,,,6.8,6.4
LTD_69527,,,7.7,7.5
LTD_73155,,,8.1,8.8
LTD_73353,,,11.2,11.4
LTD_73365,,,8.1,9.4
LTD_75241,,,12.4,14.6
LTD_78470,,,,9.1
```

Hiermee kun je een mooie grafiek maken met per station de jaren gegroepeerd. Bijvoorbeeld:

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/_GemeenteHeusden.txt.pm10.png)

---
# Hoe Python, pakketten te installeren
Uitleg voor iemand die geen kennis heeft van Python. Ik weet niet welke computer en operating systeem u heeft.

U moet Python 3.9 of hoger installeren. Ik heb Python 3.9.13 geïnstalleerd.
[Hier vindt u meer informatie over het installeren van Python](https://realpython.com/installing-python/)

Waarschijnlijk zijn sommige pakketten die nodig zijn voor samenmeten-rivm-tools niet geïnstalleerd (foutmeldingen). [Meer informatie over het installeren van Python-pakketten](https://packaging.python.org/en/latest/tutorials/installing-packages/)
Ik heb de volgende pakketten geïnstalleerd (gebruik bijvoorbeeld python -m pip install "package_name"), zie [requirements.txt](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/requirements.txt)

    python_dateutil==2.8.2
