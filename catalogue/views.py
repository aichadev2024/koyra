import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PremierAdminForm
from .models import Marque, Categorie, Produit, MessageContact

logger = logging.getLogger(__name__)


def _envoyer_emails_contact(msg):
    """Notifie Koyra et accuse réception au visiteur. Silencieux en cas d'échec."""
    sujet_interne = f"[Contact site] {msg.sujet}"
    corps_interne = (
        f"Nouveau message reçu via le formulaire de contact.\n\n"
        f"Nom      : {msg.nom}\n"
        f"Email    : {msg.email}\n"
        f"Téléphone: {msg.telephone or '—'}\n"
        f"Sujet    : {msg.sujet}\n"
        f"Date     : {msg.date_envoi:%d/%m/%Y %H:%M}\n\n"
        f"Message :\n{msg.message}\n"
    )
    try:
        send_mail(
            sujet_interne,
            corps_interne,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_NOTIFICATION_EMAIL],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Échec de l'envoi de la notification de contact")

    corps_accuse = (
        f"Bonjour {msg.nom},\n\n"
        "Nous avons bien reçu votre message et vous remercions de votre intérêt "
        "pour Koyra Distribution. Notre équipe vous répondra dans les plus brefs délais.\n\n"
        "Pour rappel, voici votre message :\n"
        f"« {msg.message} »\n\n"
        "Bien à vous,\n"
        "L'équipe Koyra Distribution"
    )
    try:
        send_mail(
            "Votre message a bien été reçu — Koyra Distribution",
            corps_accuse,
            settings.DEFAULT_FROM_EMAIL,
            [msg.email],
            fail_silently=True,
        )
    except Exception:
        logger.exception("Échec de l'envoi de l'accusé de réception au visiteur")

def accueil(request):
    marques = Marque.objects.all()
    produits_vedettes = Produit.objects.filter(disponible=True)[:4]
    return render(request, 'catalogue/accueil.html', {
        'marques_agro': marques.filter(secteur='AGRO'),
        'marques_cosm': marques.filter(secteur='COSM'),
        'produits_vedettes': produits_vedettes,
    })

SECTEURS_CATALOGUE = [
    {
        'code': 'AGRO',
        'libelle': 'Agroalimentaire',
        'kicker': 'Pôle agroalimentaire',
        'accroche': "Condiments, épices et bouillons naturels, façonnés selon les gestes du terroir malien.",
    },
    {
        'code': 'COSM',
        'libelle': 'Cosmétique',
        'kicker': 'Pôle cosmétique',
        'accroche': "Des soins naturels sobres et généreux, pensés pour les peaux riches en mélanine.",
    },
]


def liste_produits(request):
    produits = (
        Produit.objects.filter(disponible=True)
        .select_related('categorie', 'categorie__marque')
    )
    marques = Marque.objects.all()

    secteur = request.GET.get('secteur')
    if secteur not in ('AGRO', 'COSM'):
        secteur = None

    marque_slug = request.GET.get('marque')
    if marque_slug:
        produits = produits.filter(categorie__marque__slug=marque_slug)
        # on aligne le secteur actif sur la marque choisie
        marque = marques.filter(slug=marque_slug).first()
        if marque:
            secteur = marque.secteur

    if secteur:
        produits = produits.filter(categorie__marque__secteur=secteur)

    produits = list(produits)

    # Regroupement par univers pour l'affichage en sections distinctes
    groupes = []
    for info in SECTEURS_CATALOGUE:
        if secteur and info['code'] != secteur:
            continue
        groupes.append({
            **info,
            'produits': [p for p in produits if p.categorie.marque.secteur == info['code']],
        })

    return render(request, 'catalogue/liste_produits.html', {
        'groupes': groupes,
        'marques': marques,
        'secteur_actif': secteur,
        'marque_active': marque_slug,
    })

def fiche_marque(request, slug):
    marque = get_object_or_404(Marque, slug=slug)
    categories = marque.categories.all()
    return render(request, 'catalogue/fiche_marque.html', {
        'marque': marque,
        'categories': categories
    })

def fiche_categorie(request, slug):
    categorie = get_object_or_404(Categorie, slug=slug)
    produits = categorie.produits.filter(disponible=True)
    return render(request, 'catalogue/fiche_categorie.html', {
        'categorie': categorie,
        'produits': produits
    })

def fiche_produit(request, slug):
    produit = get_object_or_404(Produit, slug=slug)
    # Suggestions : autres produits de la même gamme
    suggestions = Produit.objects.filter(categorie=produit.categorie, disponible=True).exclude(id=produit.id)[:4]
    return render(request, 'catalogue/fiche_produit.html', {
        'produit': produit,
        'suggestions': suggestions
    })

def a_propos(request):
    return render(request, 'catalogue/a_propos.html')

def contact(request):
    if request.method == 'POST':
        nom = (request.POST.get('nom') or '').strip()
        email = (request.POST.get('email') or '').strip()
        telephone = (request.POST.get('telephone') or '').strip()
        sujet = (request.POST.get('sujet') or '').strip()
        message = (request.POST.get('message') or '').strip()

        # Honeypot anti-spam : champ caché qui doit rester vide.
        if request.POST.get('site_web'):
            messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.")
            return redirect('catalogue:contact')

        erreurs = []
        if not nom or not sujet or not message:
            erreurs.append("Merci de renseigner votre nom, le sujet et le message.")
        try:
            validate_email(email)
        except ValidationError:
            erreurs.append("L'adresse e-mail saisie n'est pas valide.")

        if erreurs:
            for err in erreurs:
                messages.error(request, err)
            return render(request, 'catalogue/contact.html', {
                'valeurs': {
                    'nom': nom, 'email': email, 'telephone': telephone,
                    'sujet': sujet, 'message': message,
                },
            })

        msg = MessageContact.objects.create(
            nom=nom, email=email, telephone=telephone, sujet=sujet, message=message,
        )
        _envoyer_emails_contact(msg)
        messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.")
        return redirect('catalogue:contact')

    return render(request, 'catalogue/contact.html', {
        'valeurs': {'sujet': request.GET.get('sujet', '')},
    })


def installation_admin(request, token):
    """Création unique du premier compte administrateur.

    Accessible seulement si : un jeton ADMIN_SETUP_TOKEN est configuré ET
    correspond, ET qu'aucun super-utilisateur n'existe encore. Sinon : 404.
    """
    attendu = getattr(settings, 'ADMIN_SETUP_TOKEN', '')
    if not attendu or token != attendu:
        raise Http404
    if User.objects.filter(is_superuser=True).exists():
        raise Http404

    if request.method == 'POST':
        form = PremierAdminForm(request.POST)
        if form.is_valid() and not User.objects.filter(is_superuser=True).exists():
            user = form.save()
            login(request, user)
            logger.info("Premier compte administrateur créé : %s", user.username)
            return redirect('admin:index')
    else:
        form = PremierAdminForm()

    return render(request, 'catalogue/installation_admin.html', {'form': form})
