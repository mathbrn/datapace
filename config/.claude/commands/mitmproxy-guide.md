# Guide mitmproxy pour découvrir des APIs mobiles

Guide pour utiliser mitmproxy afin de découvrir les APIs d'applications mobiles de résultats de course (technique utilisée pour RTRT.me/Great Run).

## Setup

1. `pip install mitmproxy` ou télécharger depuis mitmproxy.org
2. Lancer `mitmweb` (interface web sur localhost:8081)
3. Configurer le proxy WiFi du téléphone → IP du PC, port 8080
4. Ouvrir `mitm.it` sur le téléphone → installer le certificat SSL

## Apps à tester par marché

### Chine
- **爱燃烧 iranshao** : résultats de toutes les courses chinoises
- **咕咚 Gudong** : GPS running avec résultats
- **最酷 Zuicool** : chronométrage + résultats
- **Apps officielles** : Beijing Marathon, Shanghai Marathon

### Europe
- **Great Run app** : résultats Great North/Scottish/Manchester/Bristol Run
- **Njuko** : inscriptions (pas de résultats)
- **Sporthive app** : résultats MYLAPS

### USA
- **Athlinks app** : résultats ChronoTrack
- **RunSignup app** : inscriptions + résultats petites courses

## Ce qu'il faut capturer

Dans mitmproxy, naviguer vers la section résultats/classements d'une course et noter :
1. **URL de l'API** (ex: `api.iranshao.com/v2/races/12345/results`)
2. **Headers d'auth** : Authorization, x-api-key, Bearer token
3. **Paramètres** : pagination (page, limit, offset), filtres
4. **Réponse JSON** : structure, champs clés (total, count, finishers)

## Fournir à Claude

Copier-coller ces infos dans le chat :
```
URL : https://api.example.com/events/123/results?page=1
Authorization : Bearer XXXXXXXX
AppID : XXXXXXXX (si applicable)
Max : 50 (résultats par page)
```

Claude pourra alors requêter l'API directement et crawler les résultats.
