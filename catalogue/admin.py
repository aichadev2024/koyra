from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import Categorie, Marque, MessageContact, Produit


# -----------------------------------------------------------------------------
# Catalogue
# -----------------------------------------------------------------------------
@admin.register(Marque)
class MarqueAdmin(ModelAdmin):
    list_display = ("nom", "secteur", "statut_disponibilite", "ordre")
    list_editable = ("ordre",)
    list_filter = ("secteur", "bientot_disponible")
    list_filter_submit = True
    prepopulated_fields = {"slug": ("nom",)}
    search_fields = ("nom",)
    compressed_fields = True
    warn_unsaved_form = True

    @display(
        description=_("Disponibilité"),
        label={"Disponible": "success", "Bientôt": "warning"},
    )
    def statut_disponibilite(self, obj):
        return "Bientôt" if obj.bientot_disponible else "Disponible"


@admin.register(Categorie)
class CategorieAdmin(ModelAdmin):
    list_display = ("nom", "marque", "ordre")
    list_editable = ("ordre",)
    list_filter = ("marque",)
    list_filter_submit = True
    prepopulated_fields = {"slug": ("nom",)}
    search_fields = ("nom", "marque__nom")
    autocomplete_fields = ("marque",)
    compressed_fields = True


@admin.register(Produit)
class ProduitAdmin(ModelAdmin):
    list_display = ("nom", "variante", "categorie", "statut_disponible", "ordre")
    list_editable = ("ordre",)
    list_filter = ("disponible", "categorie", "categorie__marque")
    list_filter_submit = True
    prepopulated_fields = {"slug": ("nom", "variante")}
    search_fields = ("nom", "variante")
    autocomplete_fields = ("categorie",)
    compressed_fields = True
    warn_unsaved_form = True

    @display(description=_("État"), boolean=True)
    def statut_disponible(self, obj):
        return obj.disponible


@admin.register(MessageContact)
class MessageContactAdmin(ModelAdmin):
    list_display = ("nom", "sujet", "date_envoi", "statut_traite")
    list_filter = ("traite", "date_envoi")
    list_filter_submit = True
    search_fields = ("nom", "email", "sujet", "message")
    readonly_fields = ("nom", "email", "telephone", "sujet", "message", "date_envoi")
    list_fullwidth = True

    @display(
        description=_("Statut"),
        label={"Traité": "success", "En attente": "danger"},
    )
    def statut_traite(self, obj):
        return "Traité" if obj.traite else "En attente"

    def has_add_permission(self, request):
        return False


# -----------------------------------------------------------------------------
# Auth : on re-enregistre User / Group avec le style Unfold
# -----------------------------------------------------------------------------
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    compressed_fields = True
    warn_unsaved_form = True


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
