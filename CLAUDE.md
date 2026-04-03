# DataPace — Contexte projet pour Claude Code

## Identité du projet
- **Projet** : DataPace — Intelligence data du running mondial
- **Entité légale** : NEXT:RACE SASU (Toulouse, France)
- **Contact** : mathis.brun@orange.fr
- **LinkedIn** : [lien LinkedIn Mathis]
- **Instagram** : compte DataPace running

## Repos GitHub
- **Repo commercial (CE PROJET)** : https://github.com/mathbrn/datapace
- **Repo ASO (usage interne, NE PAS TOUCHER)** : https://github.com/mathbrn/datapace-dashboard
- **Dashboard commercial en ligne** : https://mathbrn.github.io/datapace/datapace_dashboard.html
- **Landing page** : https://mathbrn.github.io/datapace/index.html

## Règle absolue
Toujours commit et push sur le repo **datapace** uniquement.
Ne jamais toucher au repo datapace-dashboard (version ASO interne).

## Architecture des fichiers
```
datapace-web/
├── generate_dashboard.py       ← Script principal : lit les Excel, génère le HTML
├── datapace_dashboard.html     ← Généré automatiquement par le script
├── index.html                  ← Landing page commerciale
├── shared/
│   └── design-system.css       ← CSS commun landing + dashboard
├── assets/
│   ├── Logo_DataPace_primary.png   ← Logo icône seul (fond transparent)
│   └── logo_DataPace_text.png      ← Logo avec texte "DataPace." (fond transparent)
├── Suivi_Finishers_Monde_10k_-21k-_42k.xlsx   ← Données finishers 2000-2026
├── Temps_moyen_par_marathon_2024.xlsx
├── Temps_moyen_par_marathon_2025.xlsx
├── Temps_moyen_par_marathon_2026.xlsx
├── Temps_moyen_semi-marathon_2025.xlsx
└── .github/
    └── workflows/
        └── generate.yml        ← GitHub Actions
```

## Workflow de mise à jour
1. Modifier les fichiers (Excel ou code)
2. Si Excel modifié → lancer `python generate_dashboard.py` pour régénérer le HTML
3. `git add .` → `git commit -m "message"` → `git push`
4. GitHub Pages se met à jour automatiquement en ~30 secondes
5. Ctrl+Shift+R dans le navigateur pour vider le cache

## Données
- **Fichier principal** : `Suivi_Finishers_Monde_10k_-_21k_-_42k.xlsx`
  - Feuilles : ALL, 10K, 21K, 42K, BIGGEST EVENTS
  - Colonnes : Période, City, Distance, Race + années 2000 à 2026
  - 116 courses trackées
- **generate_dashboard.py** lit toutes les années disponibles dynamiquement
- Les données historiques vont de 2000 à 2026 selon les événements

## Charte visuelle — Règles absolues

### Couleurs par distance
- **MARATHON** → violet `#5C00D4`
- **SEMI-marathon** → orange (couleur définie dans le CSS)
- **10KM** → vert (couleur définie dans le CSS)
- Ces couleurs s'appliquent partout : barres, lignes, bordures, badges

### Couleurs globales
```css
--bg: #0a0a0a
--bg2: #111
--bg3: #161616
--purple: #5C00D4
--yellow: #FCDB00
--green: #22C55E
--text: #f0f0f0
--text2: #888
--text3: #555
```

### Typographie
- Police unique : **Inter** (Google Fonts)
- Titres landing : **Playfair Display** (Google Fonts)

### Badges partenaires (onglet Sponsoring + Vue d'ensemble)
- **TITRE** → fond COLOR_MAIN opacity 0.15, bordure COLOR_MAIN pleine, texte COLOR_MAIN
- **PREMIUM** → fond COLOR_MAIN opacity 0.12, bordure COLOR_MAIN opacity 0.7
- **OFFICIEL** → fond COLOR_MAIN opacity 0.08, bordure COLOR_MAIN opacity 0.5
- **FOURNISSEUR** → fond transparent, bordure #ffffff25, texte #888
- COLOR_MAIN = couleur de la distance de l'événement (violet/orange/vert)

### Graphiques Chart.js
- Grille : `rgba(255,255,255,0.03)` (quasi invisible)
- Ticks : fontSize 10, color `#555`
- Barres finishers : couleur de la distance de l'événement
- Record Homme : couleur principale de la distance (pleine)
- Record Femme : variante plus claire de la couleur de distance (+40% lightness HSL)
- Fill sous courbe : couleur à opacity 0.08
- Points : 4px, même couleur que la ligne
- maxRotation: 0, minRotation: 0 sur les axes X (labels horizontaux)
- barThickness: 18, borderRadius: 4 pour les barres

### Scrollbars custom
```css
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #ffffff18; border-radius: 999px; }
::-webkit-scrollbar-thumb:hover { background: #5C00D4; }
* { scrollbar-width: thin; scrollbar-color: #ffffff18 transparent; }
```

## Onglets du dashboard
1. **Tableau** — toutes les courses avec filtres (distance, mois, région, badge, taille, tri, période)
2. **Insights** — Top 5 croissance / Top 5 déclin (min 3 années de données), métriques clés, filtre distance
3. **Vue d'ensemble** — fiche détaillée d'un événement, affichage adaptatif selon données disponibles
4. **Comparer** — comparaison VS entre deux événements + graphique évolution superposée
5. **Evolution** — courbes d'évolution multi-événements
6. **Top événements** — classement par finishers avec barres horizontales colorées par distance
7. **Temps moyen** — barres temps moyen par course (marathon/semi, 2024/2025/2026)
8. **Winners Times** — chronos vainqueurs homme/femme
9. **Sponsoring** — données partenaires par marque et par événement

## Règles d'affichage adaptatif (Vue d'ensemble)
- 0 donnée → ne pas afficher le composant
- 1 donnée → card simple, pas de graphique
- 2 données → graphique avec mention "données limitées"
- 3+ données → graphique complet
- Axe Y finishers : minimum toujours à 0
- Années sans données : barres grises transparentes `#ffffff08`

## Light mode
- Activé via toggle "Dark/Light" en haut à droite
- `--bg: #f8f8f8`, `--bg2: #ffffff`, `--bg3: #f0f0f0`
- `--border: rgba(0,0,0,0.08)`, `--text: #0a0a0a`, `--text3: #888`
- Grilles Chart.js : `rgba(0,0,0,0.05)`
- Scrollbar thumb : `rgba(0,0,0,0.15)`
- Tous les onglets doivent être lisibles en light mode

## Landing page (index.html)
- Navbar fixe : logo gauche, liens centre, bouton CTA droite
- Hero 100vh : glow violet animé, titre Playfair Display, badge pill, 2 boutons CTA
- Bande logos défilante : grands événements running
- Section "Pour qui ?" : 3 cartes (Organisateurs / Marques / Médias)
- Section données alternée : texte + visuels
- CTA final fond violet
- Footer : logo + liens + email + LinkedIn + "DataPace © 2026 · NEXT:RACE SASU"

## Interactivité
- Clic sur événement dans Top événements → ouvre Vue d'ensemble
- Clic sur événement dans Insights → ouvre Vue d'ensemble
- Clic sur ligne dans Tableau → ouvre Vue d'ensemble
- Bouton "← Dashboard" dans Vue d'ensemble pour revenir

## Architecture des donnees (hérité du repo interne)

### Source de verite pour le dashboard
`generate_dashboard.py` utilise **SQLite en priorite** si `datapace.db` existe, sinon les fichiers Excel.
- Si `datapace.db` existe → lit depuis SQLite (tables `events`, `finishers`, `winners`, `avg_times`)
- Sinon → lit depuis les fichiers Excel

### Ou sont stockes les noms d'evenements (TOUS a modifier lors d'un renommage)
1. **`datapace.db`** (SQLite) : table `events` colonne `name` — **SOURCE PRIMAIRE du dashboard**. Les tables `finishers`, `winners`, `avg_times` referencent par `event_id` (FK).
2. **`Suivi_Finishers_Monde_10k_-_21k_-_42k_HISTORIQUE.xlsx`** : onglet ALL, colonne D (Race)
3. **`Chronos_Vainqueurs.xlsx`** : colonne Race (genere par `create_chronos.py`, verifier aussi le .py)
4. **`_event_list.json`** : liste plate des noms d'evenements
5. **`event_websites.json`** : cles = noms d'evenements
6. **`sponsoring_data.json`** : champ `event` dans chaque entree
7. **`scraped_partners.json`** : champ `event`
8. **`compile_websites.py`** : appels `add("NomEvenement", ...)`
9. **`_scrape_queue.json`** : champ `event`

### Ou sont stockees les donnees de finishers
1. **`datapace.db`** : table `finishers` (event_id, year, count, source)
2. **`Suivi_Finishers_Monde_10k_-_21k_-_42k_HISTORIQUE.xlsx`** : onglet ALL (colonnes annees 2000-2026), onglet BIGGEST EVENTS
3. **`avg_times_sporthive.json`** : temps moyens calcules depuis APIs

### Ou sont stockes les temps vainqueurs
1. **`datapace.db`** : table `winners` (event_id, year, men_time, women_time)
2. **`Chronos_Vainqueurs.xlsx`** : genere par `create_chronos.py` (donnees en dur dans le script)

### Ou sont stockes les temps moyens
1. **`datapace.db`** : table `avg_times`
2. **`Temps_moyen_semi-marathon.xlsx`** : multi-feuilles par annee
3. **`Temps_moyen_par_marathon_{2024,2025,2026}.xlsx`** : une feuille par annee
4. **`avg_times_sporthive.json`** : temps moyens calcules depuis APIs (Sporthive + Tracx)

## Regles strictes

### Donnees finishers
- **JAMAIS ecraser une cellule deja remplie** dans le fichier Excel finishers. Le script `update_finishers.py` a une protection [SKIP].
- **ZERO tolerance pour les chiffres ronds** (10000, 20000, 30000...). Ce sont des estimations ou des caps d'inscription, pas des finishers exacts.
- **Exclure les finishers VIRTUAL** des comptages. Toujours filtrer "virtual" dans les APIs.
- **Exclure les courses de plus de 42.195km** (pas d'ultras, pas de trail).
- Cellules speciales dans le Excel : `-` = edition annulee, `Elite` = edition elite uniquement, `x` = evenement n'existait pas encore.

### Distances
- `MARATHON` : 42.195km
- `SEMI` : ~21.1km (half marathon)
- `10KM` : 10km
- `AUTRE` : distances non-standard (10 miles, 12K, 15K, etc.)

### Badges evenements
- `WMM` (bleu #38BDF8) : World Marathon Majors (NYC, London, Boston, Sydney, Berlin, Chicago, Tokyo)
- `ASO` (jaune #FCDB00) : Evenements ASO (Paris, Lyon, 10K Paris, Montmartre, Manchester, London Winter Run, ASICS LDNX)
- `Autre` (violet #9B6FFF) : Tous les autres

### Premiere edition
- Marquer `x` dans le Excel pour toutes les annees AVANT la premiere edition d'un evenement
- Dashboard : petite etoile dans la couleur de l'evenement sur la cellule de la premiere edition (uniquement si >= 2000)
- Pas d'etoile pour les evenements crees avant 2000

## APIs decouvertes et exploitees

### 1. Sporthive/MYLAPS (MEILLEURE SOURCE)
- **API** : `https://eventresults-api.speedhive.com/sporthive/events/{eventId}/races`
- **Auth** : Aucune
- **Donnees** : `classificationsCount` = finishers, `raceStatistics.averageSpeedInKmh` = vitesse moyenne reelle
- **Decouverte IDs** : `site:results.sporthive.com` sur Google, ou Playwright
- **Calcul temps moyen** : `temps = distance / vitesse`

### 2. Tracx Events
- **API** : `https://api.tracx.events/v1/`
- **Auth** : `Authorization: Bearer 40496C26-9BEF-4266-8A27-43C78540F669`
- **Events** : `GET /events?page=1&per_page=100` (860 events total)
- **Races** : `GET /events/{id}/races` → `participant_count` direct
- **Results** : `GET /events/{id}/races/{raceId}/rankings/{rankingId}/results?page=1` → resultats individuels avec temps
- **Temps vainqueur** : premier resultat male + premier resultat female dans les rankings

### 3. Athlinks (US races)
- **Metadata** : `https://reignite-api.athlinks.com/master/{masterEventId}/metadata`
- **Course** : `https://alaska.athlinks.com/Events/Race/Api/{eventId}/Course/0`
- **Finishers** : `EventCoursesDropDown[].Value` = `courseId:raceId:FINISHER_COUNT:??` (3eme champ)
- **Auth** : Aucune
- **Decouverte IDs** : `site:athlinks.com/event "Event Name"`

### 4. RTRT.me (Great Run events)
- **API** : `https://api.rtrt.me/`
- **Auth** : `appid=623f2dd5e7847810bb1f0a07&token=9FA560A93CFC014488AB`
- **Total** : `GET /events/{code}` → `finishers` = total
- **Par course** : `GET /events/{code}/stats` → `stats.tags.{course}.FINISH-*.valid_count`
- **Codes** : `GR-NORTH-{YYYY}`, `GR-SCOTTISH-{YYYY}`, `GR-MANCHESTER-{YYYY}`, `GR-BRISTOL-{YYYY}`, `GR-BIRMINGHAM-{YYYY}`, `GR-SOUTH-{YYYY}`
- **Couverture** : 2022-2025 uniquement

### 5. TimeTo / SportInnovation (ASO France)
- **Events** : `https://sportinnovation.fr/api/events`
- **Races** : `https://sportinnovation.fr/api/events/{id}/races`
- **Finishers** : `totals.maxGeneralRanking`
- **Auth** : Aucune
- **Couverture** : Marathon de Paris, Semi de Paris, 10K Paris, Run in Lyon, Run in Marseille

### 6. Active.com (ASO events anciens)
- **Events** : `https://resultscui.active.com/api/results/events/{appName}`
- **Count** : `GET /events/{appName}/participants?groupId={overallId}&routeId={id}&offset=0&limit=1` → `meta.totalCount`
- **Auth** : Aucune
- **Noms d'app** : `{Sponsor}{EventName}{Year}` (ex: `SchneiderElectricMarathondeParis2019`, `RunInLyon2018`, `Adidas10KParis2022`)

### 7. Mikatiming (scraping)
- **URL** : `https://{event}.r.mikatiming.com/{year}/?pid=list&event={code}`
- **Codes** : HML=Half Marathon, MAL=Marathon
- **Extraction** : regex `(\d[\d.]*)\s*(?:Ergebnisse|Results)` dans le texte de la page
- **Couverture** : Berlin HM, Frankfurt Marathon, Stockholm

### 8. MarathonView.net (scraping)
- **URL** : `https://marathonview.net/series/{id}`
- **Donnees** : finishers par annee dans le JSON embarque
- **WebFetch** fonctionne
- **Couverture** : 500+ series de marathons mondiaux

### 9. World Athletics GraphQL (catalogue)
- **Endpoint** : `https://graphql-prod-4860.edge.aws.worldathletics.org/graphql`
- **API Key** : `da2-5eqvkoavsnhjxfqd47jvjteray`
- **Operation** : `getCalendarEvents` avec variables startDate/endDate/regionType/limit/offset
- **Donnees** : Catalogue de 807 road races/an (pas de resultats de masse)

### 10. SportTimingSolutions (Inde)
- **API** : `https://sportstimingsolutions.in/frontend/api/`
- **Races** : `GET /event-races?event_id={id}` (base64-encoded)
- **Finishers** : `GET /event/bib/result?event_id={id}&bibNo={bib}` → `brackets[].bracket_participants`
- **Necessite** un bib valide

### 11. Njuko (inscription uniquement)
- **API** : `https://front-api.njuko.com/`
- **Donnees** : Details evenement, competitions, places restantes
- **PAS de resultats** — renvoie vers les plateformes de chronometrage

## Scripts utilitaires

- `update_finishers.py "Race Name" DISTANCE YEAR COUNT` : Met a jour une cellule (avec protection SKIP)
- `add_event.py "Period" "City" "Distance" "Race Name" [YEAR COUNT ...]` : Ajoute un nouvel evenement
- `create_chronos.py` : Genere Chronos_Vainqueurs.xlsx depuis les donnees en dur
- `mark_first_editions.py` : Marque les cellules pre-premiere-edition avec 'x'
- `scrape_finishers.py` : Scraper generique via Playwright (interception reseau)
- `crawl_sporthive.py` : Crawler Sporthive par decouverte d'IDs
- `crawl_tracx.py` : Crawler exhaustif des 860 events Tracx
- `crawl_athlinks.py` : Scanner Athlinks par range d'IDs
- `aggregate_all.py` : Fusionneur de toutes les sources → `unified_race_database.json`

## Ce qui reste à faire (priorités)
- [ ] Finaliser les corrections du light mode sur tous les onglets
- [ ] Onglet Top événements : couleurs par distance, rangs #1 #2 #3, clic vers Vue d'ensemble
- [ ] Onglet Comparer : graphique évolution superposée, couleurs par distance
- [ ] Onglet Evolution : étendre à toutes les années disponibles
- [ ] Export CSV depuis le tableau
- [ ] Optimisation mobile
- [ ] Domaine personnalisé (datapace.fr à terme)
