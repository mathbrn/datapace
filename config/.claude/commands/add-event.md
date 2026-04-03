# Ajouter un nouvel événement au dashboard

Ajoute l'événement "$ARGUMENTS" au dashboard complet avec toutes les données.

## Étapes

### 1. Vérifier que l'événement n'existe pas déjà
```python
python -c "
import openpyxl
wb = openpyxl.load_workbook('Suivi_Finishers_Monde_10k_-_21k_-_42k_HISTORIQUE.xlsx', data_only=True)
ws = wb['ALL']
for row in ws.iter_rows(min_row=2, values_only=True):
    if row[3] and 'KEYWORD' in str(row[3]).lower():
        print(f'{row[3]} ({row[2]})')
"
```

### 2. Ajouter l'événement avec les données de finishers
```
python add_event.py "Période" "City" "DISTANCE" "Race Name" YEAR COUNT [YEAR COUNT ...]
```
- Période : Janvier, Février, Mars, Avril, Mai, Juin, Juillet, Août, Septembre, Octobre, Novembre, Décembre
- Distance : MARATHON, SEMI, 10KM, AUTRE
- Seuil minimum : 5000 finishers

### 3. Marquer la première édition
Rechercher l'année de la première édition. Marquer `x` pour toutes les années antérieures dans le Excel. Marquer `-` pour 2020 si annulé COVID.

### 4. Ajouter les temps vainqueurs
Ajouter dans `create_chronos.py` les tuples :
```python
("Race Name", "42K", YEAR, "H:MM:SS", "H:MM:SS"),
```

### 5. Ajouter les temps moyens
Si disponible via Sporthive/Tracx, ajouter dans `avg_times_sporthive.json`.

### 6. Déployer
```
python create_chronos.py && python generate_dashboard.py && git add -A && git commit && git push
```
