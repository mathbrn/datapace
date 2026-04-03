# Régénérer et déployer le dashboard

Régénère le dashboard HTML à partir de toutes les sources de données et pousse sur GitHub.

## Commandes

```bash
cd "C:\Users\mathi\Documents\6. DATA PACE\0. Dashboard\Fichiers sources"

# 1. Régénérer les chronos vainqueurs
python create_chronos.py

# 2. Régénérer le dashboard HTML
python generate_dashboard.py

# 3. Vérifier le taux de remplissage
python -c "
import openpyxl
wb = openpyxl.load_workbook('Suivi_Finishers_Monde_10k_-_21k_-_42k_HISTORIQUE.xlsx', data_only=True)
ws = wb['ALL']
header = [c.value for c in ws[1]]
total = filled = x_cells = data_cells = 0
for row in ws.iter_rows(min_row=2, values_only=True):
    if not row[3]: continue
    for i,h in enumerate(header):
        if isinstance(h,(int,float)):
            total += 1
            val = row[i]
            if val is not None and str(val).strip() != '':
                filled += 1
                sv = str(val).strip().lower()
                if sv == 'x': x_cells += 1
                elif sv not in ('-', 'elite'): data_cells += 1
print(f'Fill: {filled}/{total} ({100*filled/total:.1f}%)')
print(f'Relevant: {(filled-x_cells)}/{total-x_cells} ({100*(filled-x_cells)/(total-x_cells):.1f}%)')
print(f'Data: {data_cells}')
"

# 4. Commit et push
git add -A
git commit -m "Update dashboard"
git push
```

## Fichiers générés
- `datapace_dashboard.html` : Dashboard single-page (ouvrir dans navigateur)
- `Chronos_Vainqueurs.xlsx` : Fichier Excel des temps vainqueurs
