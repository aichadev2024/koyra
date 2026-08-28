from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('marque/<slug:slug>/', views.fiche_marque, name='fiche_marque'),
    path('categorie/<slug:slug>/', views.fiche_categorie, name='fiche_categorie'),
    path('produit/<slug:slug>/', views.fiche_produit, name='fiche_produit'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('contact/', views.contact, name='contact'),
]
