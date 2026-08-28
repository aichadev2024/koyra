from django.contrib import admin
from .models import Marque, Categorie, Produit, MessageContact

@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display = ('nom', 'secteur', 'bientot_disponible', 'ordre')
    list_editable = ('ordre', 'bientot_disponible')
    list_filter = ('secteur', 'bientot_disponible')
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom',)

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'marque', 'ordre')
    list_editable = ('ordre',)
    list_filter = ('marque',)
    prepopulated_fields = {'slug': ('nom',)}
    search_fields = ('nom', "marque__nom")

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'variante', 'categorie', 'disponible', 'ordre')
    list_editable = ('disponible', 'ordre')
    list_filter = ('disponible', 'categorie', 'categorie__marque')
    prepopulated_fields = {'slug': ('nom', 'variante')}
    search_fields = ('nom', 'variante')

@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ('nom', 'sujet', 'date_envoi', 'traite')
    list_filter = ('traite', 'date_envoi')
    search_fields = ('nom', 'email', 'sujet', 'message')
    readonly_fields = ('nom', 'email', 'telephone', 'sujet', 'message', 'date_envoi')
