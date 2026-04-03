# Remplir les cellules vides du dashboard

Identifie et remplit les cellules vides pour l'événement "$ARGUMENTS" (ou tous si "all").

## Étape 1 : Identifier les cellules vides

```python
import openpyxl
wb = openpyxl.load_workbook('Suivi_Finishers_Monde_10k_-_21k_-_42k_HISTORIQUE.xlsx', data_only=True)
ws = wb['ALL']
header = [c.value for c in ws[1]]
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row[3]: continue
    name = str(row[3]).strip()
    # Filter par argument si spécifié
    empty = [int(h) for i,h in enumerate(header) if isinstance(h,(int,float)) and (row[i] is None or str(row[i]).strip() == '')]
    if empty:
        print(f'{name} ({row[2]}): {len(empty)} vides - {empty}')
```

## Étape 2 : Chercher les données

Pour chaque cellule vide, utiliser les APIs dans l'ordre :
1. Sporthive (si event ID connu)
2. MarathonView (pour les marathons)
3. Tracx (si event ID connu)
4. Athlinks (pour les courses US)
5. RTRT.me (pour Great Run)
6. TimeTo (pour ASO France)
7. Active.com (pour ASO anciens)
8. Web search ciblé

## Étape 3 : Appliquer

```
python update_finishers.py "Race Name" DISTANCE YEAR COUNT
```

Règles : pas de chiffres ronds, pas d'écrasement, pas de virtual, 5K-Marathon uniquement.

## Étape 4 : Déployer

```
python generate_dashboard.py && git add -A && git commit -m "Fill empty cells for EVENT" && git push
```
