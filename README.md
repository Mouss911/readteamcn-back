RedTeamCN – Design System Platform
Une plateforme moderne de Design System permettant de créer, partager, évaluer et gérer des composants UI réutilisables.

Fonctionnalités

Authentification complète (JWT)
Création, modification, suppression de composants
Système de reviews (notes + commentaires)
Mot de passe oublié (reset par email)
Gestion des utilisateurs (superuser only)
API REST complète + Swagger
Prêt pour le frontend (React, Vue, etc.)


Apps Django



App
Description
Modèles
Endpoints clés



users
Gestion des utilisateurs, authentification, profils
User (custom)
/auth/register/, /auth/login/, /auth/logout/, /auth/me/, /users/ (admin), /auth/password/reset/


catalog
Gestion des composants UI
Component
/components/, /components/create/, /components/<id>/


reviews
Système de notation et commentaires
Review
/components/<id>/reviews/, /reviews/<id>/


tokens
(Réservé) Gestion avancée des tokens
—
—


notifications
(À venir) Notifications en temps réel
—
—


kpi
(À venir) Statistiques et métriques
—
—


audit
(À venir) Journal d'activité
—
—


dashboards
(À venir) Tableaux de bord
—
—


plugins
(À venir) Extensions tierces
—
—



Détail des Apps
users – Authentification & Profils

Modèle : User (hérite de AbstractUser)
Champs : email, username, first_name, last_name, organization_name, is_superuser
Fonctionnalités :
Inscription (POST /auth/register/)
Connexion (POST /auth/login/)
Déconnexion (POST /auth/logout/)
Profil utilisateur (GET /auth/me/)
Liste utilisateurs (superuser only) (GET /users/)
Mot de passe oublié (POST /auth/password/reset/ + lien)




catalog – Composants UI

Modèle : Component
Champs : name, description, category, code, created_by, created_at, updated_at
Catégories : BUTTON, CARD, INPUT, MODAL, NAVBAR, TYPOGRAPHY, OTHER
Endpoints :
POST /components/create/ → Créer
GET /components/ → Lister
PUT /components/<id>/ → Modifier
DELETE /components/<id>/ → Supprimer




reviews – Avis & Notation

Modèle : Review
Champs : component, user, rating (1–5), comment, created_at, updated_at
Contraintes : 1 review par utilisateur/composant
Endpoints :
POST /components/<id>/reviews/ → Ajouter
GET /components/<id>/reviews/ → Lister
DELETE /reviews/<id>/ → Supprimer (seulement le sien)




API Documentation
Swagger UI : http://127.0.0.1:8000/schema/swagger-ui/

Configuration Email (Tests)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

Les emails de reset de mot de passe s’affichent dans la console.

Lancer le projet
# 1. Cloner
git clone <repo>
cd redteamcn

# 2. Environnement
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Installer
pip install -r requirements.txt

# 4. Migrer
python manage.py migrate

# 5. Créer superuser
python manage.py createsuperuser

# 6. Lancer
python manage.py runserver


Test avec Postman

POST /api/auth/login/ → Récupérer access token
Ajouter dans les headers :Authorization: Bearer <token>



RedTeamCN – Le Design System qui unifie vos équipes.