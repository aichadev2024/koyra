from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Marque, Categorie, Produit, MessageContact

def accueil(request):
    marques = Marque.objects.all()
    produits_vedettes = Produit.objects.filter(disponible=True)[:4]
    return render(request, 'catalogue/accueil.html', {
        'marques_agro': marques.filter(secteur='AGRO'),
        'marques_cosm': marques.filter(secteur='COSM'),
        'produits_vedettes': produits_vedettes,
    })

def liste_produits(request):
    produits = Produit.objects.filter(disponible=True)
    marques = Marque.objects.all()
    
    # Filtre par marque si fourni dans GET
    marque_slug = request.GET.get('marque')
    if marque_slug:
        produits = produits.filter(categorie__marque__slug=marque_slug)

    return render(request, 'catalogue/liste_produits.html', {
        'produits': produits,
        'marques': marques,
        'marque_active': marque_slug
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
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone', '')
        sujet = request.POST.get('sujet')
        message = request.POST.get('message')
        
        # Enregistrement du message
        MessageContact.objects.create(
            nom=nom,
            email=email,
            telephone=telephone,
            sujet=sujet,
            message=message
        )
        messages.success(request, 'Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.')
        return redirect('catalogue:contact')

    return render(request, 'catalogue/contact.html')
