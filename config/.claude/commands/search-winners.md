# Recherche des temps vainqueurs H/F

Recherche les temps vainqueurs homme et femme pour l'événement "$ARGUMENTS" sur toutes les années disponibles.

## Sources par priorité

1. **Tracx API** : `api.tracx.events/v1/events/{id}/races/{raceId}/rankings/{rankingId}/results?page=1` → premier résultat male + premier résultat female. Calculer le temps depuis `finish_time - start`. Préférer les rankings par gender, sinon filtrer dans Overall.
2. **Wikipedia/Grokipedia** : Tables historiques de vainqueurs avec temps exacts
3. **World Athletics** : `worldathletics.org/competition/calendar-results/results/{id}` → temps élites
4. **Web search** : `"{Event Name}" winners time results {year} men women`
5. **Active.com** : `resultscui.active.com/api/results/events/{appName}/participants?groupId={overallId}&offset=0&limit=1` → premier résultat = vainqueur

## Format de sortie

Ajouter dans `create_chronos.py` au format :
```python
("Event Name", "42K", YEAR, "H:MM:SS", "H:MM:SS"),
```
- 4ème champ = temps homme, 5ème = temps femme
- "N/A" si non trouvé
- Préférer Gun Time ou Real Time

Puis exécuter :
```
python create_chronos.py && python generate_dashboard.py && git add -A && git commit && git push
```
