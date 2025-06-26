storm_risk:
  cape:
    low: 500         # J/kg – Unterhalb dieses Werts kein Gewitterrisiko
    medium: 1000     # J/kg – Ab hier mittleres Risiko
  shear:
    medium: 12       # m/s – Vertikaler Windscherungswert für mittleres Risiko
  wind_gust:
    medium: 40       # km/h – Böen ab diesem Wert erhöhen das Risiko
    high: 60         # km/h – Böen ab diesem Wert führen zu hoher Warnstufe
  rainrate:
    low: 0.2         # mm/h – Ab hier nennenswerter Niederschlag
    medium: 1.0      # mm/h – Ab hier signifikante Regenbelastung
  vigilance_override_level: 2  # Bei offiziellen Warnungen ab Level 2 immer Risiko=hoch