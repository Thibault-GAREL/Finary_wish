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

    # 1. Ajouter les nœuds d'entrées
    entrees_start_idx = current_index
    for _, row in data['entrees'].iterrows():
        labels.append(row['Catégorie'])
        current_index += 1
    entrees_end_idx = current_index

    # 2. Ajouter le nœud central "Total Entrées"
    total_entrees_idx = current_index
    labels.append('💰 Total Entrées')
    current_index += 1

    # 3. Ajouter les nœuds de sorties
    sorties_start_idx = current_index
    for _, row in data['sorties'].iterrows():
        labels.append(row['Catégorie'])
        current_index += 1
    sorties_end_idx = current_index

    # 4. Ajouter les nœuds d'épargne
    epargne_start_idx = current_index
    for _, row in data['epargne'].iterrows():
        labels.append(row['Catégorie'])
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

    # Créer le diagramme de Sankey
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=labels,
            color=['#2E8B57' if i < entrees_end_idx  # Vert pour entrées
                   else '#4169E1' if i >= epargne_start_idx  # Bleu pour épargne
                   else '#FF6347' if i >= sorties_start_idx  # Rouge pour sorties
                   else '#FFD700'  # Or pour le nœud central
                   for i in range(len(labels))],
            customdata=[f'{i}' for i in range(len(labels))],
            hovertemplate='<b>%{label}</b><br>Total: %{value:.2f} €<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            hovertemplate='%{source.label} → %{target.label}<br>%{value:.2f} €<extra></extra>'
        )
    )])

    fig.update_layout(
        title={
            'text': "🌊 Flux d'Argent - Diagramme de Sankey",
            'x': 0.5,
            'xanchor': 'center'
        },
        font=dict(size=12),
        height=600,
        margin=dict(t=80, b=40, l=40, r=40)
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

    selected_month = st.sidebar.selectbox(
        "📅 Sélectionnez un mois",
        options=available_months,
        index=len(available_months) - 1  # Dernier mois par défaut
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Informations")
    st.sidebar.info(
        f"**Catégories totales:** {len(df)}\n\n"
        f"**Mois disponibles:** {len(available_months)}"
    )

    # Récupérer les données du mois sélectionné
    month_data = get_month_data(df, selected_month)

    # Afficher le mois sélectionné
    st.markdown(f"## 📅 Mois sélectionné: **{selected_month}**")
    st.markdown("---")

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
