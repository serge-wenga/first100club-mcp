# Serveur MCP First €100 Club

Serveur MCP en lecture seule qui permet à Claude de connaître ta boutique :
produits, prix, liens d'achat, code promo et FAQ. Il ne prend aucun paiement.

## Outils exposés

| Outil | Rôle |
|---|---|
| `about_store` | Présentation de la boutique |
| `list_products` | Tous les produits, prix et liens |
| `get_product` | Détails d'un produit (par slug) |
| `recommend_product` | Conseille un produit selon l'objectif |
| `get_promo_codes` | Codes promo encore valides |
| `get_faq` | Questions fréquentes |

## 1. Tester en local

```bash
pip install -r requirements.txt
python server.py
```

Le serveur répond sur `http://localhost:8000/mcp`.

## 2. Le mettre en ligne (obligatoire pour Claude)

Claude se connecte à un serveur **distant en HTTPS**. Un serveur sur ton ordinateur
ne suffit pas. Déploie ce dossier chez un hébergeur Python (Render, Railway,
Fly.io…) :

- commande de démarrage : `python server.py`
- le serveur lit la variable d'environnement `PORT` fournie par l'hébergeur
- une fois en ligne, l'adresse sera du type `https://ton-serveur.exemple.com/mcp`

## 3. Le connecter à Claude

Dans Claude, ouvre les paramètres des connecteurs, ajoute un **connecteur
personnalisé** et colle l'adresse `https://ton-serveur.exemple.com/mcp`.
Le nom exact des menus peut varier selon l'application ; vérifie dans l'aide
de Claude si besoin.

## 4. Mettre à jour tes produits

Modifie uniquement `catalog.json` (prix, nouveaux produits, codes promo) puis
redéploie. Le code `LAUNCH15` expire le 12 novembre 2026 et disparaît ensuite
automatiquement de `get_promo_codes`.

## Sécurité

- Aucun mot de passe ni clé API n'est utilisé ou stocké.
- Le serveur est public par défaut : il ne doit contenir que des informations
  que tu veux montrer à tout le monde.
