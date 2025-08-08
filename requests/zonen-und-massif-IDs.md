TECHNISCHE ANFORDERUNG  
Zonen- und Massif-IDs entlang des GR20 zur Risikoanalyse

ZIEL:
• Identifiziere entlang des GR20:
  – alle bekannten Massifs mit Betretungsverbot (für Sperr-Infos)
  – alle bekannten Zonen mit Warnstufe ≥2 (für Waldbrandwarnung)
• Ausgabe ausschließlich als numerische ID-Listen (zur Nutzung in 160-Zeichen-SMS)
• Mapping Name ⇄ ID ist nur intern erforderlich (nicht für Ausgabe)

MASSIFS (fest definiert):
• Folgende Massif-IDs entlang des GR20 sind bekannt und exklusiv relevant:
  IDs: 1, 29, 3, 4, 5, 6, 9, 10, 16, 24, 25, 26, 27, 28
• Diese stammen aus der HTML-Tabelle der Webseite (manuell extrahiert)
• „(*)“ markierte Einträge in der Tabelle gelten als potenziell gesperrt

ZONEN (nur Namen bekannt):
• Folgende Zone-Namen sind relevant für den GR20:
  BALAGNE, MONTI, MONTAGNE, COTE DES NACRES, MOYENNE MONTAGNE SUD, REGION DE CONCA
• Ihre numerischen IDs sind auf der Website **nicht dokumentiert** und müssen
  durch Analyse der Leaflet-Vektordaten (DOM/JS) sicher ermittelt werden

VERARBEITUNG:
1. MASSIFS
  - Markiere von den o. g. 14 Massif-IDs jene, die in der Tabelle mit „(*)“ versehen sind
  - Ausgabe: Liste dieser Massif-IDs

2. ZONEN
  - Durchsuche die Leaflet-Pfadstruktur nach farblich markierten Polygonen:
    Gelb/orange = Warnstufe ≥2
  - Extrahiere deren interne ID-Nummer
  - Ermittle Zuordnung: Zone-ID ⇄ Zonenname (z. B. per Tooltip, JS-Attribut, etc.)
  - Filtere auf die 6 o. g. Zonen-Namen
  - Ausgabe: Liste der Zone-IDs mit Warnstufe ≥2

AUSGABEFORMAT:
• Plaintext, Markdown-Monospace-Block
• Zwei Listen:
    Massif_IDs: kommagetrennt der IDs, die mit einem Betretungsverbot belegt sind.
    Zone_IDs: kommagetrennt, die Warnstufe Level 2 (Orange) -> HIGH oder Level 3 (Rot) -> MAX sind. 
• Mapping_Massifs: ID → Name (nur GR20-Massifs)
• Mapping_Zonen: ID → Name (nur GR20-Zonen, sofern ermittelbar)

Diese Information werden an die Warntexte (E-Mail) angehängt und verändern nicht das bestehende Ausgabeformat bzw. bestehenden Code.

WICHTIG:
• Keine Verarbeitung nicht-GR20-relevanter Massifs oder Zonen
• Keine Spekulationen bei Zuordnung Name ⇄ ID
• Ergebnisse müssen belegbar sein (aus DOM, JS, Tooltip, o. ä.)

BEISPIEL:
Massif_IDs: 3,4,5,9,10,16,24,26
Zone_IDs: 204,205,207,208 (Beispiel, tatsächliche IDs sind unbekannt)
Mapping_Massifs:
  3 → BONIFATO
  4 → TARTAGINE-MELAJA
  …
Mapping_Zonen (Beispiel, Zuordnung nicht belegt):
  204 → MONTAGNE
  205 → MONTI
  …


Hier noch einmal die komplette Liste der Massifs (diese ist zu 100% sicher belegt durch die Webseite selbst )

(*)	Fermeture possible	

1	AGRIATES OUEST (*)	
29	AGRIATES EST (*)	
2	STELLA	
3	BONIFATO (*)	
4	TARTAGINE-MELAJA (*)	
5	FANGO (*)	
6	ASCO	
7	PIANA (*)	
8	LONCA-AITONE-SERRIERA	
9	VALDU-NIELLU ALBERTACCE	
10	RESTONICA-TAVIGNANO	
11	LIBBIU TRETTORE	
12	VERO-TAVERA -UCCIANI	
13	VERGHELLU (*)	
14	MANGANELLU (*)	
15	VALLEE DU VECCHIO - ROSPA SORBA	
16	VIZZAVONA	
17	GHISONI	
18	SAINT ANTOINE	
19	FIUMORBO	
20	PINIA (*)	
21	TOVA-SOLARO-CHISA	
22	COTI-CHIAVARI	
23	VALLE MALE	
24	BAVELLA (*)	
25	ZONZA	
26	CAVU LIVIU (*)	
27	OSPEDALE	
28	CAGNA	
 