"""Contexte du tableau de bord de l'admin Unfold (Koyra Distribution)."""
import json

from django.db.models import Count
from django.urls import reverse
from django.utils import timezone

from .models import Categorie, Marque, MessageContact, Produit

# Palette Koyra
VERT = "#2E5A27"
TERRACOTTA = "#C85A17"
OR_DOUX = "#C5A059"


def badge_messages_non_traites(request):
    """Pastille affichée dans la sidebar à côté de « Messages de contact »."""
    n = MessageContact.objects.filter(traite=False).count()
    return n or None


def dashboard_callback(request, context):
    total_produits = Produit.objects.count()
    produits_dispo = Produit.objects.filter(disponible=True).count()
    total_messages = MessageContact.objects.count()
    messages_non_traites = MessageContact.objects.filter(traite=False).count()
    taux_traitement = (
        round((total_messages - messages_non_traites) / total_messages * 100)
        if total_messages
        else 100
    )

    context["koyra_kpis"] = [
        {
            "label": "Marques",
            "value": Marque.objects.count(),
            "sous_titre": f"{Marque.objects.filter(bientot_disponible=True).count()} bientôt disponibles",
            "icon": "storefront",
            "url": reverse("admin:catalogue_marque_changelist"),
        },
        {
            "label": "Catégories",
            "value": Categorie.objects.count(),
            "sous_titre": "réparties par marque",
            "icon": "category",
            "url": reverse("admin:catalogue_categorie_changelist"),
        },
        {
            "label": "Produits",
            "value": total_produits,
            "sous_titre": f"{produits_dispo} en ligne",
            "icon": "inventory_2",
            "url": reverse("admin:catalogue_produit_changelist"),
        },
        {
            "label": "Messages en attente",
            "value": messages_non_traites,
            "sous_titre": f"{taux_traitement}% traités",
            "icon": "mark_email_unread",
            "url": reverse("admin:catalogue_messagecontact_changelist"),
            "accent": messages_non_traites > 0,
        },
    ]

    marques = (
        Marque.objects.annotate(n=Count("categories__produits"))
        .order_by("-n", "nom")[:8]
    )
    context["koyra_chart"] = json.dumps(
        {
            "labels": [m.nom for m in marques] or ["Aucune marque"],
            "datasets": [
                {
                    "label": "Produits",
                    "data": [m.n for m in marques] or [0],
                    "backgroundColor": VERT,
                    "borderRadius": 6,
                    "maxBarThickness": 44,
                }
            ],
        }
    )
    context["koyra_chart_options"] = json.dumps(
        {
            "plugins": {"legend": {"display": False}},
            "scales": {
                "y": {"beginAtZero": True, "ticks": {"precision": 0}},
                "x": {"grid": {"display": False}},
            },
        }
    )

    context["koyra_recent_messages"] = MessageContact.objects.all()[:6]
    context["koyra_now"] = timezone.now()
    return context
