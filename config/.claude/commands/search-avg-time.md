# Recherche du temps moyen par édition

Recherche le temps moyen de finisher pour l'événement "$ARGUMENTS" sur toutes les années disponibles.

## Sources par priorité

1. **Sporthive API** (MEILLEURE SOURCE) : `eventresults-api.speedhive.com/sporthive/events/{id}/races` → `raceStatistics.averageSpeedInKmh` → `temps = distance_km / vitesse`. C'est la VRAIE moyenne, pas une estimation.
2. **Tracx API** : paginer les résultats individuels (`results?page=X`), échantillonner ~30 pages uniformément réparties, calculer la moyenne des `finish_time - start`. Attention : `average_speed` dans Tracx est souvent une valeur par défaut (3.055 m/s), NE PAS l'utiliser.
3. **Active.com** : prendre le résultat à la position médiane (`offset=total/2&limit=1`) comme proxy. Attention : utilise le gun time qui inclut l'attente au départ.

## Stockage

Ajouter dans `avg_times_sporthive.json` au format :
```json
{"label": "source_year", "race": "Event Name", "dist_m": 21097, "year": 2024, "count": 15000, "avg_time": "2:03:45", "avg_speed_kmh": 10.5}
```

Puis `python generate_dashboard.py && git add -A && git commit && git push`
