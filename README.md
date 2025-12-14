# 💰 Application de Visualisation de Finances Personnelles

Une application Streamlit intuitive et évolutive pour visualiser et analyser vos finances personnelles mensuelles.

## 📋 Table des matières

- [Caractéristiques](#caractéristiques)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure des données](#structure-des-données)
- [Choix techniques](#choix-techniques)
- [Évolutions futures](#évolutions-futures)

## ✨ Caractéristiques

- **Visualisation mensuelle** : Sélectionnez un mois et visualisez instantanément vos finances
- **Métriques clés** :
  - Total des entrées (revenus)
  - Total des sorties (dépenses)
  - Total de l'épargne
  - Taux d'épargne (pourcentage)
  - Solde mensuel
- **Graphiques interactifs** :
  - Répartition des sorties par catégorie (camembert)
  - Répartition de l'épargne par type (camembert)
  - Vue détaillée des sorties (barres horizontales)
- **Tableaux détaillés** : Consultez le détail de chaque catégorie
- **Architecture modulaire** : Code propre et facilement extensible

## 📁 Structure du projet

```
Finary_wish/
├── app.py                      # Application Streamlit principale
├── generate_sample_data.py     # Script de génération de données fictives
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation
└── finances_data.xlsx          # Fichier de données (généré)
```

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone <votre-repo>
cd Finary_wish
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Générer les données fictives

```bash
python generate_sample_data.py
```

Cela créera un fichier `finances_data.xlsx` avec 12 mois de données réalistes.

### 5. Lancer l'application

```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur à l'adresse `http://localhost:8501`.

## 📊 Structure des données

### Format du fichier Excel

Le fichier `finances_data.xlsx` suit cette structure :

| Catégorie | Type | 2024-01 | 2024-02 | 2024-03 | ... |
|-----------|------|---------|---------|---------|-----|
| Salaire | Entrée | 2800.00 | 2795.50 | 2810.20 | ... |
| Loyer | Sortie | 950.00 | 950.00 | 950.00 | ... |
| Livret A | Épargne | 300.00 | 315.50 | 290.00 | ... |

### Colonnes obligatoires

1. **Catégorie** : Nom de la catégorie financière (ex: Salaire, Loyer, Livret A)
2. **Type** : Type de transaction
   - `Entrée` : Revenus (salaire, rente, bonus, etc.)
   - `Sortie` : Dépenses (loyer, nourriture, loisirs, etc.)
   - `Épargne` : Montants épargnés (livrets, PEA, etc.)
3. **Colonnes mensuelles** : Format `YYYY-MM` (ex: 2024-01, 2024-02)

### Catégories par défaut

**Entrées :**
- Salaire
- Rente
- Bonus

**Sorties :**
- Loyer
- Nourriture
- Transports
- Abonnements
- Loisirs
- Santé
- Vêtements
- Énergie
- Assurances
- Téléphone/Internet
- Impôts

**Épargne :**
- Livret A
- Compte Épargne
- PEA (Plan d'Épargne en Actions)

### Ajouter de nouvelles catégories

Pour ajouter une catégorie, il suffit d'ajouter une ligne dans le fichier Excel avec :
- Le nom de la catégorie
- Son type (Entrée/Sortie/Épargne)
- Les montants pour chaque mois

**Aucune modification de code n'est nécessaire** - l'application détecte automatiquement les nouvelles catégories.

## 🔧 Choix techniques

### 1. **Streamlit**

**Pourquoi Streamlit ?**
- Création rapide d'interfaces web interactives
- Syntaxe Python pure (pas de HTML/CSS/JavaScript)
- Rechargement automatique lors des modifications
- Parfait pour les prototypes et applications de data science

### 2. **Pandas**

**Pourquoi Pandas ?**
- Standard de l'industrie pour la manipulation de données tabulaires
- Lecture/écriture Excel native
- Opérations de filtrage et agrégation puissantes
- Excellent pour les données financières

### 3. **Plotly**

**Pourquoi Plotly ?**
- Graphiques interactifs (zoom, survol, sélection)
- Rendu natif dans Streamlit
- Large gamme de types de graphiques
- Personnalisation avancée possible

### 4. **OpenPyXL**

**Pourquoi OpenPyXL ?**
- Support complet des fichiers Excel (.xlsx)
- Lecture et écriture de fichiers Excel modernes
- Pas de dépendance à Microsoft Office

### 5. **Architecture modulaire**

Le code est organisé en fonctions bien définies :

```python
# Chargement des données
load_data()          # Charge le fichier Excel
get_available_months() # Extrait les mois disponibles
get_month_data()     # Calcule les totaux pour un mois

# Visualisation
display_metrics()    # Affiche les métriques clés
plot_pie_chart()     # Crée un graphique circulaire
plot_bar_chart()     # Crée un graphique en barres
display_detailed_tables() # Affiche les tableaux détaillés
```

**Avantages :**
- Code facile à tester et déboguer
- Fonctions réutilisables
- Évolutions futures facilitées
- Maintenance simplifiée

### 6. **Cache Streamlit**

L'utilisation de `@st.cache_data` sur `load_data()` permet de :
- Éviter de recharger le fichier Excel à chaque interaction
- Améliorer les performances
- Réduire la consommation de ressources

## 🎯 Évolutions futures possibles

### Analyses avancées

1. **Comparaisons inter-mois**
   - Graphique d'évolution temporelle
   - Tendances des dépenses par catégorie
   - Moyenne glissante sur 3/6/12 mois

2. **Projections**
   - Prévisions basées sur les tendances historiques
   - Objectifs d'épargne
   - Alertes de budget

3. **Analyses approfondies**
   - Identification des pics de dépenses
   - Corrélations entre catégories
   - Saisonnalité des dépenses

### Fonctionnalités supplémentaires

1. **Upload de fichier**
   - Permettre à l'utilisateur de télécharger son propre fichier Excel
   - Validation automatique du format

2. **Export de rapports**
   - Génération de PDF mensuels
   - Export des graphiques en images
   - Résumé annuel automatique

3. **Budgets et objectifs**
   - Définir des budgets par catégorie
   - Alertes en cas de dépassement
   - Suivi des objectifs d'épargne

4. **Multi-devises**
   - Support de plusieurs devises
   - Conversion automatique

5. **Authentification**
   - Gestion multi-utilisateurs
   - Données personnelles sécurisées

### Améliorations techniques

1. **Base de données**
   - Remplacer Excel par SQLite ou PostgreSQL
   - Meilleures performances sur gros volumes

2. **Tests automatisés**
   - Tests unitaires avec pytest
   - Tests d'intégration

3. **CI/CD**
   - Déploiement automatique
   - Tests automatiques avant déploiement

4. **Containerisation**
   - Docker pour faciliter le déploiement
   - Docker Compose pour l'environnement complet

## 📝 Notes importantes

### Données fictives

Les données générées par `generate_sample_data.py` sont **purement fictives** et servent de template. Elles incluent :
- Des variations réalistes (±10% à ±50% selon les catégories)
- Des valeurs fixes pour loyer/assurances
- 12 mois de données pour tester toutes les fonctionnalités

### Personnalisation

Pour utiliser vos vraies données :
1. Ouvrez `finances_data.xlsx` dans Excel
2. Modifiez les valeurs selon vos finances réelles
3. Ajoutez/supprimez des catégories si nécessaire
4. Sauvegardez le fichier
5. Rechargez l'application Streamlit

### Performance

L'application est optimisée pour :
- Fichiers Excel de taille raisonnable (< 1000 lignes)
- Plusieurs années de données
- Mise en cache des données pour réactivité maximale

## 🤝 Contribution

Ce projet est conçu pour être facilement extensible. N'hésitez pas à :
- Ajouter de nouvelles visualisations
- Proposer de nouvelles fonctionnalités
- Améliorer l'interface utilisateur
- Optimiser les performances

## 📄 Licence

Ce projet est fourni tel quel pour usage personnel.

## 🆘 Support

Pour toute question ou problème :
1. Vérifiez que toutes les dépendances sont installées
2. Vérifiez que le fichier `finances_data.xlsx` existe
3. Consultez les logs dans le terminal Streamlit
4. Vérifiez la structure du fichier Excel

---

**Développé avec ❤️ et Python**
