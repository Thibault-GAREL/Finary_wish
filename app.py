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
            pad=20,
            thickness=25,
            line=dict(color='white', width=2),
            label=labels,
            color=['#228B22' if i < entrees_end_idx  # Vert foncé pour entrées
                   else '#1E90FF' if i >= epargne_start_idx  # Bleu foncé pour épargne
                   else '#DC143C' if i >= sorties_start_idx  # Rouge foncé pour sorties
                   else '#FFA500'  # Orange pour le nœud central
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
        font=dict(size=14, color='white', family='Arial Black'),
        height=700,
        margin=dict(t=80, b=40, l=40, r=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


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
            delta=f"{diff_sorties:+.2f} €",
            delta_color="inverse"
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

    # Mode de visualisation
    st.sidebar.markdown("---")
    view_mode = st.sidebar.radio(
        "🔍 Mode de visualisation",
        options=["📊 Vue Simple", "⚖️ Comparaison"],
        index=0
    )

    st.sidebar.markdown("---")

    # Sélection des mois selon le mode
    if view_mode == "📊 Vue Simple":
        selected_month = st.sidebar.selectbox(
            "📅 Sélectionnez un mois",
            options=available_months,
            index=len(available_months) - 1  # Dernier mois par défaut
        )
        selected_month2 = None
    else:
        col_m1, col_m2 = st.sidebar.columns(2)
        with col_m1:
            selected_month = st.selectbox(
                "📅 Mois 1",
                options=available_months,
                index=max(0, len(available_months) - 2)  # Avant-dernier mois
            )
        with col_m2:
            selected_month2 = st.selectbox(
                "📅 Mois 2",
                options=available_months,
                index=len(available_months) - 1  # Dernier mois
            )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 Informations")
    st.sidebar.info(
        f"**Catégories totales:** {len(df)}\n\n"
        f"**Mois disponibles:** {len(available_months)}"
    )

    # Récupérer les données du/des mois sélectionné(s)
    month_data = get_month_data(df, selected_month)

    # ========================================================================
    # MODE VUE SIMPLE
    # ========================================================================
    if view_mode == "📊 Vue Simple":
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

    # ========================================================================
    # MODE COMPARAISON
    # ========================================================================
    else:
        month_data2 = get_month_data(df, selected_month2)

        # Afficher les mois comparés
        st.markdown(f"## ⚖️ Comparaison: **{selected_month}** vs **{selected_month2}**")
        st.markdown("---")

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
