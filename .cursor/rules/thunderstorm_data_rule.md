# 🌩️ Thunderstorm-Daten Regel

## **Morning Report:**
- **TH** (Thunderstorm): **D+0** Daten (heute) mit **T1** Koordinaten (heute)
- **TH+** (Thunderstorm Plus One): **D+1** Daten (morgen) mit **T2** Koordinaten (morgen)

## **Evening Report:**
- **TH** (Thunderstorm): **D+1** Daten (morgen) mit **T2** Koordinaten (morgen)
- **TH+** (Thunderstorm Plus One): **D+2** Daten (übermorgen) mit **T3** Koordinaten (übermorgen)

## **API-Limitation:**
- MeteoFrance API liefert nur **D+1** Thunderstorm-Daten
- **TH+** im Evening Report ist daher immer leer (`TH+:-`)

## **Merksatz:**
> "TH+ verschiebt sich um einen Tag: Morning = D+1/T2, Evening = D+2/T3"

## **Mapping:**
- `'Risque d\'orages'`: 'low'
- `'Averses orageuses'`: 'med'  
- `'Orages'`: 'high'

**Diese Regel gilt ab sofort für alle Thunderstorm-Berechnungen!** 