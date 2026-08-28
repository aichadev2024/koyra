from django.db import models
from django.utils.text import slugify

class Marque(models.Model):
    SECTEUR_CHOICES = [
        ('AGRO', 'Agroalimentaire'),
        ('COSM', 'Cosmétique naturelle'),
    ]
    
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    secteur = models.CharField(max_length=4, choices=SECTEUR_CHOICES, default='AGRO')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='marques/', blank=True, null=True)
    bientot_disponible = models.BooleanField(default=False, verbose_name="Bientôt disponible")
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom


class Categorie(models.Model):
    marque = models.ForeignKey(Marque, related_name='categories', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.marque.nom} - {self.nom}"


class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, related_name='produits', on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    variante = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    disponible = models.BooleanField(default=True)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre', 'nom']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.nom} {self.variante}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nom} {self.variante}".strip()


class MessageContact(models.Model):
    nom = models.CharField(max_length=150)
    email = models.EmailField()
    telephone = models.CharField(max_length=30, blank=True)
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False, verbose_name="Traité")

    class Meta:
        ordering = ['-date_envoi']
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"

    def __str__(self):
        return f"{self.nom} - {self.sujet}"
