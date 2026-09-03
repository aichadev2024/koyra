from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class PremierAdminForm(UserCreationForm):
    """Création du tout premier compte administrateur (page d'installation)."""

    email = forms.EmailField(required=False, label="Adresse e-mail (optionnel)")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email", "")
        user.is_staff = True
        user.is_superuser = True
        if commit:
            user.save()
        return user
