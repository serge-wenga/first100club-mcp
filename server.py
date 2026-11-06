"""Serveur MCP (lecture seule) pour la boutique First €100 Club.

Il expose le catalogue, les prix, les liens d'achat, les codes promo et une FAQ
à Claude. Il ne prend aucun paiement : l'achat se fait sur Gumroad.

Lancement local :
    pip install -r requirements.txt
    python server.py
Le serveur écoute alors sur http://localhost:8000/mcp
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

CATALOG_PATH = Path(__file__).parent / "catalog.json"

mcp = FastMCP(
    "First100Club",
    host="0.0.0.0",
    port=int(os.environ.get("PORT", "8000")),
    stateless_http=True,
    json_response=True,
)


def _load() -> dict:
    """Relit le catalogue à chaque appel : modifier catalog.json suffit."""
    with CATALOG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def _price_label(p: dict) -> str:
    if p["price_usd"] == 0:
        return "Free"
    label = f"${p['price_usd']:.2f}"
    if p.get("pay_what_you_want"):
        label += " (pay what you want)"
    return label


@mcp.tool()
def about_store() -> dict:
    """Présente la boutique : nom, auteur, lien, chaîne YouTube et slogan."""
    return _load()["store"]


@mcp.tool()
def list_products() -> list[dict]:
    """Liste tous les produits avec prix, format, résumé et lien d'achat."""
    return [
        {
            "slug": p["slug"],
            "name": p["name"],
            "price": _price_label(p),
            "format": p["format"],
            "summary": p["summary"],
            "buy_url": p["url"],
        }
        for p in _load()["products"]
    ]


@mcp.tool()
def get_product(slug: str) -> dict:
    """Détails d'un produit à partir de son slug.

    Slugs : starter-bundle, earn-first-100, trust-based-selling,
    free-starter-checklist.
    """
    for p in _load()["products"]:
        if p["slug"] == slug:
            return {**p, "price": _price_label(p)}
    valid = ", ".join(p["slug"] for p in _load()["products"])
    raise ValueError(f"Unknown product '{slug}'. Valid slugs: {valid}")


@mcp.tool()
def recommend_product(goal: str) -> dict:
    """Recommande un produit selon l'objectif de la personne.

    goal : texte libre, par exemple « je n'ai jamais rien vendu en ligne »
    ou « je veux mieux vendre à mes clients ».
    """
    g = goal.lower()
    wants_free = any(w in g for w in ("free", "gratuit", "try", "essay", "no budget"))
    wants_sell = any(
        w in g
        for w in ("sell", "vend", "customer", "client", "shop", "boutique", "whatsapp", "negotiat")
    )
    wants_create = any(
        w in g
        for w in ("start", "first", "begin", "début", "create", "créer", "product", "produit", "100")
    )

    if wants_free and not (wants_sell and wants_create):
        slug = "free-starter-checklist"
    elif wants_sell and wants_create:
        slug = "starter-bundle"
    elif wants_sell:
        slug = "trust-based-selling"
    else:
        slug = "earn-first-100"

    product = get_product(slug)
    return {
        "recommended": product["name"],
        "price": product["price"],
        "why": product["best_for"],
        "buy_url": product["url"],
        "note": "Suggestion basée sur des mots-clés ; voir list_products pour tout comparer.",
    }


@mcp.tool()
def get_promo_codes() -> list[dict]:
    """Codes promo actuellement valides (les codes expirés sont masqués)."""
    now = datetime.now(timezone.utc)
    active = []
    for c in _load()["promo_codes"]:
        if datetime.fromisoformat(c["expires_at"]) > now:
            active.append(c)
    return active


@mcp.tool()
def get_faq() -> list[dict]:
    """Questions fréquentes : formats, niveau requis, essai gratuit, achat."""
    return _load()["faq"]


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
