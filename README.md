- [Inleiding](#inleiding)
- [Python script gemeente\_station\_namen.py](#python-script-gemeente_station_namenpy)
  - [Voorbeeld van uitvoer voor gemeente Heusden (797)](#voorbeeld-van-uitvoer-voor-gemeente-heusden-797)
- [Python script station\_data\_naar\_csv.py](#python-script-station_data_naar_csvpy)
  - [Voorbeeld van (gedeeltelijke uitvoer), gebruik makend van meetstation namen in \_GemeenteHeusden.txt](#voorbeeld-van-gedeeltelijke-uitvoer-gebruik-makend-van-meetstation-namen-in-_gemeenteheusdentxt)
  - [Voorbeeld van (gedeeltelijke) inhoud van zo een csv bestand, bijvoorbeeld LTD\_54329](#voorbeeld-van-gedeeltelijke-inhoud-van-zo-een-csv-bestand-bijvoorbeeld-ltd_54329)
- [Python script samenvatting.py](#python-script-samenvattingpy)
  - [Voorbeeld voor genereren samenvatting van \_Elshout.txt](#voorbeeld-voor-genereren-samenvatting-van-_elshouttxt)
  - [Voorbeelden van filteren opties](#voorbeelden-van-filteren-opties)
  - [Gegenereerd .kml bestand](#gegenereerd-kml-bestand)
  - [Voorbeeld van Google Maps op basis van .kml uitvoer](#voorbeeld-van-google-maps-op-basis-van-kml-uitvoer)
  - [Voorbeeld van gegenereerd PM2.5 .csv bestand: \_Elshout.txt.pm25.csv](#voorbeeld-van-gegenereerd-pm25-csv-bestand-_elshouttxtpm25csv)
  - [Voorbeeld van gegenereerd PM10 .csv bestand: \_Elshout.txt.pm10.csv](#voorbeeld-van-gegenereerd-pm10-csv-bestand-_elshouttxtpm10csv)
  - [Voorbeeld van gegenereerd gemiddeld PM2.5 .avg.csv bestand: \_Elshout.txt.pm25.avg.csv](#voorbeeld-van-gegenereerd-gemiddeld-pm25-avgcsv-bestand-_elshouttxtpm25avgcsv)
  - [Voorbeeld van gegenereerd gemiddeld PM10 .avg.csv bestand: \_Elshout.txt.pm10.avg.csv](#voorbeeld-van-gegenereerd-gemiddeld-pm10-avgcsv-bestand-_elshouttxtpm10avgcsv)
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
Uitvoer  : STATION_LIST.txt.kml          (bestand in Google My Maps formaat)
           STATION_LIST.txt.pm25.csv     (PM2.5 per jaar per station in csv formaat)
           STATION_LIST.txt.pm10.csv     (PM10  per jaar per station in csv formaat)
           STATION_LIST.txt.pm25.avg.csv (gemiddelde PM2.5 per jaar per station)
           STATION_LIST.txt.pm10.avg.csv (gemiddelde PM10  per jaar per station)
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

## Voorbeeld voor genereren samenvatting van _Elshout.txt
```
python ..\samenvatting.py _Elshout.txt
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar
  LTD_58544,  JAAR   269d/  269d, 2022-12-31,    2022,  16.0,    2,  310,    6,    2,  10.8,    1,  140,    53, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58544,  JAAR   247d/  247d, 2023-09-22,    2023,  16.6,    1,  128,    5,    4,   9.1,    1,   76,    33, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58544, ALLES   516d/  516d,           ,   alles,  16.4,    0,  310,    6,    4,  10.1,    0,  140,    53, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_65562,  JAAR    32d/   32d, 2022-12-31,    2022,  15.7,    2,   57,    0,    0,  10.9,    0,   37,    10, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65562,  JAAR   341d/  341d, 2023-12-31,    2023,  10.6,    0,   76,    0,    0,   5.1,    0,   53,     8, PM2.5 > WHO jaar 5
  LTD_65562,  JAAR   182d/  182d, 2024-07-15,    2024,   9.3,    0,   90,    0,    0,   5.6,    0,   61,     7, PM2.5 > WHO jaar 5
  LTD_65562, ALLES   556d/  556d,           ,   alles,  10.5,    0,   90,    0,    0,   5.7,    0,   61,    10, PM2.5 > WHO jaar 5
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

  LTD_65341,  JAAR     5d/    5d, 2022-11-26,    2022,  32.9,    6,   85,    2,    0,  22.2,    6,   54,     6, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65341, ALLES     5d/    5d,           ,   alles,  40.1,    0,   85,    2,    0,  29.4,    0,   54,     6, PM10  > WHO jaar 15 > EU jaar 40; PM2.5 > WHO jaar 5 > EU jaar 25
    Station,             Periode,      Datum,    Info,  PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar

 Gemiddelde,  JAAR   307d/  307d,           ,    2022,  16.3,    2,  310,    6,    2,  11.0,    0,  140,    53, PM10  > WHO jaar 15; PM2.5 > WHO jaar 5
 Gemiddelde,  JAAR   588d/  588d,           ,    2023,  13.1,    0,  128,    5,    4,   6.8,    0,   76,    33, PM10  > WHO dag #5; PM2.5 > WHO jaar 5
 Gemiddelde,  JAAR   182d/  182d,           ,    2024,   9.3,    0,   90,    0,    0,   5.6,    0,   61,     7, PM2.5 > WHO jaar 5
 Gemiddelde, ALLES  1078d/ 1078d,           ,   alles,  13.4,    0,  310,    6,    4,   7.8,    0,  140,    53, PM10  > WHO dag #6; PM2.5 > WHO jaar 5
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


## Voorbeeld van gegenereerd PM2.5 .csv bestand: _Elshout.txt.pm25.csv
```
Station,2022,2023,2024,Gemiddeld
LTD_58544,10.8,9.1,10.0
LTD_65341,22.2,22.2
LTD_65562,10.9,5.1,5.6,5.6
```

Hiermee kun je een mooie grafiek maken met per station de jaren gegroepeerd. Bijvoorbeeld:

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/_GemeenteHeusden.txt.pm25.png)


## Voorbeeld van gegenereerd PM10 .csv bestand: _Elshout.txt.pm10.csv
```
Station,2022,2023,2024,Gemiddeld
LTD_58544,16.0,16.6,16.3
LTD_65341,32.9,32.9
LTD_65562,15.7,10.6,9.3,10.5
```

Hiermee kun je een mooie grafiek maken met per station de jaren gegroepeerd. Bijvoorbeeld:

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/_GemeenteHeusden.txt.pm10.png)

## Voorbeeld van gegenereerd gemiddeld PM2.5 .avg.csv bestand: _Elshout.txt.pm25.avg.csv
```
Station,2022,2023,2024,Gemiddeld
Elshout,11.0,6.8,5.6,7.8
```

Hiermee kun je een mooie grafiek maken door per dorp/stad de jaren gegroepeerd (meerdere avg.csv bestanden samenvoegen). Bijvoorbeeld:
```
Station,2022,2023,2024,Gemiddeld
Drunen,11.2,7.2,7.6,8.4
Elshout,11.0,6.8,5.6,7.8
Hedikhuizen,8.6,6.0,8.3,6.8
Herpt,16.8,12.3,14.0,14.4
Heusden,12.4,7.5,7.2,8.7
Nieuwkuijk,9.6,6.2,6.6,7.1
OudHeusden,7.4,5.7,5.7,5.8
Vlijmen,8.7,6.4,6.9,7.0
GemeenteHeusden,10.7,6.9,7.3,8.0
```

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/_GemeenteHeusden.txt.pm25.avg.png)


## Voorbeeld van gegenereerd gemiddeld PM10 .avg.csv bestand: _Elshout.txt.pm10.avg.csv
```
Station,2022,2023,2024,Gemiddeld
Elshout,16.3,13.1,9.3,13.4
```

Hiermee kun je een mooie grafiek maken door per dorp/stad de jaren gegroepeerd (meerdere avg.csv bestanden samenvoegen). Bijvoorbeeld:
```
Station,2022,2023,2024,Gemiddeld
Drunen,16.3,13.4,12.0,13.9
Elshout,16.3,13.1,9.3,13.4
Hedikhuizen,13.6,12.5,12.7,12.7
Herpt,19.5,16.9,15.8,17.7
Heusden,18.7,13.0,10.7,13.9
Nieuwkuijk,15.5,12.3,11.4,12.8
OudHeusden,14.3,12.3,11.1,11.9
Vlijmen,13.1,12.2,11.3,12.0
GemeenteHeusden,15.7,12.9,11.7,13.3
```

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/_GemeenteHeusden.txt.pm10.avg.png)

---
# Hoe Python, pakketten te installeren
Uitleg voor iemand die geen kennis heeft van Python. Ik weet niet welke computer en operating systeem u heeft.

U moet Python 3.9 of hoger installeren. Ik heb Python 3.9.13 geïnstalleerd.
[Hier vindt u meer informatie over het installeren van Python](https://realpython.com/installing-python/)

Waarschijnlijk zijn sommige pakketten die nodig zijn voor samenmeten-rivm-tools niet geïnstalleerd (foutmeldingen). [Meer informatie over het installeren van Python-pakketten](https://packaging.python.org/en/latest/tutorials/installing-packages/)
Ik heb de volgende pakketten geïnstalleerd (gebruik bijvoorbeeld python -m pip install "package_name"), zie [requirements.txt](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/requirements.txt)

    python_dateutil==2.8.2
