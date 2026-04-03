# Découvrir l'API d'un site de résultats

Analyse le site "$ARGUMENTS" pour découvrir son API de résultats.

## Méthode Playwright (interception réseau)

```python
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    page = ctx.new_page()

    calls = []
    def h(r):
        u = r.url
        ct = r.headers.get('content-type', '')
        if r.status == 200 and ('json' in ct or 'api' in u.lower() or 'graphql' in u.lower()):
            try:
                body = r.text()
                if len(body) > 50 and not any(x in u for x in ['google', 'facebook', 'analytics']):
                    calls.append({'url': u, 'size': len(body), 'body': body[:2000],
                                 'headers': dict(r.request.headers)})
            except: pass
    page.on('response', h)

    page.goto(URL, wait_until='networkidle', timeout=20000)
    page.wait_for_timeout(3000)

    for c in calls:
        print(f'API: {c["url"][:150]} ({c["size"]}b)')
        # Chercher auth headers
        for hk in ['authorization', 'x-api-key', 'x-auth-token']:
            if hk in c['headers']:
                print(f'  AUTH: {hk} = {c["headers"][hk][:80]}')
```

## Ce qu'on cherche

1. **Endpoints JSON** avec des données de résultats (finishers, temps, positions)
2. **Headers d'authentification** (Bearer token, API key)
3. **Structure de pagination** (total, page, per_page)
4. **Champs clés** : total/count/finishers/classificationsCount/participant_count

## Après découverte

1. Tester l'endpoint directement avec curl
2. Vérifier si l'auth est nécessaire ou optionnelle
3. Documenter dans CLAUDE.md section APIs
4. Sauvegarder dans la mémoire (reference_finisher_sources.md)
5. Créer un crawler si la source est riche
