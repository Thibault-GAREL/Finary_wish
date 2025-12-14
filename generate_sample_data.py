"""
Script de génération de données financières fictives pour l'application Streamlit.

Ce script crée un fichier Excel avec des données réalistes sur plusieurs mois
pour tester l'application de visualisation de finances personnelles.

Structure du fichier Excel:
- Colonne 'Catégorie': nom de la catégorie financière
- Colonne 'Type': 'Entrée', 'Sortie', ou 'Épargne'
- Colonnes mensuelles: format 'YYYY-MM' (ex: 2024-01, 2024-02, etc.)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_monthly_columns(start_date: str, num_months: int) -> list:
    """
    Génère une liste de colonnes mensuelles au format YYYY-MM.

    Args:
        start_date: Date de début au format 'YYYY-MM'
        num_months: Nombre de mois à générer

    Returns:
        Liste des mois au format YYYY-MM
    """
    start = datetime.strptime(start_date, '%Y-%m')
    months = []

    for i in range(num_months):
        current_date = start + timedelta(days=30 * i)
        # Recalculer pour avoir le bon mois
        current_date = datetime(start.year, start.month, 1) + pd.DateOffset(months=i)
        months.append(current_date.strftime('%Y-%m'))

    return months


def add_variation(base_value: float, variation_percent: float = 0.1) -> float:
    """
    Ajoute une variation aléatoire à une valeur de base.

    Args:
        base_value: Valeur de base
        variation_percent: Pourcentage de variation (0.1 = ±10%)

    Returns:
        Valeur avec variation aléatoire
    """
    variation = base_value * variation_percent
    return base_value + np.random.uniform(-variation, variation)


def generate_finance_data(start_date: str = '2024-01', num_months: int = 12) -> pd.DataFrame:
    """
    Génère un DataFrame avec des données financières fictives.

    Args:
        start_date: Date de début au format 'YYYY-MM'
        num_months: Nombre de mois à générer

    Returns:
        DataFrame avec les données financières
    """

    # Générer les colonnes de mois
    months = generate_monthly_columns(start_date, num_months)

    # Définir les catégories avec leurs valeurs de base mensuelles
    categories_data = [
        # ENTRÉES
        {'Catégorie': 'Salaire', 'Type': 'Entrée', 'base': 2800, 'variation': 0.02},
        {'Catégorie': 'Rente', 'Type': 'Entrée', 'base': 450, 'variation': 0.05},
        {'Catégorie': 'Bonus', 'Type': 'Entrée', 'base': 200, 'variation': 0.5},

        # SORTIES
        {'Catégorie': 'Loyer', 'Type': 'Sortie', 'base': 950, 'variation': 0.0},
        {'Catégorie': 'Nourriture', 'Type': 'Sortie', 'base': 450, 'variation': 0.15},
        {'Catégorie': 'Transports', 'Type': 'Sortie', 'base': 120, 'variation': 0.2},
        {'Catégorie': 'Abonnements', 'Type': 'Sortie', 'base': 85, 'variation': 0.05},
        {'Catégorie': 'Loisirs', 'Type': 'Sortie', 'base': 180, 'variation': 0.3},
        {'Catégorie': 'Santé', 'Type': 'Sortie', 'base': 65, 'variation': 0.4},
        {'Catégorie': 'Vêtements', 'Type': 'Sortie', 'base': 90, 'variation': 0.35},
        {'Catégorie': 'Énergie', 'Type': 'Sortie', 'base': 110, 'variation': 0.15},
        {'Catégorie': 'Assurances', 'Type': 'Sortie', 'base': 95, 'variation': 0.0},
        {'Catégorie': 'Téléphone/Internet', 'Type': 'Sortie', 'base': 45, 'variation': 0.0},
        {'Catégorie': 'Impôts', 'Type': 'Sortie', 'base': 180, 'variation': 0.1},

        # ÉPARGNE
        {'Catégorie': 'Livret A', 'Type': 'Épargne', 'base': 300, 'variation': 0.15},
        {'Catégorie': 'Compte Épargne', 'Type': 'Épargne', 'base': 200, 'variation': 0.2},
        {'Catégorie': 'PEA ETF World', 'Type': 'Épargne', 'base': 150, 'variation': 0.25},
        {'Catégorie': 'CTO Actions', 'Type': 'Épargne', 'base': 100, 'variation': 0.3},

        # PATRIMOINE (valeurs accumulées)
        {'Catégorie': 'Résidence principale', 'Type': 'Patrimoine', 'base': 180000, 'variation': 0.02},
        {'Catégorie': 'Compte courant', 'Type': 'Patrimoine', 'base': 2500, 'variation': 0.3},
        {'Catégorie': 'Livret A (valorisation)', 'Type': 'Patrimoine', 'base': 15000, 'variation': 0.05},
        {'Catégorie': 'PEA (valorisation)', 'Type': 'Patrimoine', 'base': 12000, 'variation': 0.1},
        {'Catégorie': 'CTO (valorisation)', 'Type': 'Patrimoine', 'base': 8000, 'variation': 0.12},
        {'Catégorie': 'Assurance Vie Linxea', 'Type': 'Patrimoine', 'base': 25000, 'variation': 0.08},
        {'Catégorie': 'Véhicule', 'Type': 'Patrimoine', 'base': 15000, 'variation': 0.05},
    ]

    # Créer le DataFrame
    data = []

    for cat_info in categories_data:
        row = {
            'Catégorie': cat_info['Catégorie'],
            'Type': cat_info['Type']
        }

        # Générer les valeurs pour chaque mois avec variation
        for month in months:
            if cat_info['variation'] > 0:
                value = add_variation(cat_info['base'], cat_info['variation'])
            else:
                value = cat_info['base']

            # Arrondir à 2 décimales
            row[month] = round(value, 2)

        data.append(row)

    df = pd.DataFrame(data)

    return df


def save_to_excel(df: pd.DataFrame, filename: str = 'finances_data.xlsx'):
    """
    Sauvegarde le DataFrame dans un fichier Excel.

    Args:
        df: DataFrame à sauvegarder
        filename: Nom du fichier de sortie
    """
    df.to_excel(filename, index=False, engine='openpyxl')
    print(f"✓ Fichier '{filename}' créé avec succès!")
    print(f"  - {len(df)} catégories")
    print(f"  - {len([col for col in df.columns if col not in ['Catégorie', 'Type']])} mois de données")


def main():
    """Fonction principale pour générer et sauvegarder les données."""

    print("Génération des données financières fictives...")

    # Générer les données pour 12 mois à partir de janvier 2024
    df = generate_finance_data(start_date='2024-01', num_months=12)

    # Sauvegarder dans un fichier Excel
    save_to_excel(df, 'finances_data.xlsx')

    # Afficher un aperçu
    print("\nAperçu des données générées:")
    print(df.head(10))

    # Afficher quelques statistiques
    print("\n--- Résumé par type ---")
    for cat_type in ['Entrée', 'Sortie', 'Épargne', 'Patrimoine']:
        count = len(df[df['Type'] == cat_type])
        print(f"{cat_type}: {count} catégories")


if __name__ == "__main__":
    main()
