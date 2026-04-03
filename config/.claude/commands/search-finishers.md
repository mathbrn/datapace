# Recherche de finishers pour un événement

Recherche le nombre exact de finishers pour l'événement "$ARGUMENTS" en utilisant toutes les APIs disponibles dans l'ordre de priorité :

1. **Sporthive API** : `site:results.sporthive.com "{event}"` → extraire l'event ID → `curl eventresults-api.speedhive.com/sporthive/events/{id}/races` → `classificationsCount`
2. **Tracx API** : chercher dans les 860 events Tracx → `api.tracx.events/v1/events/{id}/races` → `participant_count`
3. **MarathonView** : `marathonview.net/series/{id}` via WebFetch → finisher counts par année
4. **Athlinks** : `site:athlinks.com/event "{event}"` → `reignite-api.athlinks.com/master/{id}/metadata` → `alaska.athlinks.com/Events/Race/Api/{eventId}/Course/0` → `EventCoursesDropDown[].Value` 3ème champ
5. **RTRT.me** : pour les Great Run events → `api.rtrt.me/events/{code}` → `finishers`
6. **TimeTo** : pour les événements ASO → `sportinnovation.fr/api/events/{id}/races` → `totals.maxGeneralRanking`
7. **Active.com** : `resultscui.active.com/api/results/events/{appName}` → `meta.totalCount`
8. **Web search** ciblé avec fourchettes de chiffres

Règles strictes :
- JAMAIS de chiffres ronds (estimations)
- JAMAIS écraser une cellule déjà remplie
- Exclure les résultats VIRTUAL
- Uniquement 5K à Marathon (pas d'ultras/trail)

Après avoir trouvé les données, appliquer avec :
```
python update_finishers.py "Race Name" DISTANCE YEAR COUNT
```
Puis `python generate_dashboard.py && git add -A && git commit && git push`
