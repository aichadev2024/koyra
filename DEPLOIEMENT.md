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

Le fichier `render.yaml` à la racine décrit tout automatiquement.

1. Sur Render : **New +** → **Blueprint**.
2. Sélectionner le dépôt `koyra`.
3. Render lit `render.yaml` et propose de créer :
   - le service web **koyra**
   - la base **koyra-db** (PostgreSQL)
   - le disque **koyra-media** (1 Go, pour les images)
4. Cliquer **Apply**. Le premier déploiement démarre (`build.sh` installe les
   dépendances, lance `collectstatic` puis `migrate`).

`SECRET_KEY` et `DATABASE_URL` sont générés automatiquement.

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

## 5. Créer le compte administrateur

Dashboard Render → service **koyra** → onglet **Shell** :

```bash
python manage.py createsuperuser
```

Puis se connecter sur `https://koyra.onrender.com/admin/`.

---

## 6. Nom de domaine (optionnel)

Service **koyra** → **Settings** → **Custom Domains** → ajouter
`www.koyradistribution.com`. Render affiche les enregistrements DNS
(un `CNAME`) à créer chez le registrar. Le certificat HTTPS est émis
automatiquement.

Après ajout, mettre à jour la variable `ALLOWED_HOSTS` :

```
ALLOWED_HOSTS=.onrender.com,www.koyradistribution.com,koyradistribution.com
```

---

## 7. Mises à jour

Chaque `git push` sur `main` redéclenche un déploiement (build + migrations).

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
| `MEDIA_ROOT` | dossier des images | `/var/media` |
| `SECURE_SSL_REDIRECT` | forcer HTTPS | `true` |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `CONTACT_NOTIFICATION_EMAIL` | envoi des e-mails | *(voir §4)* |

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

| Ressource | Plan | Prix |
|---|---|---|
| Service web | Starter | ~7 $/mois |
| PostgreSQL | Basic 256 Mo | ~7 $/mois |
| Disque média 1 Go | inclus | ~0,25 $/mois |

Des plans **gratuits** existent pour tester, mais : le web s'endort après
15 min d'inactivité (réveil lent) et la base gratuite est supprimée au bout
de 30 jours. À éviter pour un site livré à un client.
