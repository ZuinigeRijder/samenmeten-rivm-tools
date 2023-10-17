- [Inleiding](#inleiding)
- [Hoe Python, pakketten te installeren](#hoe-python-pakketten-te-installeren)
- [gemeente\_station\_namen.py](#gemeente_station_namenpy)
- [station\_data\_naar\_csv.py](#station_data_naar_csvpy)
- [samenvatting.py](#samenvattingpy)



---
# Inleiding
In [gemeente Heusden](https://samenmeten.rivm.nl/dataportaal/gemeente_tijdreeks.php?gem_id=797) is er ook een samenmeten project en ik wilde weten in hoeverre de fijnstof uitstoot van PM10 en PM2.5 voldoet aan de WHO (World Health Organization) of EU richtlijnen en/of hoever we daarvan af zitten. Ik kon bij de RIVM wel historische data vinden, maar geen actuele informatie. Daarnaast wilde ik gebruik maken van gekalibreerde uurwaardes om zo te berekenen of een meetstation of een groep van meetstations op (lopende) jaarbasis wel of niet aan de richtlijnen voldoen. Daarom heb ik deze python scripts gemaakt en deze beschikbaar gesteld, zodat die door andere ook gebruikt kunnen worden. En eventuele verbeteringen aangebracht kunnen worden.

Er zijn 3 python scripts:
- gemeente_station_namen.py: hiermee kun je meetstation namen van een gemeente achterhalen
- station_data_naar_csv.py: hiermee kun je de uurwaardes van een meeststation of een groep van meetstations ophalen en toevoegen aan reeds beschikbare .csv bestanden
- samenvatting.py: genereert een samenvatting van de jaar waardes (en optioneel maand, week, dag) van een meetstation of groep van meetstations en schrijft deze ook naar een kml bestand, zodat je die in [Google My Maps](https://mymaps.google.com) kunt importeren.

Voorbeeld van de [resultaten van fijnstof over 2022 van gemeente Heusden kun je hier vinden op Google My Maps](https://www.google.com/maps/d/edit?mid=1nyoEbCk_SXPRRWx5NF0R1Hr0dcx_big&usp=sharing).

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/HeusdenFijnstof2022.png)

Python als programmeertaal heeft het voordeel dat het draait op Windows, Linux en Mac. De python scripts maken gebruik van [https://api-samenmeten.rivm.nl/v1.0](https://samenmeten.nl/dataportaal/api-application-programming-interface) voor het ophalen van de gegevens.

---
# Hoe Python, pakketten te installeren
Uitleg voor iemand die geen kennis heeft van Python. Ik weet niet welke computer je hebt.

U moet Python 3.9 of hoger installeren. Ik heb Python 3.9.13 geïnstalleerd.
[Hier vindt u meer informatie over het installeren van Python](https://realpython.com/installing-python/)

Waarschijnlijk zijn sommige pakketten die nodig zijn voor samenmeten-rivm-tools niet geïnstalleerd (foutmeldingen). [Meer informatie over het installeren van Python-pakketten](https://packaging.python.org/en/latest/tutorials/installing-packages/)
Ik heb de volgende pakketten geïnstalleerd (gebruik bijvoorbeeld python -m pip install "package_name"), zie [requirements.txt](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/requirements.txt)

    python_dateutil==2.8.2



---
# gemeente_station_namen.py
De andere python scripts gebruiken als invoer een bestand met lijst van meetstation namen. In plaats van deze allemaal op te zoeken en over te typen, kun je dit script gebruiken als hulpmiddel.

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

Zoek in [GemeentenAlfabetisch2022.csv](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/GemeentenAlfabetisch2022.csv) de gemeentecode op en voer dan het volgende commando uit voor een overzicht van stationnamen bij een gemeente, bijvoorbeeld 797:
```
python gemeente_station_namen.py 797
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

Deze namen kun je in een bestand zetten, bijvoorbeeld _Heusden.txt, die je in de volgende scripts als invoer gebruikt. Natuurlijk kun je hier meetstations uit verwijderen en/of toevoegen van bijvoorbeeld andere gemeentes.


---
# station_data_naar_csv.py
Dit script update per meetstation uit het invoer bestand met meetstation namen een .csv bestand. De eerste keer zal deze alle data ophalen, de volgende keren zal deze nieuwe data toevoegen aan de .csv bestanden per meetstation.

Voer het volgende commando uit voor hulp:
```
python station_data_naar_csv.py

Gebruik  : python station_data_naar_csv.py bestand_met_station_namen.txt [debug]
Voorbeeld: python station_data_naar_csv.py _heusden.txt
INVOER   : bestand_met_station_namen.txt
UITVOER  : voor iedere station in bestand_met_station_namen.txt schrijf .csv bestand

Opmerking: station namen van een gemeente kun je opvragen met:
           python gemeente_station_namen.py gemeente_code
```

Voorbeeld van (gedeeltelijke uitvoer), gebruik makend van meetstation namen in _Heusden.txt:
```
python station_data_naar_csv.py _Heusden.txt
Ophalen station data voor GLB_1732427
Laatste datum locale tijd: 2023-09-12 21:00 -> iso8601 utc: 2023-09-12T19:00:00.000Z
Uitvoer csv bestand: GLB_1732427.csv

Ophalen data voor type: pm10_kal
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(36530)/Observations

Ophalen data voor type: pm10
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(36529)/Observations

Ophalen data voor type: pm25_kal
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(36528)/Observations

Ophalen data voor type: pm25
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(36527)/Observations

Toevoegen 108 resultaten aan csv bestand
Ophalen station data voor LTD_56607
Laatste datum locale tijd: 2023-09-12 21:00 -> iso8601 utc: 2023-09-12T19:00:00.000Z
Uitvoer csv bestand: LTD_56607.csv

Ophalen data voor type: rh
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(32216)/Observations

Ophalen data voor type: temp
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(32215)/Observations

Ophalen data voor type: pm10_kal
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(32214)/Observations

Ophalen data voor type: pm10
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(32213)/Observations

Ophalen data voor type: pm25_kal
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(32212)/Observations

Ophalen data voor type: pm25
@iot.nextLink=https://api-samenmeten.rivm.nl/v1.0/Datastreams(32211)/Observations

Toevoegen 108 resultaten aan csv bestand
Ophalen station data voor LTD_54329
Laatste datum locale tijd: 2023-09-12 21:00 -> iso8601 utc: 2023-09-12T19:00:00.000Z
Uitvoer csv bestand: LTD_54329.csv
.....
```

Voorbeeld van (gedeeltelijke) inhoud van zo een csv bestand, bijvoorbeeld LTD_54329:
```
datetime,pm10_kal,pm10,pm25_kal,pm25,rh%,temp
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
# samenvatting.py
Dit script genereert een samenvatting per meetstation uit het invoer bestand met meetstation namen en gebruikt hiervoor de .csv bestanden die geupdate zijn uit het vorige script. Daarnaast wordt er ook een .kml bestand gemaakt, die je in [Google My Maps](https://mymaps.google.com) kunt importeren.

Voer het volgende commando uit voor hulp:
```
python samenvatting.py
Onbekend invoer bestand:

Gebruik  : python samenvatting.py [dag] [week] [maand] [jjjj] STATION_LIJST.txt
Voorbeeld: python samenvatting.py _heusden.txt

Opm.1: Wilt u alleen tot en met een bepaald jaar een samenvatting hebben,
       kunt u parameter jjjj gebruiken, bijvoorbeeld 2022
Opm.2: Wilt u alle details zien per dag/week/maand, kunt u deze als parameter meegeven
Opm.3: station namen van een gemeente kan opgevraagd worden met tool:
            python gemeente_station_namen.py gemeente_code
Opm.4: Voordat dit script gedraaid wordt, moeten de .csv bestanden voor
       deze STATION_LIJST.txt gegenereerd zijn met:
            python station_data_naar_csv.py STATION_LIST.txt
```

Voorbeeld voor generenen samenvatting van _Heusden.txt:
```
python samenvatting.py _Heusden.txt
    Station,   Periode,      Datum,  Info, PM10, (Min,  Max, #WHO, #EU), PM2.5, (Min,  Max, #WHO), Commentaar
GLB_1732427, JAAR 112d, 2022-12-31,  2022,   39,    0, 1000,   12,   11,    38,    0, 1000,    43, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5 > EU jaar 25
GLB_1732427, JAAR 259d, 2023-09-17,  2023,    9,    0,  107,    1,    1,     9,    0,   96,    47, PM2.5 > WHO jaar 5

  LTD_56607, JAAR 351d, 2022-12-31,  2022,   16,    1,  148,    9,    5,    11,    1,   60,    72, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_56607, JAAR 259d, 2023-09-17,  2023,   14,    1,  104,    3,    1,     8,    1,   60,    30, PM2.5 > WHO jaar 5

  LTD_54329, JAAR  40d, 2021-12-31,  2021,   12,    1,   66,    0,    0,    10,    1,   69,     9, PM2.5 > WHO jaar 5
  LTD_54329, JAAR 365d, 2022-12-31,  2022,   15,    2,  144,    1,    0,     8,    0,  119,    38, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54329, JAAR 259d, 2023-09-17,  2023,   15,    1,   88,    0,    0,     6,    0,   54,    14, PM2.5 > WHO jaar 5

  LTD_57197, JAAR 338d, 2022-12-31,  2022,   19,    3,  155,    6,    3,     8,    1,   54,    39, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_57197, JAAR 259d, 2023-09-17,  2023,   17,    2,  193,    2,    0,     7,    1,   58,    17, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_64753, JAAR  58d, 2022-12-31,  2022,   18,    4,  143,    1,    0,    10,    1,   77,    17, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_64753, JAAR 259d, 2023-09-17,  2023,   16,    2,  359,    1,    0,     7,    0,   76,    17, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_58098, JAAR 314d, 2022-12-31,  2022,   19,    1,  101,    9,    6,    10,    1,   69,    55, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58098, JAAR 259d, 2023-09-17,  2023,   18,    2,  171,    7,    6,     9,    1,   94,    29, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_65989, JAAR  20d, 2022-12-31,  2022,   21,    4,   81,    1,    0,    12,    1,   58,     6, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65989, JAAR 259d, 2023-09-17,  2023,   18,    2,  103,    3,    0,     8,    1,   81,    21, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_54087, JAAR  44d, 2021-12-31,  2021,   13,    1,   56,    0,    0,    10,    0,   60,     7, PM2.5 > WHO jaar 5
  LTD_54087, JAAR 365d, 2022-12-31,  2022,   14,    1,  124,    0,    0,     8,    0,   67,    43, PM2.5 > WHO jaar 5
  LTD_54087, JAAR 259d, 2023-09-17,  2023,   13,    1,  121,    0,    0,     7,    0,   61,    18, PM2.5 > WHO jaar 5

  LTD_64499, JAAR  72d, 2022-12-31,  2022,   16,    3,   65,    0,    0,    10,    1,   45,    15, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_64499, JAAR 259d, 2023-09-17,  2023,   15,    1,   88,    0,    0,     7,    0,   57,    22, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_54636, JAAR  30d, 2021-12-31,  2021,   12,    1,   44,    0,    0,    10,    1,   50,     6, PM2.5 > WHO jaar 5
  LTD_54636, JAAR 365d, 2022-12-31,  2022,   14,    1,  249,    0,    0,     9,    0,   97,    51, PM2.5 > WHO jaar 5
  LTD_54636, JAAR 259d, 2023-09-17,  2023,   13,    0,  156,    1,    0,     7,    0,   78,    21, PM2.5 > WHO jaar 5

  LTD_64106, JAAR  86d, 2022-12-31,  2022,   15,    2,   62,    0,    0,     8,    1,   42,    11, PM2.5 > WHO jaar 5
  LTD_64106, JAAR 259d, 2023-09-17,  2023,   14,    1,   89,    0,    0,     6,    0,   52,    14, PM2.5 > WHO jaar 5

  LTD_58544, JAAR 296d, 2022-12-31,  2022,   16,    2,  310,    6,    2,    10,    1,  125,    44, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_58544, JAAR 259d, 2023-09-17,  2023,   17,    1,  128,    5,    5,     9,    1,   76,    33, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_65562, JAAR  34d, 2022-12-31,  2022,   16,    2,   57,    0,    0,    11,    1,   37,    10, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65562, JAAR 259d, 2023-09-17,  2023,   11,    0,   76,    0,    0,     5,    0,   53,     8, PM2.5 > WHO jaar 5

  LTD_68565, JAAR 187d, 2023-09-17,  2023,    7,    1,   56,    0,    0,     4,    0,   40,     1,

  LTD_63545, JAAR 106d, 2022-12-31,  2022,   20,    3,  117,    2,    1,    11,    1,   77,    25, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_63545, JAAR 259d, 2023-09-17,  2023,   17,    1,  383,    6,    1,     8,    1,   70,    23, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_64160, JAAR  84d, 2022-12-31,  2022,   11,    2,   43,    0,    0,     6,    1,   34,     1, PM2.5 > WHO jaar 5
  LTD_64160, JAAR 259d, 2023-09-17,  2023,   12,    2,   85,    0,    0,     5,    1,   42,     4, PM2.5 > WHO jaar 5

  LTD_64764, JAAR  62d, 2022-12-31,  2022,   13,    2,   63,    0,    0,     7,    1,   36,     6, PM2.5 > WHO jaar 5
  LTD_64764, JAAR 259d, 2023-09-17,  2023,   17,    2,   66,    0,    0,     6,    0,   43,     4, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_66653, JAAR 255d, 2023-09-17,  2023,   12,    1,  107,    0,    0,     6,    0,   59,    14, PM2.5 > WHO jaar 5

  LTD_65145, JAAR  48d, 2022-12-31,  2022,   16,    2,   68,    0,    0,    11,    1,   49,    17, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_65145, JAAR 259d, 2023-09-17,  2023,   12,    1,   79,    0,    0,     6,    0,   55,    14, PM2.5 > WHO jaar 5

  LTD_54447, JAAR  37d, 2021-12-31,  2021,   11,    1,   50,    0,    0,     9,    1,   36,     6, PM2.5 > WHO jaar 5
  LTD_54447, JAAR 365d, 2022-12-31,  2022,   14,    1,  701,    0,    0,     8,    0,  268,    40, PM2.5 > WHO jaar 5
  LTD_54447, JAAR 259d, 2023-09-17,  2023,   13,    1,  183,    0,    0,     7,    0,   60,    18, PM2.5 > WHO jaar 5

  LTD_54165, JAAR  43d, 2021-12-31,  2021,    5,    0,   25,    0,    0,     5,    1,   24,     2,
  LTD_54165, JAAR 365d, 2022-12-19,  2022,    9,    1,   42,    0,    0,     6,    0,   49,    14, PM2.5 > WHO jaar 5
  LTD_54165, JAAR 259d, 2023-09-17,  2023,    8,    0,   52,    0,    0,     5,    0,   43,     5, PM2.5 > WHO dag #4

  LTD_55358, JAAR 345d, 2022-12-31,  2022,   15,    2,  277,    3,    0,     9,    0,   66,    56, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_55358, JAAR 259d, 2023-09-17,  2023,   15,    1,  160,    1,    1,     8,    0,  161,    24, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_64345, JAAR  77d, 2022-12-31,  2022,   14,    3,   59,    0,    0,     7,    1,   35,     9, PM2.5 > WHO jaar 5
  LTD_64345, JAAR 259d, 2023-09-17,  2023,   13,    1,   67,    0,    0,     6,    0,   39,     9, PM2.5 > WHO jaar 5

  LTD_66698, JAAR 251d, 2023-09-17,  2023,   16,    2,  162,    1,    0,     7,    1,   61,    18, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_63321, JAAR 116d, 2022-12-31,  2022,   16,    2,  722,    1,    1,    10,    1,  163,    25, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_63321, JAAR 259d, 2023-09-17,  2023,   15,    1,  392,    2,    1,     8,    0,   98,    31, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_56928, JAAR 353d, 2022-12-10,  2022,   18,    3,  139,    1,    0,    10,    1,   75,    36, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_56928, JAAR 251d, 2023-09-17,  2023,   13,    1,  185,    0,    0,     8,    1,   58,    22, PM2.5 > WHO jaar 5

  LTD_54311, JAAR  40d, 2021-12-31,  2021,   16,    2,   93,    0,    0,    17,    2,   91,    20, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54311, JAAR 365d, 2022-12-31,  2022,   20,    2,  949,   10,    9,    15,    1,  732,   125, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
  LTD_54311, JAAR 259d, 2023-09-17,  2023,   18,    1,  124,    6,    4,    12,    1,   90,    53, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5

  LTD_64544, JAAR  70d, 2022-12-31,  2022,   13,    2,   48,    0,    0,     8,    0,   36,     9, PM2.5 > WHO jaar 5
  LTD_64544, JAAR 259d, 2023-09-17,  2023,   13,    2,  111,    0,    0,     6,    0,   61,    12, PM2.5 > WHO jaar 5

 Gemiddelde,      JAAR, 2021-12-01,  2021,   12,    0,   93,    0,    0,    10,    0,   91,    20, PM2.5 > WHO jaar 5
 Gemiddelde,      JAAR, 2022-12-11,  2022,   17,    0, 1000,   12,   11,    10,    0, 1000,   125, PM10 > WHO jaar 15; PM2.5 > WHO jaar 5
 Gemiddelde,      JAAR, 2023-03-13,  2023,   14,    0,  392,    7,    6,     7,    0,  161,    53, PM10 > WHO dag #4; PM2.5 > WHO jaar 5
```

Het uitvoer kml bestand (de naam van je invoer bestand met extensie .kml, bijvoorbeeld _Heusden.txt.kml) kun je importeren in Google My Maps.

Je kunt ook alleen een samenvatting genereren tot een volledig jaar, bijvoorbeeld:
```
python samenvatting.py 2022 _Heusden.txt
```

Voorbeeld van de [resultaten van fijnstof over 2022 van gemeente Heusden kun je hier vinden op Google My Maps](https://www.google.com/maps/d/edit?mid=1nyoEbCk_SXPRRWx5NF0R1Hr0dcx_big&usp=sharing).

![alt text](https://raw.githubusercontent.com/ZuinigeRijder/samenmeten-rivm-tools/main/examples/HeusdenFijnstof2022.png)

Wanneer een meetstation boven de WHO waardes zit, dan wordt dit weergegeven als ![alt text](https://maps.google.com/mapfiles/kml/shapes/firedept.png) anders als ![alt text](https://maps.google.com/mapfiles/kml/shapes/parks.png) (of als er geen meetdata voor laatste jaar is).
De gemiddeldes van alle meetstations uit de lijst wordt ergens in het midden van de coördinaten weergegeven, boven de WHO waardes als ![alt text](https://maps.google.com/mapfiles/kml/shapes/schools.png) anders als ![alt text](https://maps.google.com/mapfiles/kml/shapes/ranger_station.png)