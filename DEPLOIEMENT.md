# Déploiement — Koyra Distribution

Site Django (Python 3.12) + PostgreSQL. Ce guide décrit une mise en ligne sur
**Render.com** : hébergement du site, base de données managée, disque pour les
images, HTTPS automatique.

---

## 1. Prérequis (une seule fois)

- Un compte **GitHub** (gratuit) — https://github.com
- Un compte **Render** — https://render.com (connexion via GitHub conseillée)
- Un compte **SMTP** pour l'envoi des e-mails du formulaire de contact
  (Gmail avec « mot de passe d'application », Brevo, SendGrid, ou l'e-mail
  professionnel OVH/IONOS de Koyra).

---

## 2. Pousser le code sur GitHub

Dans le dossier du projet :

```bash
git remote add origin https://github.com/VOTRE-COMPTE/koyra.git
git push -u origin main
```

> Le dépôt peut rester **privé**. Le fichier `.env` n'est jamais envoyé
> (protégé par `.gitignore`).

---

## 3. Créer les services sur Render

Le fichier `render.yaml` à la racine décrit tout automatiquement. **Il est
configuré en version gratuite** (voir §9 pour passer en production).

1. Sur Render : **New +** → **Blueprint**.
2. Connecter GitHub si besoin, puis sélectionner le dépôt `koyra`.
3. Render lit `render.yaml` et propose de créer :
   - le service web **koyra** (plan *free*)
   - la base **koyra-db** (PostgreSQL, plan *free*)
4. Render demande les variables marquées `sync: false` (le bloc e-mail Gmail).
   Les remplir maintenant (§4) ou laisser vide et compléter plus tard.
5. Cliquer **Apply**. Le premier déploiement démarre (~3-5 min) : `build.sh`
   installe les dépendances et lance `collectstatic` ; les migrations de la
   base tournent au démarrage du service (`startCommand`), pas pendant le
   build (la base n'y est pas joignable sur Render).

`SECRET_KEY` et `DATABASE_URL` sont générés automatiquement, rien à saisir.

### Limites de la version gratuite

- le site **s'endort après 15 min** sans visite (réveil ~50 s à la visite suivante)
- la base gratuite est **supprimée au bout de 30 jours**
- **pas de disque persistant** : les images uploadées dans l'admin disparaissent
  à chaque redéploiement

C'est fait pour **valider le rendu en ligne**, pas pour un site livré définitivement.

---

## 4. Renseigner les variables e-mail

Dans le dashboard Render → service **koyra** → onglet **Environment**, compléter
les variables laissées vides (`sync: false`) :

| Variable | Exemple |
|---|---|
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_HOST_USER` | `contact@koyradistribution.com` |
| `EMAIL_HOST_PASSWORD` | *(mot de passe d'application SMTP)* |
| `DEFAULT_FROM_EMAIL` | `Koyra Distribution <contact@koyradistribution.com>` |
| `CONTACT_NOTIFICATION_EMAIL` | `contact@koyradistribution.com` |

`EMAIL_BACKEND`, `EMAIL_PORT` (587) et `EMAIL_USE_TLS` (true) sont déjà réglés.
Enregistrer → Render redéploie.

> **Gmail** : activer la validation en 2 étapes puis créer un
> « mot de passe d'application » (Google Account → Sécurité). Le mot de passe
> habituel ne fonctionne pas en SMTP.

---

## 5. Créer le premier compte administrateur

Via une page d'installation à usage unique (pas besoin du Shell).

1. Render → service **koyra** → onglet **Environment** → définir
   `ADMIN_SETUP_TOKEN` avec une valeur **URL-safe** (lettres + chiffres,
   ~40 caractères) — ex. `python -c "import secrets;print(secrets.token_hex(24))"`.
   Éviter `generateValue` : le base64 de Render contient `/ + =` et casse l'URL.
2. Ouvrir `https://koyra.onrender.com/installation/<jeton>/`.
3. Choisir un identifiant + un mot de passe → le compte est créé et la
   session ouverte, redirection vers `/admin/`.

Cette page ne répond **que** tant qu'aucun administrateur n'existe **et** que
le jeton est bon ; sinon elle renvoie une erreur 404. Une fois le premier
compte créé, elle est donc automatiquement hors service.

> Repli possible via le Shell : `python manage.py createsuperuser`.

Ensuite, les comptes suivants se créent depuis l'admin :
**Utilisateurs → Ajouter** (cocher « Statut équipe » + permissions *catalogue*).

---

## 6. Images produits — Cloudinary (obligatoire sur l'offre gratuite)

Le disque de Render (offre gratuite) est **éphémère** : les images
téléversées disparaissent au redéploiement et à la mise en veille. On les
stocke donc sur **Cloudinary** (offre gratuite : 25 Go, CDN).

1. Créer un compte sur https://cloudinary.com (gratuit).
2. Dashboard Cloudinary → **API Keys** → copier l'**API Environment variable**,
   de la forme `CLOUDINARY_URL=cloudinary://123...:abc...@mon-cloud`.
3. Render → service **koyra** → **Environment** → ajouter `CLOUDINARY_URL`
   avec cette valeur (sans le `CLOUDINARY_URL=` devant). Save → redéploie.
4. Dans l'admin, **re-téléverser** les images des produits déjà créés
   (les anciennes, stockées sur le disque éphémère, sont perdues).

Ensuite, tout `ImageField` est envoyé sur Cloudinary automatiquement et
servi via son CDN. Sans `CLOUDINARY_URL`, le site sert `/media/` localement
(utile en dev, ou sur un plan payant avec disque).

---

## 7. Nom de domaine (optionnel)

Service **koyra** → **Settings** → **Custom Domains** → ajouter
`www.koyradistribution.com`. Render affiche les enregistrements DNS
(un `CNAME`) à créer chez le registrar. Le certificat HTTPS est émis
automatiquement.

Après ajout, mettre à jour la variable `ALLOWED_HOSTS` :

```
ALLOWED_HOSTS=.onrender.com,www.koyradistribution.com,koyradistribution.com
```

---

## 8. Mises à jour

Chaque `git push` sur `main` redéclenche un déploiement (build + migrations).

---

## 9. Passer en production (formules payantes)

À faire le jour du lancement officiel, dans `render.yaml` :

1. **Base** : `plan: free` → `plan: basic-256mb`.
2. **Web** : `plan: free` → `plan: starter`.
3. **Disque images** : décommenter le bloc `disk:` (name `koyra-media`,
   mountPath `/var/media`, sizeGB `1`).
4. **Media** : ajouter la variable d'env `MEDIA_ROOT = /var/media`.
5. `git commit` + `git push` → Render applique les changements.

> ⚠️ Sur le plan gratuit, les images déjà uploadées auront été perdues :
> il faudra les re-téléverser après le passage en payant.

Total après passage : **~14 $/mois** (7 web + 7 base + ~0,25 disque).

---

## Variables d'environnement (référence)

Voir `.env.example`. Les principales en production :

| Variable | Rôle | Valeur prod |
|---|---|---|
| `DEBUG` | mode debug | `false` |
| `SECRET_KEY` | clé de signature | *(généré par Render)* |
| `ALLOWED_HOSTS` | domaines autorisés | `.onrender.com,...` |
| `DATABASE_URL` | connexion PostgreSQL | *(généré par Render)* |
| `DB_SSL_REQUIRE` | SSL vers la base | `true` |
| `CLOUDINARY_URL` | stockage des images | `cloudinary://…` (voir §6) |
| `MEDIA_ROOT` | dossier des images (si disque payant) | `/var/media` |
| `SECURE_SSL_REDIRECT` | forcer HTTPS | `true` |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `CONTACT_NOTIFICATION_EMAIL` | envoi des e-mails | *(voir §4)* |
| `ADMIN_SETUP_TOKEN` | page de création du 1er admin | *(voir §5)* |

---

## Développement local

```bash
cp .env.example .env      # puis renseigner DB_PASSWORD
python manage.py migrate
python manage.py runserver
```

En local, `DEBUG=true` par défaut : base PostgreSQL locale, e-mails affichés
dans la console (aucun envoi réel).

---

## Coût indicatif Render

| Ressource | Test (gratuit) | Production |
|---|---|---|
| Service web | free — s'endort après 15 min | Starter ~7 $/mois |
| PostgreSQL | free — effacé après 30 j | Basic 256 Mo ~7 $/mois |
| Disque média 1 Go | *(indisponible en gratuit)* | inclus ~0,25 $/mois |
| **Total** | **0 $** | **~14 $/mois** |

`render.yaml` est livré en version **gratuite**. Voir §9 pour basculer en
production.
