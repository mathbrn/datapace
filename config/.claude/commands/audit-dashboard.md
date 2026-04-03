# Audit complet du dashboard

Analyse l'état complet du dashboard et identifie les lacunes à combler.

## Vérifications

### 1. Taux de remplissage par catégorie
```python
import openpyxl
wb = openpyxl.load_workbook('Suivi_Finishers_Monde_10k_-_21k_-_42k_HISTORIQUE.xlsx', data_only=True)
ws = wb['ALL']
header = [c.value for c in ws[1]]
stats = {}
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row[3]: continue
    dist = row[2]
    if dist not in stats: stats[dist] = {'total':0,'filled':0,'x':0,'cancel':0,'data':0}
    for i,h in enumerate(header):
        if isinstance(h,(int,float)):
            stats[dist]['total'] += 1
            val = row[i]
            if val is not None and str(val).strip() != '':
                stats[dist]['filled'] += 1
                sv = str(val).strip().lower()
                if sv == 'x': stats[dist]['x'] += 1
                elif sv == '-': stats[dist]['cancel'] += 1
                else: stats[dist]['data'] += 1
for d,s in sorted(stats.items()):
    rel = s['total'] - s['x']
    pct = 100*(s['filled']-s['x'])/rel if rel else 0
    print(f"{d}: {s['data']} data / {rel} relevant ({pct:.1f}%)")
```

### 2. Événements sans chronos vainqueurs
Comparer les événements dans le Excel avec ceux dans Chronos_Vainqueurs.xlsx.

### 3. Événements sans temps moyen
Comparer avec avg_times_sporthive.json.

### 4. Premières éditions manquantes
Vérifier que tous les événements ont des 'x' avant leur première édition.

### 5. Éditions annulées COVID 2020-2021
Vérifier que toutes les éditions annulées sont marquées '-' et que les éditions qui ont eu lieu ne sont PAS marquées '-'.

### 6. Cohérence des données
- Pas de chiffres ronds suspects
- Pas de données virtual incluses
- Pas de cellules écrasées par erreur
