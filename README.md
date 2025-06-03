# Personnalisation du Panneau d'Administration Django : Thèmes, Sécurité et Améliorations UI

Ce projet vise à améliorer et personnaliser le panneau d'administration par défaut de Django en introduisant des fonctionnalités de gestion de thèmes, d'analyse d'accessibilité basée sur l'IA, et une API robuste pour l'interaction.

## Fonctionnalités Implémentées

* **Gestion des Thèmes (AdminTheme Model) :**
    * Modèle `AdminTheme` pour définir et stocker les configurations de thèmes (nom, URLs CSS/JS, statut actif).
    * Validation des URLs CSS/JS pour s'assurer qu'elles se terminent par les extensions correctes.
* **API RESTful pour la Gestion des Thèmes :**
    * Endpoints pour lister, créer, récupérer, mettre à jour et supprimer des thèmes.
    * Endpoint dédié pour activer un thème spécifique (`is_active=True`), désactivant automatiquement les autres.
    * Endpoint d'upload de thèmes (`/api/themes/upload/`) pour téléverser des fichiers CSS/JS et les associer à un thème existant ou nouveau, avec gestion de l'écrasement.
* **API GraphQL pour la Gestion des Thèmes :**
    * Types GraphQL pour exposer les données des thèmes.
    * Mutation `switchAdminSkin` pour changer le thème actif via GraphQL.
* **Sécurité Robuste :**
    * Accès aux APIs REST et mutations GraphQL restreint aux superutilisateurs uniquement.
    * Protection CSRF intégrée pour les endpoints REST (fournie par Django).
* **Intégration Celery pour les Tâches d'Arrière-Plan :**
    * Tâche Celery `analyze_ui_suggestions` pour analyser les fichiers CSS des thèmes et générer des suggestions d'accessibilité (contraste des couleurs, dépendance à la couleur seule).
* **Rapport d'Accessibilité :**
    * Génération d'un rapport textuel d'accessibilité pour chaque thème, stocké dans le champ `accessibility_report`, facilitant la lecture des problèmes détectés.

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre système :

* **Python 3.x** (version 3.9 ou supérieure recommandée pour une meilleure compatibilité avec les librairies)
* **pip** (gestionnaire de paquets Python)
* **Redis** (serveur de base de données en mémoire, utilisé comme broker pour Celery)
    * Pour Windows, vous pouvez utiliser le port non officiel : [https://github.com/microsoftarchive/redis/releases](https://github.com/microsoftarchive/redis/releases)
    * Pour Linux/macOS, installez via votre gestionnaire de paquets (ex: `sudo apt-get install redis-server` ou `brew install redis`).

## Installation

Suivez ces étapes pour installer et exécuter l'application :

1.  **Clonez le dépôt :**
    ```bash
    git clone [https://github.com/BerrimaFedi/admin-ui.git](https://github.com/BerrimaFedi/admin-ui.git)
    cd admin-ui # Accédez au répertoire racine du projet
    ```

2.  **Créez et activez un environnement virtuel (recommandé) :**
    ```bash
    python -m venv venv
    # Sur Windows
    .\venv\Scripts\activate
    # Sur Linux/macOS
    source venv/bin/activate
    ```

3.  **Installez les dépendances Python :**
    Créez un fichier `requirements.txt` à la racine de votre projet (voir la section "Générer `requirements.txt`" ci-dessous) puis installez :
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurez la base de données :**
    Appliquez les migrations Django pour créer les tables de la base de données :
    ```bash
    python manage.py migrate
    ```

5.  **Créez un superutilisateur Django :**
    Ceci est nécessaire pour accéder au panneau d'administration et aux APIs sécurisées :
    ```bash
    python manage.py createsuperuser
    ```
    Suivez les invites pour créer votre utilisateur.

6.  **Démarrez le serveur de développement Django :**
    ```bash
    python manage.py runserver
    ```
    Le serveur sera accessible à `http://127.0.0.1:8000/`.

7.  **Démarrez le serveur Redis :**
    Assurez-vous que votre serveur Redis est en cours d'exécution. La commande dépend de votre installation (souvent `redis-server` sur Linux/macOS).

8.  **Démarrez le worker Celery :**
    Dans un **nouveau terminal** (séparé du serveur Django) et après avoir activé votre environnement virtuel :
    ```bash
    celery -A admin_personalization worker -l info -P solo
    ```
 

## Utilisation

1.  **Accédez au panneau d'administration Django :**
    Ouvrez votre navigateur et allez à `http://127.0.0.1:8000/admin/`. Connectez-vous avec le superutilisateur que vous avez créé.

2.  **Gérez les Thèmes :**
    * Dans le panneau d'administration, vous trouverez la section `Admin Theme Manager` et le modèle `AdminTheme`.
    * Vous pouvez créer et modifier des thèmes ici.
    * Lorsque vous sauvegardez un `AdminTheme`, la tâche Celery `analyze_ui_suggestions` sera déclenchée en arrière-plan pour mettre à jour les champs `ui_suggestions` (JSON brut) et `accessibility_report` (rapport textuel lisible).



3.  **Utilisation de l'API REST pour Appliquer un Thème :**
    **Endpoint :** `http://127.0.0.1:8000/api/themes/<id_du_theme>/apply/`
    **Méthode :** `PATCH`
    **Headers :** `Authorization` et `X-CSRFToken` comme ci-dessus.
    **Corps de la requête :** Aucun corps nécessaire, le `PATCH` est géré par la vue.

4.  **Utilisation de GraphQL pour Basculer les Skins Admin :**
    Accédez à l'interface GraphQL (souvent `http://127.0.0.1:8000/graphql/` si configuré).
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
    Assurez-vous d'être authentifié en tant que superutilisateur pour exécuter cette mutation.

## Exigences (Requirements)

Les principales dépendances Python sont listées dans le `requirements.txt` ci-dessous.
