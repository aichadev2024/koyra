# Intégration Firebase Storage

Où vont les images et documents téléversés dans l'admin, et comment le code
décide du stockage.

> Version illustrée (schémas, dépannage) :
> https://claude.ai/code/artifact/217a0de9-a747-43bc-b4c8-231c1cbd2d35

| | |
|---|---|
| Fournisseur | Firebase Storage (= bucket Google Cloud Storage) |
| Offre | Spark gratuite — ~5 Go stockés, ~1 Go/jour téléchargé |
| Backend Django | `storages.backends.gcloud.GoogleCloudStorage` |
| Emplacement | bucket, sous le préfixe `media/` |
| URL servie | URL signée V4, valable 24 h, régénérée à chaque rendu |
| Dév. local | inchangé — disque `koyra/media/` servi par Django |

## 1. Pourquoi

Le disque de Render (offre gratuite) est **éphémère** : les fichiers
téléversés disparaissent au redéploiement / à la mise en veille. Cloudinary
bloque les inscriptions depuis le Mali. Firebase = bucket GCS, global,
gratuit jusqu'à 5 Go, accepte images **et** documents.

## 2. La chaîne de stockage (`koyra_web/settings.py`)

Le stockage par défaut est choisi selon les variables d'environnement
présentes, dans cet ordre :

```
GS_BUCKET_NAME défini ?      -> Firebase Storage
sinon S3_ENDPOINT_URL ?      -> S3 / compatible S3 (B2, R2, Supabase…)
sinon CLOUDINARY_URL ?       -> Cloudinary
sinon                        -> disque local (MEDIA_ROOT)
```

`koyra_web/urls.py` ne sert `/media/` depuis le disque **que si** aucun
stockage externe n'est configuré.

## 3. Fonctionnement

**Téléversement :** `ImageField.save()` → `GoogleCloudStorage` → envoi vers
`gs://<bucket>/media/…` avec la clé de compte de service. Le chemin relatif
est stocké en base ; le préfixe `media/` vient de `GS_LOCATION`.

**Affichage :** `{{ obj.image.url }}` → URL signée V4
`https://storage.googleapis.com/<bucket>/media/…?X-Goog-Signature=…`
valable 24 h. Le navigateur charge le fichier directement chez Google.
Chaque rendu de page régénère l'URL → jamais d'image cassée par expiration.

**Pourquoi des URLs signées :** le bucket reste privé, aucun réglage IAM /
règles Storage à faire. Ne pas mettre ces URLs en cache ailleurs (e-mail,
flux) : elles expirent au bout de 24 h.

## 4. Réglages de la branche Firebase

```python
if GS_BUCKET_NAME:
    _raw = os.getenv('GS_CREDENTIALS_JSON', '')
    try:
        _info = json.loads(_raw)                       # JSON brut
    except json.JSONDecodeError:
        _info = json.loads(base64.b64decode(_raw))     # ou base64

    INSTALLED_APPS += ['storages']
    STORAGES['default'] = {'BACKEND': 'storages.backends.gcloud.GoogleCloudStorage'}
    GS_CREDENTIALS      = service_account.Credentials.from_service_account_info(_info)
    GS_PROJECT_ID       = _info.get('project_id')
    GS_DEFAULT_ACL      = None
    GS_QUERYSTRING_AUTH = True            # -> URLs signées
    GS_EXPIRATION       = timedelta(hours=24)
    GS_FILE_OVERWRITE   = False
    GS_LOCATION         = 'media'
```

## 5. Variables d'environnement

| Variable | Contenu | Source |
|---|---|---|
| `GS_BUCKET_NAME` | `koyra-xxxxx.firebasestorage.app` (ou `…appspot.com`) | Console Firebase → Storage |
| `GS_CREDENTIALS_JSON` | tout le contenu du `.json` de compte de service (brut **ou** base64) | ⚙ Paramètres du projet → Comptes de service → Générer une clé privée |

En prod : onglet **Environment** du service `koyra` sur Render.
En local : fichier `.env` (voir `.env.example`).

## 6. Mise en place

1. Console Firebase → **Storage → Commencer** → emplacement → mode production.
   Noter le nom du bucket.
2. Ne rien changer aux **règles Storage** (bucket privé, URLs signées).
3. ⚙ Paramètres → **Comptes de service** → **Générer une nouvelle clé privée**
   → fichier `.json`.
4. Render → service `koyra` → **Environment** → ajouter `GS_BUCKET_NAME` +
   `GS_CREDENTIALS_JSON` → Save (redéploie ~4-5 min).
5. Dans l'admin, **re-téléverser** les images des fiches créées avant Firebase.

**Vérifier :** sur une fiche en ligne, le `src` de l'`<img>` doit être
`storage.googleapis.com/<bucket>/media/…?X-Goog-Signature=…`.

## 7. Fichiers concernés

| Fichier | Changement |
|---|---|
| `koyra_web/settings.py` | chaîne de stockage + branche Firebase |
| `koyra_web/urls.py` | `/media/` local seulement sans stockage externe |
| `requirements.txt` | `django-storages`, `google-cloud-storage`, `google-auth` (+ deps) |
| `render.yaml` | `GS_BUCKET_NAME` + `GS_CREDENTIALS_JSON` (`sync: false`) |
| `.env.example` | modèle des variables |
| `DEPLOIEMENT.md` | §6 guide pas-à-pas |

Commits : `a6f1e71` (Firebase + URLs signées), `23b5f56` (socle S3).

## 8. Dépannage

| Symptôme | Cause | Correctif |
|---|---|---|
| OK en local, cassé en ligne | variables absentes sur Render | vérifier `GS_*` dans Environment, redéployer |
| `ValueError: Could not deserialize key` au boot | JSON tronqué / mal collé | recoller tout le `.json`, ou version base64 |
| Envoi image → `403 Forbidden` | compte de service sans accès Storage | utiliser la clé **générée par Firebase** |
| Envoi → `404` bucket introuvable | `GS_BUCKET_NAME` erroné | copier le nom exact affiché dans Storage |
| `<img>` pointe vers `/media/…` pas Google | branche Firebase non prise | `GS_BUCKET_NAME` vide — vérifier l'orthographe |
| Images qui marchaient → `403` | quota journalier de téléchargement atteint | attendre le reset, ou passer en Blaze |
| Build Render échoue | libs Google manquantes | vérifier `google-cloud-storage` dans `requirements.txt` |

## 9. Migrer plus tard

- **Disque Render payant :** décommenter `disk:` dans `render.yaml`, définir
  `MEDIA_ROOT=/var/media`, retirer les `GS_*`, re-téléverser.
- **Autre fournisseur S3 :** renseigner `S3_ENDPOINT_URL` + `S3_ACCESS_KEY_ID`
  + `S3_SECRET_ACCESS_KEY` + `S3_BUCKET_NAME` + `S3_REGION`, retirer
  `GS_BUCKET_NAME`.
- **Exporter depuis Firebase :** `gsutil -m cp -r gs://<bucket>/media ./media`.
