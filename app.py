"""
Application Streamlit pour la visualisation de finances personnelles.

Cette application permet de :
- Visualiser les entrées, sorties et épargne par mois
- Afficher des graphiques de répartition par catégorie
- Calculer le taux d'épargne
- Suivre l'évolution des finances dans le temps

Architecture modulaire pour faciliter les futures évolutions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os


# ============================================================================
# CONFIGURATION DE LA PAGE
# ============================================================================

st.set_page_config(
    page_title="Finances Personnelles",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# FONCTIONS DE CHARGEMENT ET TRAITEMENT DES DONNÉES
# ============================================================================

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Charge les données financières depuis un fichier Excel.

    Args:
        file_path: Chemin vers le fichier Excel

    Returns:
        DataFrame avec les données financières

    Raises:
        FileNotFoundError: Si le fichier n'existe pas
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} n'existe pas.")

    df = pd.read_excel(file_path, engine='openpyxl')
    return df


def get_available_months(df: pd.DataFrame) -> list:
    """
    Extrait la liste des mois disponibles dans le DataFrame.

    Args:
        df: DataFrame avec les données financières

    Returns:
        Liste des mois au format YYYY-MM
    """
    # Les colonnes de mois sont toutes celles qui ne sont pas 'Catégorie' ou 'Type'
    months = [col for col in df.columns if col not in ['Catégorie', 'Type']]
    return sorted(months)


def get_month_data(df: pd.DataFrame, month: str) -> dict:
    """
    Calcule les totaux et détails pour un mois donné.

    Args:
        df: DataFrame avec les données financières
        month: Mois au format YYYY-MM

    Returns:
        Dictionnaire contenant les totaux et détails par catégorie
    """
    # Filtrer par type
    entrees = df[df['Type'] == 'Entrée'][['Catégorie', month]].copy()
    sorties = df[df['Type'] == 'Sortie'][['Catégorie', month]].copy()
    epargne = df[df['Type'] == 'Épargne'][['Catégorie', month]].copy()

    # Renommer la colonne du mois en 'Montant' pour plus de clarté
    entrees.rename(columns={month: 'Montant'}, inplace=True)
    sorties.rename(columns={month: 'Montant'}, inplace=True)
    epargne.rename(columns={month: 'Montant'}, inplace=True)

    # Calculer les totaux
    total_entrees = entrees['Montant'].sum()
    total_sorties = sorties['Montant'].sum()
    total_epargne = epargne['Montant'].sum()

    # Calculer le taux d'épargne (épargne / entrées * 100)
    taux_epargne = (total_epargne / total_entrees * 100) if total_entrees > 0 else 0

    # Calculer le solde (entrées - sorties - épargne)
    solde = total_entrees - total_sorties - total_epargne

    return {
        'entrees': entrees,
        'sorties': sorties,
        'epargne': epargne,
        'total_entrees': total_entrees,
        'total_sorties': total_sorties,
        'total_epargne': total_epargne,
        'taux_epargne': taux_epargne,
        'solde': solde
    }


def get_all_categories(df: pd.DataFrame) -> list:
    """
    Extrait la liste de toutes les catégories avec leur type.

    Args:
        df: DataFrame avec les données financières

    Returns:
        Liste de tuples (catégorie, type)
    """
    categories = []
    for _, row in df.iterrows():
        categories.append((row['Catégorie'], row['Type']))
    return categories


def get_category_evolution(df: pd.DataFrame, category: str) -> dict:
    """
    Récupère l'évolution d'une catégorie sur tous les mois.

    Args:
        df: DataFrame avec les données financières
        category: Nom de la catégorie

    Returns:
        Dictionnaire avec l'évolution et les statistiques
    """
    # Trouver la ligne de la catégorie
    cat_row = df[df['Catégorie'] == category]

    if cat_row.empty:
        return None

    # Extraire le type
    cat_type = cat_row['Type'].values[0]

    # Extraire les mois et valeurs
    months = [col for col in df.columns if col not in ['Catégorie', 'Type']]
    values = []

    for month in months:
        values.append(cat_row[month].values[0])

    # Calculer les statistiques
    values_array = pd.Series(values)
    stats = {
        'min': values_array.min(),
        'max': values_array.max(),
        'mean': values_array.mean(),
        'median': values_array.median(),
        'std': values_array.std(),
        'total': values_array.sum()
    }

    return {
        'category': category,
        'type': cat_type,
        'months': months,
        'values': values,
        'stats': stats
    }


def plot_category_evolution(evolution_data: dict) -> go.Figure:
    """
    Crée un graphique d'évolution pour une catégorie.

    Args:
        evolution_data: Données d'évolution de la catégorie

    Returns:
        Figure Plotly
    """
    months = evolution_data['months']
    values = evolution_data['values']
    category = evolution_data['category']
    cat_type = evolution_data['type']

    # Couleur selon le type
    color_map = {
        'Entrée': '#228B22',  # Vert
        'Sortie': '#DC143C',  # Rouge
        'Épargne': '#1E90FF'  # Bleu
    }
    color = color_map.get(cat_type, '#808080')

    fig = go.Figure()

    # Ligne d'évolution
    fig.add_trace(go.Scatter(
        x=months,
        y=values,
        mode='lines+markers',
        name=category,
        line=dict(color=color, width=3),
        marker=dict(size=8, color=color),
        hovertemplate='%{x}<br>%{y:.2f} €<extra></extra>'
    ))

    # Ligne de moyenne
    mean_value = evolution_data['stats']['mean']
    fig.add_trace(go.Scatter(
        x=months,
        y=[mean_value] * len(months),
        mode='lines',
        name='Moyenne',
        line=dict(color='gray', width=2, dash='dash'),
        hovertemplate=f'Moyenne: {mean_value:.2f} €<extra></extra>'
    ))

    fig.update_layout(
        title=f"Évolution de '{category}' ({cat_type})",
        xaxis_title="Mois",
        yaxis_title="Montant (€)",
        height=500,
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig


def display_category_stats(evolution_data: dict):
    """
    Affiche les statistiques d'une catégorie.

    Args:
        evolution_data: Données d'évolution de la catégorie
    """
    stats = evolution_data['stats']

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            label="📉 Minimum",
            value=f"{stats['min']:.2f} €"
        )

    with col2:
        st.metric(
            label="📈 Maximum",
            value=f"{stats['max']:.2f} €"
        )

    with col3:
        st.metric(
            label="📊 Moyenne",
            value=f"{stats['mean']:.2f} €"
        )

    with col4:
        st.metric(
            label="📍 Médiane",
            value=f"{stats['median']:.2f} €"
        )

    with col5:
        st.metric(
            label="📊 Écart-type",
            value=f"{stats['std']:.2f} €"
        )

    # Statistiques additionnelles
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        variation = stats['max'] - stats['min']
        st.metric(
            label="🔄 Variation (max-min)",
            value=f"{variation:.2f} €"
        )

    with col2:
        if stats['mean'] > 0:
            volatilite = (stats['std'] / stats['mean']) * 100
            st.metric(
                label="📈 Volatilité",
                value=f"{volatilite:.1f}%"
            )

    with col3:
        st.metric(
            label="💰 Total cumulé",
            value=f"{stats['total']:.2f} €"
        )


# ============================================================================
# FONCTIONS DE VISUALISATION
# ============================================================================

def display_metrics(data: dict):
    """
    Affiche les métriques clés dans des colonnes Streamlit.

    Args:
        data: Dictionnaire contenant les données du mois
    """
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total Entrées",
            value=f"{data['total_entrees']:.2f} €"
        )

    with col2:
        st.metric(
            label="💸 Total Sorties",
            value=f"{data['total_sorties']:.2f} €"
        )

    with col3:
        st.metric(
            label="🏦 Total Épargne",
            value=f"{data['total_epargne']:.2f} €"
        )

    with col4:
        st.metric(
            label="📊 Taux d'Épargne",
            value=f"{data['taux_epargne']:.1f}%"
        )

    # Afficher le solde restant
    st.markdown("---")
    solde_color = "green" if data['solde'] >= 0 else "red"
    st.markdown(
        f"**Solde du mois:** <span style='color:{solde_color}; font-size:20px'>"
        f"{data['solde']:.2f} €</span>",
        unsafe_allow_html=True
    )


def plot_pie_chart(df: pd.DataFrame, title: str, color_scheme: str = 'Blues') -> go.Figure:
    """
    Crée un graphique en camembert pour la répartition des catégories.

    Args:
        df: DataFrame avec colonnes 'Catégorie' et 'Montant'
        title: Titre du graphique
        color_scheme: Schéma de couleurs Plotly

    Returns:
        Figure Plotly
    """
    fig = px.pie(
        df,
        values='Montant',
        names='Catégorie',
        title=title,
        color_discrete_sequence=px.colors.sequential.RdBu,
        hole=0.3  # Donut chart
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value:.2f} €<br>%{percent}<extra></extra>'
    )

    fig.update_layout(
        showlegend=True,
        height=400,
        margin=dict(t=50, b=20, l=20, r=20)
    )

    return fig


def plot_bar_chart(df: pd.DataFrame, title: str, color: str = '#1f77b4') -> go.Figure:
    """
    Crée un graphique en barres pour les montants par catégorie.

    Args:
        df: DataFrame avec colonnes 'Catégorie' et 'Montant'
        title: Titre du graphique
        color: Couleur des barres

    Returns:
        Figure Plotly
    """
    # Trier par montant décroissant
    df_sorted = df.sort_values('Montant', ascending=True)

    fig = go.Figure(data=[
        go.Bar(
            x=df_sorted['Montant'],
            y=df_sorted['Catégorie'],
            orientation='h',
            marker_color=color,
            text=df_sorted['Montant'].apply(lambda x: f'{x:.2f} €'),
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>%{x:.2f} €<extra></extra>'
        )
    ])

    fig.update_layout(
        title=title,
        xaxis_title="Montant (€)",
        yaxis_title="Catégorie",
        height=max(300, len(df) * 30),  # Hauteur adaptative
        margin=dict(t=50, b=50, l=150, r=50),
        showlegend=False
    )

    return fig


def plot_sankey_diagram(data: dict) -> go.Figure:
    """
    Crée un diagramme de Sankey montrant le flux d'argent des entrées vers les sorties et l'épargne.

    Args:
        data: Dictionnaire contenant les données du mois

    Returns:
        Figure Plotly avec le diagramme de Sankey
    """
    # Préparer les données pour le diagramme de Sankey
    labels = []  # Noms de tous les nœuds
    sources = []  # Indices des nœuds sources
    targets = []  # Indices des nœuds cibles
    values = []  # Montants des flux
    colors = []  # Couleurs des liens

    # Couleurs personnalisées
    color_entrees = 'rgba(34, 139, 34, 0.4)'  # Vert pour les entrées
    color_sorties = 'rgba(255, 99, 71, 0.4)'  # Rouge pour les sorties
    color_epargne = 'rgba(65, 105, 225, 0.4)'  # Bleu pour l'épargne

    # Index des nœuds
    current_index = 0

    # 1. Ajouter les nœuds d'entrées avec montants
    entrees_start_idx = current_index
    for _, row in data['entrees'].iterrows():
        labels.append(f"{row['Catégorie']}<br>{row['Montant']:.0f} €")
        current_index += 1
    entrees_end_idx = current_index

    # 2. Ajouter le nœud central "Total Entrées"
    total_entrees_idx = current_index
    labels.append(f"💰 Total<br>{data['total_entrees']:.0f} €")
    current_index += 1

    # 3. Ajouter les nœuds de sorties avec montants
    sorties_start_idx = current_index
    for _, row in data['sorties'].iterrows():
        labels.append(f"{row['Catégorie']}<br>{row['Montant']:.0f} €")
        current_index += 1
    sorties_end_idx = current_index

    # 4. Ajouter les nœuds d'épargne avec montants
    epargne_start_idx = current_index
    for _, row in data['epargne'].iterrows():
        labels.append(f"{row['Catégorie']}<br>{row['Montant']:.0f} €")
        current_index += 1
    epargne_end_idx = current_index

    # 5. Calculer et ajouter le nœud "Marge non épargnée"
    marge_non_epargnee = data['total_entrees'] - data['total_sorties'] - data['total_epargne']
    marge_idx = None
    if marge_non_epargnee > 0:
        marge_idx = current_index
        labels.append(f"💎 Marge non épargnée<br>{marge_non_epargnee:.0f} €")
        current_index += 1

    # Créer les liens : Entrées -> Total Entrées
    for idx, (_, row) in enumerate(data['entrees'].iterrows()):
        sources.append(entrees_start_idx + idx)
        targets.append(total_entrees_idx)
        values.append(row['Montant'])
        colors.append(color_entrees)

    # Créer les liens : Total Entrées -> Sorties
    for idx, (_, row) in enumerate(data['sorties'].iterrows()):
        sources.append(total_entrees_idx)
        targets.append(sorties_start_idx + idx)
        values.append(row['Montant'])
        colors.append(color_sorties)

    # Créer les liens : Total Entrées -> Épargne
    for idx, (_, row) in enumerate(data['epargne'].iterrows()):
        sources.append(total_entrees_idx)
        targets.append(epargne_start_idx + idx)
        values.append(row['Montant'])
        colors.append(color_epargne)

    # Créer le lien : Total Entrées -> Marge non épargnée
    if marge_idx is not None:
        sources.append(total_entrees_idx)
        targets.append(marge_idx)
        values.append(marge_non_epargnee)
        colors.append(color_epargne)  # Bleu comme l'épargne

    # Créer le diagramme de Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color='white', width=2),
            label=labels,
            color=['#228B22' if i < entrees_end_idx  # Vert foncé pour entrées
                   else '#FFA500' if i == total_entrees_idx  # Orange pour le nœud central
                   else '#DC143C' if sorties_start_idx <= i < sorties_end_idx  # Rouge foncé pour sorties
                   else '#1E90FF' if epargne_start_idx <= i < epargne_end_idx  # Bleu foncé pour épargne
                   else '#1E90FF' if marge_idx is not None and i == marge_idx  # Bleu pour marge non épargnée
                   else '#808080'  # Gris par défaut
                   for i in range(len(labels))],
            customdata=[f'{i}' for i in range(len(labels))],
            hovertemplate='<b>%{label}</b><extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            hovertemplate='%{value:.2f} €<extra></extra>'
        )
    )])

    fig.update_layout(
        title={
            'text': "🌊 Flux d'Argent - Diagramme de Sankey",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18, 'color': '#333'}
        },
        font=dict(size=13, color='black', family='Arial, sans-serif'),
        height=700,
        margin=dict(t=80, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def calculate_financial_score(data: dict, user_params: dict, df: pd.DataFrame) -> dict:
    """
    Calcule le score financier global basé sur différents critères.

    Args:
        data: Données financières du mois
        user_params: Paramètres additionnels fournis par l'utilisateur
        df: DataFrame complet avec toutes les données historiques

    Returns:
        Dictionnaire contenant tous les scores et détails
    """
    scores = {
        'budget': {'max': 40, 'score': 0, 'details': []},
        'matelas': {'max': 15, 'score': 0, 'details': []},
        'bourse': {'max': 25, 'score': 0, 'details': []},
        'immobilier': {'max': 10, 'score': 0, 'details': []},
        'crypto': {'max': 4, 'score': 0, 'details': []},
        'reflexes': {'max': 6, 'score': 0, 'details': []}
    }

    # ========================================================================
    # BUDGET (40 points)
    # ========================================================================

    # 1. Gagner plus que ce qu'on ne dépense (20 points)
    # Note: L'épargne n'est PAS considérée comme une dépense
    total_depenses = data['total_sorties']
    if data['total_entrees'] > total_depenses:
        scores['budget']['score'] += 20
        scores['budget']['details'].append({
            'critere': 'Gagner plus que ce qu\'on ne dépense',
            'score': 20,
            'max': 20,
            'obtenu': True,
            'explication': f"Entrées ({data['total_entrees']:.0f}€) > Dépenses ({total_depenses:.0f}€)",
            'calculable': True
        })
    else:
        scores['budget']['details'].append({
            'critere': 'Gagner plus que ce qu\'on ne dépense',
            'score': 0,
            'max': 20,
            'obtenu': False,
            'explication': f"Entrées ({data['total_entrees']:.0f}€) ≤ Dépenses ({total_depenses:.0f}€)",
            'calculable': True
        })

    # 2. Se payer en premier (20 points)
    taux_epargne_minimal = 10  # Au moins 10% d'épargne
    if data['taux_epargne'] >= taux_epargne_minimal:
        scores['budget']['score'] += 20
        scores['budget']['details'].append({
            'critere': 'Se payer en premier (≥10% d\'épargne)',
            'score': 20,
            'max': 20,
            'obtenu': True,
            'explication': f"Épargne ({data['total_epargne']:.0f}€) / Entrées ({data['total_entrees']:.0f}€) × 100 = {data['taux_epargne']:.1f}% (≥{taux_epargne_minimal}%)",
            'calculable': True
        })
    else:
        score_partiel = int((data['taux_epargne'] / taux_epargne_minimal) * 20)
        scores['budget']['score'] += score_partiel
        scores['budget']['details'].append({
            'critere': 'Se payer en premier (≥10% d\'épargne)',
            'score': score_partiel,
            'max': 20,
            'obtenu': False,
            'explication': f"Épargne ({data['total_epargne']:.0f}€) / Entrées ({data['total_entrees']:.0f}€) × 100 = {data['taux_epargne']:.1f}% (<{taux_epargne_minimal}%) = {score_partiel}/20 pts",
            'calculable': True
        })

    # ========================================================================
    # MATELAS DE SÉCURITÉ (15 points)
    # ========================================================================

    # Calculer automatiquement l'épargne totale accumulée et la moyenne des dépenses
    # 1. Récupérer tous les mois disponibles
    month_columns = [col for col in df.columns if col not in ['Catégorie', 'Type']]

    # 2. Calculer l'épargne totale accumulée (somme de toutes les épargnes de tous les mois)
    epargne_rows = df[df['Type'] == 'Épargne']
    epargne_totale_accumulee = 0
    for month_col in month_columns:
        epargne_totale_accumulee += epargne_rows[month_col].sum()

    # 3. Calculer la moyenne des dépenses mensuelles (sorties uniquement)
    sorties_rows = df[df['Type'] == 'Sortie']
    depenses_mensuelles = []
    for month_col in month_columns:
        depenses_mensuelles.append(sorties_rows[month_col].sum())
    moyenne_depenses = sum(depenses_mensuelles) / len(depenses_mensuelles) if depenses_mensuelles else 0

    # 4. Calculer le nombre de mois de couverture
    mois_couverture = epargne_totale_accumulee / moyenne_depenses if moyenne_depenses > 0 else 0

    # 5. Attribuer le score en fonction du nombre de mois
    if mois_couverture >= 3 and mois_couverture <= 6:
        scores['matelas']['score'] = 15
        scores['matelas']['details'].append({
            'critere': '3 à 6 mois de dépenses en épargne',
            'score': 15,
            'max': 15,
            'obtenu': True,
            'explication': f"Épargne accumulée ({epargne_totale_accumulee:.0f}€) / Moyenne dépenses ({moyenne_depenses:.0f}€/mois) = {mois_couverture:.1f} mois",
            'calculable': True
        })
    elif mois_couverture > 6:
        scores['matelas']['score'] = 12
        scores['matelas']['details'].append({
            'critere': '3 à 6 mois de dépenses en épargne',
            'score': 12,
            'max': 15,
            'obtenu': False,
            'explication': f"Épargne accumulée ({epargne_totale_accumulee:.0f}€) / Moyenne dépenses ({moyenne_depenses:.0f}€/mois) = {mois_couverture:.1f} mois (>6, peut-être trop liquide)",
            'calculable': True
        })
    else:
        score_partiel = int((mois_couverture / 3) * 15)
        scores['matelas']['score'] = min(score_partiel, 15)
        scores['matelas']['details'].append({
            'critere': '3 à 6 mois de dépenses en épargne',
            'score': score_partiel,
            'max': 15,
            'obtenu': False,
            'explication': f"Épargne accumulée ({epargne_totale_accumulee:.0f}€) / Moyenne dépenses ({moyenne_depenses:.0f}€/mois) = {mois_couverture:.1f} mois (<3 mois)",
            'calculable': True
        })

    # ========================================================================
    # BOURSE (25 points)
    # ========================================================================

    # Détecter automatiquement les investissements PEA/CTO dans les catégories d'épargne
    epargne_categories = df[df['Type'] == 'Épargne']['Catégorie'].tolist()
    has_pea = any(cat.startswith('PEA') for cat in epargne_categories)
    has_cto = any(cat.startswith('CTO') for cat in epargne_categories)
    has_bourse = has_pea or has_cto

    # 1. Investissement en bourse (10 points) - Auto-détecté
    if has_bourse:
        scores['bourse']['score'] += 10
        categories_bourse = [cat for cat in epargne_categories if cat.startswith('PEA') or cat.startswith('CTO')]
        scores['bourse']['details'].append({
            'critere': 'Investissement en bourse',
            'score': 10,
            'max': 10,
            'obtenu': True,
            'explication': f"Détecté: {', '.join(categories_bourse)}",
            'calculable': True
        })
    else:
        scores['bourse']['details'].append({
            'critere': 'Investissement en bourse',
            'score': 0,
            'max': 10,
            'obtenu': False,
            'explication': 'Aucune catégorie PEA/CTO détectée',
            'calculable': True
        })

    # 2. Investissement via PEA en priorité (3 points) - Auto-détecté
    if has_pea:
        scores['bourse']['score'] += 3
        pea_categories = [cat for cat in epargne_categories if cat.startswith('PEA')]
        scores['bourse']['details'].append({
            'critere': 'Investissement via PEA en priorité',
            'score': 3,
            'max': 3,
            'obtenu': True,
            'explication': f"Détecté: {', '.join(pea_categories)}",
            'calculable': True
        })
    else:
        scores['bourse']['details'].append({
            'critere': 'Investissement via PEA en priorité',
            'score': 0,
            'max': 3,
            'obtenu': False,
            'explication': 'Aucune catégorie PEA détectée',
            'calculable': True
        })

    # 3. CTO (Compte-Titres Ordinaire) (1 point) - Auto-détecté
    if has_cto:
        scores['bourse']['score'] += 1
        cto_categories = [cat for cat in epargne_categories if cat.startswith('CTO')]
        scores['bourse']['details'].append({
            'critere': 'CTO (Compte-Titres Ordinaire)',
            'score': 1,
            'max': 1,
            'obtenu': True,
            'explication': f"Détecté: {', '.join(cto_categories)}",
            'calculable': True
        })
    else:
        scores['bourse']['details'].append({
            'critere': 'CTO (Compte-Titres Ordinaire)',
            'score': 0,
            'max': 1,
            'obtenu': False,
            'explication': 'Aucune catégorie CTO détectée',
            'calculable': True
        })

    # Critères manuels restants
    bourse_criteres_manuels = [
        ('Investissement sur des ETFs', 3),
        ('Minimum d\'overlap entre les ETFs', 1),
        ('Frais au plancher', 2),
        ('DCA tous les mois', 3),
        ('Si stock-picking, pas plus de 20%', 1),
        ('Prise de date sur Assurance Vie', 1)
    ]

    for critere, max_pts in bourse_criteres_manuels:
        scores['bourse']['details'].append({
            'critere': critere,
            'score': 0,
            'max': max_pts,
            'obtenu': False,
            'explication': 'À renseigner manuellement',
            'calculable': False
        })

    # ========================================================================
    # IMMOBILIER (10 points)
    # ========================================================================

    immo_criteres = [
        ('Si achat > Effet de levier', 5),
        ('Immobilier locatif', 5)
    ]

    for critere, max_pts in immo_criteres:
        scores['immobilier']['details'].append({
            'critere': critere,
            'score': 0,
            'max': max_pts,
            'obtenu': False,
            'explication': 'À renseigner manuellement',
            'calculable': False
        })

    # ========================================================================
    # CRYPTO (4 points)
    # ========================================================================

    crypto_criteres = [
        ('Bitcoin', 2),
        ('Ethereum', 1),
        ('DCA tous les mois/semaines', 1)
    ]

    for critere, max_pts in crypto_criteres:
        scores['crypto']['details'].append({
            'critere': critere,
            'score': 0,
            'max': max_pts,
            'obtenu': False,
            'explication': 'À renseigner manuellement',
            'calculable': False
        })

    # ========================================================================
    # RÉFLEXES GLOBAUX (6 points)
    # ========================================================================

    reflexes_criteres = [
        ('Investissement en soi', 1),
        ('Vision long terme', 1),
        ('Objectif clairement défini', 2),
        ('Optimisation de la fiscalité', 1),
        ('Patrimoine suffisamment liquide', 1)
    ]

    for critere, max_pts in reflexes_criteres:
        scores['reflexes']['details'].append({
            'critere': critere,
            'score': 0,
            'max': max_pts,
            'obtenu': False,
            'explication': 'À renseigner manuellement',
            'calculable': False
        })

    # ========================================================================
    # CALCUL DU SCORE TOTAL
    # ========================================================================

    total_score = sum(cat['score'] for cat in scores.values())
    total_max = sum(cat['max'] for cat in scores.values())
    pourcentage = (total_score / total_max * 100) if total_max > 0 else 0

    scores['total'] = {
        'score': total_score,
        'max': total_max,
        'pourcentage': pourcentage
    }

    return scores


def display_financial_score(scores: dict):
    """
    Affiche le score financier avec tous les détails.

    Args:
        scores: Dictionnaire contenant tous les scores calculés
    """
    st.markdown("## 🎯 Score Financier Global")

    # Score total
    total = scores['total']
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown(f"### Score: **{total['score']}/{total['max']}** points")

    with col2:
        st.markdown(f"### **{total['pourcentage']:.1f}%**")

    with col3:
        if total['pourcentage'] >= 80:
            emoji = "🏆"
            niveau = "Excellence"
        elif total['pourcentage'] >= 60:
            emoji = "🥈"
            niveau = "Bon"
        elif total['pourcentage'] >= 40:
            emoji = "🥉"
            niveau = "Moyen"
        else:
            emoji = "📈"
            niveau = "À améliorer"
        st.markdown(f"### {emoji} {niveau}")

    # Barre de progression
    progress_color = "green" if total['pourcentage'] >= 60 else "orange" if total['pourcentage'] >= 40 else "red"
    st.markdown(f"""
        <div style="background-color: #e0e0e0; border-radius: 10px; height: 30px; margin: 10px 0;">
            <div style="background-color: {progress_color}; width: {total['pourcentage']:.1f}%;
                        height: 100%; border-radius: 10px; text-align: center; line-height: 30px;
                        color: white; font-weight: bold;">
                {total['pourcentage']:.1f}%
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Détails par catégorie
    categories = [
        ('budget', '💰 Budget', 'success'),
        ('matelas', '🛡️ Matelas de sécurité', 'info'),
        ('bourse', '📈 Bourse', 'warning'),
        ('immobilier', '🏠 Immobilier', 'secondary'),
        ('crypto', '₿ Crypto', 'primary'),
        ('reflexes', '🧠 Réflexes globaux', 'light')
    ]

    for key, title, _ in categories:
        cat_data = scores[key]
        cat_score = cat_data['score']
        cat_max = cat_data['max']
        cat_pct = (cat_score / cat_max * 100) if cat_max > 0 else 0

        with st.expander(f"{title} - {cat_score}/{cat_max} pts ({cat_pct:.0f}%)", expanded=False):
            for detail in cat_data['details']:
                if detail['calculable']:
                    # Critère calculable - afficher en vert si obtenu, jaune sinon
                    color = "green" if detail['obtenu'] else "orange"
                    st.markdown(
                        f"<div style='padding: 8px; margin: 5px 0; background-color: rgba({('0,128,0' if detail['obtenu'] else '255,165,0')},0.1); "
                        f"border-left: 4px solid {color}; border-radius: 4px;'>"
                        f"<b>{detail['critere']}</b>: {detail['score']}/{detail['max']} pts<br>"
                        f"<small style='color: #666;'>{detail['explication']}</small>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    # Critère non calculable - afficher en rouge
                    st.markdown(
                        f"<div style='padding: 8px; margin: 5px 0; background-color: rgba(255,0,0,0.1); "
                        f"border-left: 4px solid red; border-radius: 4px;'>"
                        f"<b style='color: red;'>{detail['critere']}</b>: 0/{detail['max']} pts<br>"
                        f"<small style='color: #666;'>{detail['explication']}</small>"
                        f"</div>",
                        unsafe_allow_html=True
                    )


def display_comparison_metrics(data1: dict, data2: dict, month1: str, month2: str):
    """
    Affiche une comparaison des métriques entre deux mois.

    Args:
        data1: Données du premier mois
        data2: Données du deuxième mois
        month1: Nom du premier mois
        month2: Nom du deuxième mois
    """
    st.markdown(f"### 📊 Comparaison: **{month1}** vs **{month2}**")

    col1, col2, col3, col4 = st.columns(4)

    # Calculer les différences
    diff_entrees = data2['total_entrees'] - data1['total_entrees']
    diff_sorties = data2['total_sorties'] - data1['total_sorties']
    diff_epargne = data2['total_epargne'] - data1['total_epargne']
    diff_taux = data2['taux_epargne'] - data1['taux_epargne']

    with col1:
        st.metric(
            label="💰 Entrées",
            value=f"{data2['total_entrees']:.2f} €",
            delta=f"{diff_entrees:+.2f} €"
        )

    with col2:
        st.metric(
            label="💸 Sorties",
            value=f"{data2['total_sorties']:.2f} €",
            delta=f"{diff_sorties:+.2f} €"
        )

    with col3:
        st.metric(
            label="🏦 Épargne",
            value=f"{data2['total_epargne']:.2f} €",
            delta=f"{diff_epargne:+.2f} €"
        )

    with col4:
        st.metric(
            label="📊 Taux d'Épargne",
            value=f"{data2['taux_epargne']:.1f}%",
            delta=f"{diff_taux:+.1f}%"
        )


def plot_comparison_bar(data1: dict, data2: dict, month1: str, month2: str,
                        category_type: str) -> go.Figure:
    """
    Crée un graphique en barres comparatif entre deux mois pour une catégorie.

    Args:
        data1: Données du premier mois
        data2: Données du deuxième mois
        month1: Nom du premier mois
        month2: Nom du deuxième mois
        category_type: Type de catégorie ('sorties' ou 'epargne')

    Returns:
        Figure Plotly
    """
    df1 = data1[category_type].copy()
    df2 = data2[category_type].copy()

    # Fusionner les données
    df_merged = df1.merge(df2, on='Catégorie', how='outer', suffixes=('_1', '_2'))
    df_merged = df_merged.fillna(0)

    # Calculer la différence
    df_merged['Différence'] = df_merged['Montant_2'] - df_merged['Montant_1']
    df_merged = df_merged.sort_values('Montant_2', ascending=True)

    fig = go.Figure()

    # Barres pour le premier mois
    fig.add_trace(go.Bar(
        y=df_merged['Catégorie'],
        x=df_merged['Montant_1'],
        name=month1,
        orientation='h',
        marker_color='lightblue',
        text=df_merged['Montant_1'].apply(lambda x: f'{x:.0f} €'),
        textposition='outside'
    ))

    # Barres pour le deuxième mois
    fig.add_trace(go.Bar(
        y=df_merged['Catégorie'],
        x=df_merged['Montant_2'],
        name=month2,
        orientation='h',
        marker_color='darkblue',
        text=df_merged['Montant_2'].apply(lambda x: f'{x:.0f} €'),
        textposition='outside'
    ))

    title_map = {'sorties': 'Sorties', 'epargne': 'Épargne'}

    fig.update_layout(
        title=f"Comparaison des {title_map.get(category_type, category_type)}",
        xaxis_title="Montant (€)",
        yaxis_title="Catégorie",
        height=max(400, len(df_merged) * 40),
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=80, b=50, l=150, r=100)
    )

    return fig


def display_detailed_tables(data: dict):
    """
    Affiche les tableaux détaillés pour chaque type de transaction.

    Args:
        data: Dictionnaire contenant les données du mois
    """
    st.markdown("### 📋 Détails par Catégorie")

    tab1, tab2, tab3 = st.tabs(["Entrées", "Sorties", "Épargne"])

    with tab1:
        st.dataframe(
            data['entrees'].style.format({'Montant': '{:.2f} €'}),
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.dataframe(
            data['sorties'].style.format({'Montant': '{:.2f} €'}),
            use_container_width=True,
            hide_index=True
        )

    with tab3:
        st.dataframe(
            data['epargne'].style.format({'Montant': '{:.2f} €'}),
            use_container_width=True,
            hide_index=True
        )


# ============================================================================
# INTERFACE PRINCIPALE
# ============================================================================

def main():
    """
    Fonction principale de l'application Streamlit.
    """

    # En-tête
    st.title("💰 Tableau de Bord - Finances Personnelles")
    st.markdown("Visualisez et analysez vos finances mensuelles de manière claire et intuitive.")

    # Sidebar pour la configuration
    st.sidebar.header("⚙️ Configuration")

    # Sélection du fichier de données
    default_file = "finances_data.xlsx"

    if not os.path.exists(default_file):
        st.error(
            f"❌ Le fichier '{default_file}' n'existe pas. "
            f"Veuillez d'abord générer les données fictives en exécutant : "
            f"`python generate_sample_data.py`"
        )
        st.stop()

    # Charger les données
    try:
        df = load_data(default_file)
        st.sidebar.success(f"✓ Données chargées: {default_file}")

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        st.stop()

    # Sélection du mois
    available_months = get_available_months(df)

    if not available_months:
        st.error("❌ Aucun mois trouvé dans les données.")
        st.stop()

    # Navigation principale
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 Navigation")
    page = st.sidebar.radio(
        "Choisissez une vue :",
        options=[
            "📊 Tableau de bord - Vue Simplifiée",
            "⚖️ Tableau de bord - Comparaison",
            "📈 Évolution d'une Catégorie"
        ],
        index=0
    )

    st.sidebar.markdown("---")

    # Informations générales
    st.sidebar.markdown("### 📊 Informations")
    st.sidebar.info(
        f"**Catégories totales:** {len(df)}\n\n"
        f"**Mois disponibles:** {len(available_months)}"
    )

    # ========================================================================
    # PAGE 1 : VUE SIMPLIFIÉE
    # ========================================================================
    if page == "📊 Tableau de bord - Vue Simplifiée":
        st.markdown("## 📊 Tableau de bord - Vue Simplifiée")

        # Sélecteur de mois dans la page
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            selected_month = st.selectbox(
                "📅 Sélectionnez un mois :",
                options=available_months,
                index=len(available_months) - 1,  # Dernier mois par défaut
                key="month_simple"
            )

        st.markdown("---")

        # Récupérer les données du mois sélectionné
        month_data = get_month_data(df, selected_month)

        # Paramètres pour le score (dans la page)
        user_params = {'epargne_totale': None}

        # Afficher les métriques clés
        display_metrics(month_data)

        st.markdown("---")

        # Diagramme de Sankey - Flux d'argent
        st.markdown("### 🌊 Flux d'Argent")
        fig_sankey = plot_sankey_diagram(month_data)
        st.plotly_chart(fig_sankey, use_container_width=True)

        st.markdown("---")

        # Visualisations graphiques
        st.markdown("### 📊 Visualisations")

        col1, col2 = st.columns(2)

        with col1:
            # Graphique des sorties
            if not month_data['sorties'].empty:
                fig_sorties = plot_pie_chart(
                    month_data['sorties'],
                    "Répartition des Sorties"
                )
                st.plotly_chart(fig_sorties, use_container_width=True)
            else:
                st.info("Aucune donnée de sorties pour ce mois.")

        with col2:
            # Graphique de l'épargne
            if not month_data['epargne'].empty:
                fig_epargne = plot_pie_chart(
                    month_data['epargne'],
                    "Répartition de l'Épargne"
                )
                st.plotly_chart(fig_epargne, use_container_width=True)
            else:
                st.info("Aucune donnée d'épargne pour ce mois.")

        # Graphique en barres pour les sorties (vue alternative)
        st.markdown("### 📊 Détail des Sorties par Catégorie")
        if not month_data['sorties'].empty:
            fig_bar_sorties = plot_bar_chart(
                month_data['sorties'],
                "Montant des Sorties par Catégorie",
                color='#ff7f0e'
            )
            st.plotly_chart(fig_bar_sorties, use_container_width=True)

        st.markdown("---")

        # Tableaux détaillés
        display_detailed_tables(month_data)

        st.markdown("---")

        # Score financier
        scores = calculate_financial_score(month_data, user_params, df)
        display_financial_score(scores)

    # ========================================================================
    # PAGE 2 : COMPARAISON
    # ========================================================================
    elif page == "⚖️ Tableau de bord - Comparaison":
        st.markdown("## ⚖️ Tableau de bord - Comparaison")

        # Sélecteurs de mois dans la page (centrés)
        col1, col2, col3, col4, col5 = st.columns([1, 1.5, 0.5, 1.5, 1])
        with col2:
            selected_month = st.selectbox(
                "📅 Mois 1 :",
                options=available_months,
                index=max(0, len(available_months) - 2),  # Avant-dernier mois
                key="month_comp_1"
            )
        with col4:
            selected_month2 = st.selectbox(
                "📅 Mois 2 :",
                options=available_months,
                index=len(available_months) - 1,  # Dernier mois
                key="month_comp_2"
            )

        st.markdown("---")

        # Récupérer les données des deux mois
        month_data = get_month_data(df, selected_month)
        month_data2 = get_month_data(df, selected_month2)

        # Paramètres pour le score (dans la page)
        user_params = {'epargne_totale': None}

        # Métriques de comparaison
        display_comparison_metrics(month_data, month_data2, selected_month, selected_month2)

        st.markdown("---")

        # Diagrammes de Sankey côte à côte
        st.markdown("### 🌊 Flux d'Argent")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{selected_month}**")
            fig_sankey1 = plot_sankey_diagram(month_data)
            st.plotly_chart(fig_sankey1, use_container_width=True)

        with col2:
            st.markdown(f"**{selected_month2}**")
            fig_sankey2 = plot_sankey_diagram(month_data2)
            st.plotly_chart(fig_sankey2, use_container_width=True)

        st.markdown("---")

        # Graphiques comparatifs
        st.markdown("### 📊 Comparaisons Détaillées")

        # Comparaison des sorties
        if not month_data['sorties'].empty or not month_data2['sorties'].empty:
            fig_comp_sorties = plot_comparison_bar(
                month_data, month_data2,
                selected_month, selected_month2,
                'sorties'
            )
            st.plotly_chart(fig_comp_sorties, use_container_width=True)

        # Comparaison de l'épargne
        if not month_data['epargne'].empty or not month_data2['epargne'].empty:
            fig_comp_epargne = plot_comparison_bar(
                month_data, month_data2,
                selected_month, selected_month2,
                'epargne'
            )
            st.plotly_chart(fig_comp_epargne, use_container_width=True)

        st.markdown("---")

        # Scores financiers comparés
        st.markdown("### 🎯 Comparaison des Scores Financiers")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"**{selected_month}**")
            scores1 = calculate_financial_score(month_data, user_params, df)
            display_financial_score(scores1)

        with col2:
            st.markdown(f"**{selected_month2}**")
            scores2 = calculate_financial_score(month_data2, user_params, df)
            display_financial_score(scores2)

    # ========================================================================
    # PAGE 3 : ÉVOLUTION D'UNE CATÉGORIE
    # ========================================================================
    else:  # page == "📈 Évolution d'une Catégorie"
        st.markdown("## 📈 Évolution d'une Catégorie")

        # Sélecteur de catégorie dans la page (centré)
        all_categories = get_all_categories(df)
        category_options = [f"{cat} ({typ})" for cat, typ in all_categories]

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            selected_category_full = st.selectbox(
                "🏷️ Sélectionnez une catégorie :",
                options=category_options,
                index=0,
                key="category_evolution"
            )

        # Extraire le nom de la catégorie
        selected_category = selected_category_full.split(" (")[0]

        st.markdown("---")

        # Récupérer les données d'évolution
        evolution_data = get_category_evolution(df, selected_category)

        if evolution_data is None:
            st.error(f"❌ Catégorie '{selected_category}' introuvable.")
            st.stop()

        # Extraire le type de catégorie (nécessaire pour l'analyse de tendance)
        cat_type = evolution_data['type']

        # Statistiques
        st.markdown("### 📊 Statistiques Globales")
        display_category_stats(evolution_data)

        st.markdown("---")

        # Graphique d'évolution
        st.markdown("### 📈 Graphique d'Évolution")
        fig_evolution = plot_category_evolution(evolution_data)
        st.plotly_chart(fig_evolution, use_container_width=True)

        st.markdown("---")

        # Tableau détaillé
        st.markdown("### 📋 Détails Mensuels")
        months = evolution_data['months']
        values = evolution_data['values']

        # Créer un DataFrame pour l'affichage
        detail_df = pd.DataFrame({
            'Mois': months,
            'Montant (€)': values
        })

        # Ajouter des colonnes calculées
        detail_df['Variation (€)'] = detail_df['Montant (€)'].diff()
        detail_df['Variation (%)'] = detail_df['Montant (€)'].pct_change() * 100

        # Formater et afficher
        st.dataframe(
            detail_df.style.format({
                'Montant (€)': '{:.2f}',
                'Variation (€)': '{:+.2f}',
                'Variation (%)': '{:+.1f}%'
            }),
            use_container_width=True,
            hide_index=True
        )

        # Analyses supplémentaires
        st.markdown("---")
        st.markdown("### 🔍 Analyse de Tendance")

        col1, col2 = st.columns(2)

        with col1:
            # Tendance générale
            first_value = values[0]
            last_value = values[-1]
            variation_totale = last_value - first_value
            variation_pct = (variation_totale / first_value * 100) if first_value > 0 else 0

            if variation_totale > 0:
                trend_emoji = "📈"
                trend_text = "Hausse"
                trend_color = "green" if cat_type == "Entrée" or cat_type == "Épargne" else "red"
            elif variation_totale < 0:
                trend_emoji = "📉"
                trend_text = "Baisse"
                trend_color = "red" if cat_type == "Entrée" or cat_type == "Épargne" else "green"
            else:
                trend_emoji = "➡️"
                trend_text = "Stable"
                trend_color = "gray"

            st.markdown(f"""
            **Tendance globale :** {trend_emoji} {trend_text}

            - **Premier mois :** {first_value:.2f} € ({months[0]})
            - **Dernier mois :** {last_value:.2f} € ({months[-1]})
            - **Variation :** <span style='color:{trend_color}; font-weight:bold'>{variation_totale:+.2f} € ({variation_pct:+.1f}%)</span>
            """, unsafe_allow_html=True)

        with col2:
            # Mois min et max
            min_idx = values.index(min(values))
            max_idx = values.index(max(values))

            st.markdown(f"""
            **Extrêmes :**

            - **📉 Minimum :** {min(values):.2f} € en {months[min_idx]}
            - **📈 Maximum :** {max(values):.2f} € en {months[max_idx]}
            - **🔄 Amplitude :** {max(values) - min(values):.2f} €
            """)

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray; font-size: 12px;'>"
        "Application de visualisation de finances personnelles - Développée avec Streamlit 🚀"
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    main()
