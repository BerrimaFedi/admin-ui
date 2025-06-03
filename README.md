# Personnalisation du Panneau d'Administration Django : Thèmes, Sécurité et Améliorations UI

Ce projet vise à améliorer et personnaliser le panneau d'administration par défaut de Django en introduisant des fonctionnalités de gestion de thèmes, d'analyse d'accessibilité basée sur l'IA, et une API robuste pour l'interaction.

***

## Fonctionnalités Implémentées

### Gestion des Thèmes (AdminTheme Model)
- Modèle `AdminTheme` pour définir et stocker les configurations de thèmes (nom, URLs CSS/JS, statut actif).
- Validation des URLs CSS/JS pour s'assurer qu'elles se terminent par les extensions correctes.

### API RESTful pour la Gestion des Thèmes
- Endpoints pour lister, créer, récupérer, mettre à jour et supprimer des thèmes.
- Endpoint dédié pour activer un thème spécifique (`is_active=True`), désactivant automatiquement les autres.
- Endpoint d'upload de thèmes (`/api/themes/upload/`) pour téléverser des fichiers CSS/JS et les associer à un thème existant ou nouveau, avec gestion de l'écrasement.

### API GraphQL pour la Gestion des Thèmes
- Types GraphQL pour exposer les données des thèmes.
- Mutation `switchAdminSkin` pour changer le thème actif via GraphQL.

### Sécurité Robuste
- Accès aux APIs REST et mutations GraphQL restreint aux superutilisateurs uniquement.
- Protection CSRF intégrée pour les endpoints REST (fournie par Django).
- Authentification par jeton (Token Authentication) pour les clients API.
- Configuration CORS (Cross-Origin Resource Sharing) pour autoriser les requêtes depuis des origines spécifiques.

### Intégration Celery pour les Tâches d'Arrière-Plan
- Tâche Celery `analyze_ui_suggestions` pour analyser les fichiers CSS des thèmes et générer des suggestions d'accessibilité (contraste des couleurs, dépendance à la couleur seule).
- Tâches `compile_scss` et `deploy_static_assets` prêtes pour l'automatisation (le scheduling via celerybeat est possible mais non configuré par défaut).

### Rapport d'Accessibilité
- Génération d'un rapport textuel d'accessibilité pour chaque thème, stocké dans le champ `accessibility_report`, facilitant la lecture des problèmes détectés.

***

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre système :

- Python 3.x (version 3.9 ou supérieure recommandée pour une meilleure compatibilité avec les librairies)
- pip (gestionnaire de paquets Python)
- Redis (serveur de base de données en mémoire, utilisé comme broker pour Celery)
  - Pour Windows, vous pouvez utiliser le port non officiel : https://github.com/microsoftarchive/redis/releases
  - Pour Linux/macOS, installez via votre gestionnaire de paquets (ex: `sudo apt-get install redis-server` ou `brew install redis`).

***

## Installation

Suivez ces étapes pour installer et exécuter l'application :

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/BerrimaFedi/admin-ui.git
   cd admin-ui # Accédez au répertoire racine du projet
   ```

2. Créez et activez un environnement virtuel (recommandé) :
   ```bash
   # Sur Windows
   python -m venv venv
   .\venv\Scripts\activate
   # Sur Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installez les dépendances Python :
   Créez un fichier `requirements.txt` à la racine de votre projet (voir la section "Générer requirements.txt" ci-dessous) puis installez :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez la base de données :
   Appliquez les migrations Django pour créer les tables de la base de données :
   ```bash
   python manage.py migrate
   ```

5. Créez un superutilisateur Django :
   Ceci est nécessaire pour accéder au panneau d'administration et aux APIs sécurisées :
   ```bash
   python manage.py createsuperuser
   ```
   Suivez les invites pour créer votre utilisateur.

6. Démarrez le serveur de développement Django :
   ```bash
   python manage.py runserver
   ```
   Le serveur sera accessible à http://127.0.0.1:8000/.

7. Démarrez le serveur Redis :
   Assurez-vous que votre serveur Redis est en cours d'exécution. La commande dépend de votre installation (souvent `redis-server` sur Linux/macOS).

8. Démarrez le worker Celery :
   Dans un nouveau terminal (séparé du serveur Django) et après avoir activé votre environnement virtuel :
   ```bash
   celery -A admin_personalization worker -l info -P solo
   ```

***

## Utilisation

### Accédez au panneau d'administration Django
Ouvrez votre navigateur et allez à http://127.0.0.1:8000/admin/. Connectez-vous avec le superutilisateur que vous avez créé.

### Gérez les Thèmes
Dans le panneau d'administration, vous trouverez la section Admin Theme Manager et le modèle AdminTheme. Vous pouvez créer et modifier des thèmes ici. Lorsque vous sauvegardez un `AdminTheme`, la tâche Celery `analyze_ui_suggestions` sera déclenchée en arrière-plan pour mettre à jour les champs `ui_suggestions` (JSON brut) et `accessibility_report` (rapport textuel lisible).

### Authentification par Jeton (Token Authentication)
Pour interagir avec les APIs REST et GraphQL via des clients non-navigateur (comme Postman, curl, ou un frontend séparé), vous aurez besoin d'un jeton d'authentification.

### Générer un jeton pour un superutilisateur
Dans votre terminal, activez votre environnement virtuel et entrez dans le shell Django :
```bash
python manage.py shell
```
Dans le shell Python, exécutez les commandes suivantes (remplacez 'admin' par le nom d'utilisateur de votre superutilisateur) :
```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
user = User.objects.get(username='admin')
token, created = Token.objects.get_or_create(user=user)
print(token.key) # Copiez cette clé de jeton
exit()
```

### Utiliser le jeton dans les requêtes API
Incluez le jeton dans l'en-tête Authorization de vos requêtes, au format `Token <votre_jeton>`. Exemple avec curl :
```bash
curl -X GET \
  http://127.0.0.1:8000/api/themes/ \
  -H 'Authorization: Token VOTRE_JETON_ICI'
```
Exemple avec Postman : Dans l'onglet Headers, ajoutez une clé `Authorization` avec la valeur `Token VOTRE_JETON_ICI`.

### Utilisation de l'API REST pour l'Upload de Thèmes
Vous pouvez utiliser des outils comme Postman ou curl pour téléverser des thèmes.

- **Endpoint** : http://127.0.0.1:8000/api/themes/upload/
- **Méthode** : POST
- **Headers** :
  - `Authorization: Token VOTRE_JETON_ICI`
  - (Le `Content-Type: multipart/form-data` sera automatiquement défini par votre client si vous utilisez `form-data`).
- **Corps de la requête (form-data)** :
  - `name`: MonNouveauTheme
  - `css_file`: (sélectionnez votre fichier .css)
  - `js_file`: (optionnel, sélectionnez votre fichier .js)
  - `overwrite`: true (optionnel, pour écraser un thème existant par nom)

### Utilisation de l'API REST pour Appliquer un Thème
- **Endpoint** : http://127.0.0.1:8000/api/themes/<id_du_theme>/apply/
- **Méthode** : PATCH
- **Headers** : `Authorization: Token VOTRE_JETON_ICI`
- **Corps de la requête** : Aucun corps nécessaire, le PATCH est géré par la vue.

### Utilisation de GraphQL pour Basculer les Skins Admin
Accédez à l'interface GraphQL (souvent http://127.0.0.1:8000/graphql/ si configuré). Assurez-vous d'être authentifié (soit via la session du navigateur en tant que superutilisateur, soit en configurant l'en-tête `Authorization: Token VOTRE_JETON_ICI` dans votre client GraphQL ou Postman si vous l'utilisez pour GraphQL).

Exemple de mutation :
```graphql
mutation {
  switchAdminSkin(themeId: "1") { # Remplacez 1 par l'ID de votre thème
    id
    name
    isActive
  }
}
```

***

## Exigences (Requirements)

Les principales dépendances Python sont listées dans le `requirements.txt` ci-dessous.
