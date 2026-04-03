# Crawler massif d'une source de données

Lance un crawl massif de la source "$ARGUMENTS" pour collecter le maximum de données de courses.

## Sources disponibles

### sporthive
Crawler `crawl_sporthive.py` : découverte d'event IDs via Google + API Sporthive.
```
python crawl_sporthive.py
```

### tracx
Crawler `crawl_tracx.py` : scan exhaustif des 860 events Tracx.
```
python crawl_tracx.py
```

### athlinks
Crawler `crawl_athlinks.py` : scan d'IDs master Athlinks.
```
python crawl_athlinks.py
```

### all
Exécuter les 3 crawlers puis l'agrégateur :
```
python crawl_sporthive.py
python crawl_tracx.py
python crawl_athlinks.py
python aggregate_all.py
```

## Après le crawl

1. Analyser `unified_race_database.json` pour trouver des événements 5000+ pas dans le dashboard
2. Ajouter les nouveaux événements via `/add-event`
3. Extraire les temps moyens des résultats Sporthive → `avg_times_sporthive.json`
4. Commit et push
