# 🛠️ Commande d'installation de l'environnement :
# conda create -n projet_ds python=3.10 pandas numpy matplotlib seaborn streamlit plotly -y

### 1. Importation des librairies et chargement des données
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Tableau de bord sur les salaires en science des données", layout="wide")

# Chargement des données 
@st.cache_data
def load_data():
    if os.path.exists("ds_salaries.csv"):
        return pd.read_csv("ds_salaries.csv")
    else:
        st.error("Fichier 'ds_salaries.csv' non trouvé. Assurez-vous qu'il est dans le même dossier.")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    df['experience_level'] = df['experience_level'].replace({'EN': 'Débutant', 'MI': 'Intermédiaire', 'SE': 'Senior', 'EX': 'Expert'})
    df['company_size'] = df['company_size'].replace({'S': 'Petite', 'M': 'Moyenne', 'L': 'Grande'})
    df['employment_type'] = df['employment_type'].replace({'FT': 'Temps plein', 'PT': 'Temps partiel', 'CT': 'Contrat', 'FL': 'Freelance'})
    df['remote_ratio'] = df['remote_ratio'].replace({0: 'Présentiel', 50: 'Hybride', 100: 'Télétravail'})

# Indicateurs de synthèse 
if not df.empty:
    st.markdown("### 💰 Chiffres Clés")
    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    
    with col_kpi1:
        st.metric("💰 Salaire Moyen", f"{round(df['salary_in_usd'].mean(), 0)} $")
    with col_kpi2:
        # Calcul issu du notebook
        moy_rem = df[df['remote_ratio'] == 'Télétravail']['salary_in_usd'].mean()
        st.metric("🏠 Moyenne Télétravail", f"{round(moy_rem, 0)} $")
    with col_kpi3:
        # Vérification des valeurs nulles
        null_count = df.isnull().sum().sum()
        st.metric("🔎 Données Manquantes", "Aucune" if null_count == 0 else f"{null_count}")
    st.divider()


### 2. Exploration visuelle des données 
st.title("📊 Visualisation des Salaires en Data Science")
st.markdown("Explorez les tendances des salaires mondiaux à travers différentes visualisations interactives.")

if not df.empty:
    if st.checkbox("💾 Afficher un aperçu des données"):
        st.write(df.head(10))

    st.subheader("📌 Statistiques générales")
    st.write(df.describe())

    ### 3. Distribution des salaires en France par rôle et niveau d'expérience 
    st.subheader("📈 Distribution des salaires en France")
    # Filtrage pour la France 
    df_fr = df[df['employee_residence'] == 'FR']
    
    if not df_fr.empty:
        fig_box = px.box(df_fr, x='experience_level', y='salary_in_usd', color='experience_level',
                         title="Dispersion des salaires en France par niveau d'expérience",
                         labels={'salary_in_usd': 'Salaire (USD)', 'experience_level': "Niveau d'expérience"},
                         points="all")
        st.plotly_chart(fig_box)
        st.markdown("**Interprétation :** On remarque une progression logique du salaire médian avec l'expérience. Les écarts (outliers) sont plus marqués sur les profils Senior (SE), reflétant une forte spécialisation ou des bonus variables.")
    else:
        st.warning("Pas de données disponibles pour la France.")

    ### 4. Analyse des tendances de salaires par catégorie 
    st.subheader("🎯 Salaire moyen par catégorie")
    categorie = st.selectbox("Choisissez une catégorie d'analyse :", 
                             ['experience_level', 'employment_type', 'job_title', 'company_location'])
    
    # Calcul de la moyenne
    df_grouped = df.groupby(categorie)['salary_in_usd'].mean().sort_values(ascending=False).reset_index()
    
    fig_bar = px.bar(df_grouped, x=categorie, y='salary_in_usd', 
                     title=f"Salaire moyen par {categorie}",
                     color='salary_in_usd', color_continuous_scale='Viridis',
                     labels={'salary_in_usd': 'Salaire moyen (USD)', 'experience_level': "Niveau d'expérience", 'employment_type': "Type d'emploi", 'job_title': "Métier", 'company_location': "Localisation"})
    st.plotly_chart(fig_bar)
    st.markdown(f"**Interprétation :** Ce graphique permet d'identifier rapidement les facteurs les plus rémunérateurs pour la variable **{categorie}**. On note souvent que les contrats 'Full-Time' et les localisations US dominent le classement.")

    ### 5. Corrélation entre variables 
    st.subheader("🔗 Corrélations entre variables numériques")
    # Sélectionner uniquement les colonnes numériques
    numeric_df = df.select_dtypes(include=[np.number])
    corr_matrix = numeric_df.corr()

    # Affichage du heatmap
    fig_corr, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=ax)
    st.pyplot(fig_corr)
    st.markdown("**Interprétation :** La matrice montre l'intensité du lien entre les variables. Une corrélation proche de 1 entre l'année et le salaire indiquerait une augmentation globale du marché au fil du temps. D'après la matrice de corrélation, on remarque qu'aucune variable de présente de forte corrélation entre elles, elles ont toutes une valeur de corrélation (valeur abosulue des résultats présenté) inférieur à 0.3")

    ### 6. Analyse des variations de salaire (Top 10 postes)
    st.subheader("📅 Évolution des salaires pour les 10 postes les plus fréquents")
    top_10_roles = df['job_title'].value_counts().nlargest(10).index
    df_top10 = df[df['job_title'].isin(top_10_roles)]
    
    df_evolution = df_top10.groupby(['work_year', 'job_title'])['salary_in_usd'].mean().reset_index()
    
    fig_line = px.line(df_evolution, x='work_year', y='salary_in_usd', color='job_title',
                       title="Évolution annuelle du salaire moyen par métier",
                       labels={'work_year': 'Année', 'salary_in_usd': 'Salaire moyen (USD)', 'job_title': 'Métier'})
    st.plotly_chart(fig_line)
    st.markdown("**Interprétation :** On observe globalement une tendance à la hausse, confirmant que la demande en Data Science reste forte d'année en année pour les rôles comme Data Scientist ou Data Engineer.")

    ### 7. Salaire médian par expérience et taille d'entreprise 
    st.subheader("🏢 Salaire médian par expérience et taille d'entreprise")
    df_median = df.groupby(['experience_level', 'company_size'])['salary_in_usd'].median().reset_index()
    
    fig_median = px.bar(df_median, x='experience_level', y='salary_in_usd', color='company_size',
                        barmode='group', title="Impact de la taille d'entreprise sur le salaire médian",
                        labels={'salary_in_usd': 'Salaire médian (USD)', 'experience_level': "Niveau d'expérience", 'company_size': "Taille d'entreprise"})
    st.plotly_chart(fig_median)
    st.markdown("**Interprétation :** En général, les grandes entreprises (L) offrent des salaires plus élevés pour les seniors, mais les PME (S/M) peuvent être compétitives sur les profils juniors pour attirer les talents.")

    ### 8. Ajout de filtres dynamiques 
    st.sidebar.header("⚙️ Filtres de recherche")
    min_sal, max_sal = int(df['salary_in_usd'].min()), int(df['salary_in_usd'].max())
    salary_range = st.sidebar.slider("Sélectionnez une plage de salaire (USD)", min_sal, max_sal, (min_sal, max_sal))
    
    df_filtered = df[(df['salary_in_usd'] >= salary_range[0]) & (df['salary_in_usd'] <= salary_range[1])]

    ### 9. Impact du télétravail sur le salaire selon le pays 
    st.subheader("🏠 Impact du télétravail sur le salaire")
    # On compare les salaires en fonction des ratios de télétravail
    fig_remote = px.strip(df_filtered, x='remote_ratio', y='salary_in_usd', color='experience_level',
                          title="Répartition des salaires selon le taux de télétravail",
                          labels={'remote_ratio': 'Mode de travail', 'salary_in_usd': 'Salaire (USD)', 'experience_level': "Niveau d'expérience"})
    st.plotly_chart(fig_remote)
    st.markdown("**Interprétation :** Le télétravail total (100) n'entraîne pas forcément une baisse de salaire, au contraire, il permet souvent d'accéder à des marchés internationaux mieux rémunérés.")

    ### 10. Filtrage avancé des données 
    st.subheader("🧪 Filtrage ciblé")
    col1, col2 = st.columns(2)
    
    with col1:
        exp_filter = st.multiselect("Sélectionnez le niveau d'expérience", options=df['experience_level'].unique())
    with col2:
        size_filter = st.multiselect("Sélectionnez la taille d'entreprise", options=df['company_size'].unique())
    
   
    final_df = df_filtered.copy()
    if exp_filter:
        final_df = final_df[final_df['experience_level'].isin(exp_filter)]
    if size_filter:
        final_df = final_df[final_df['company_size'].isin(size_filter)]
        
    st.write(f"Nombre de résultats trouvés : {len(final_df)}")
    st.dataframe(final_df)

else:
    st.info("Veuillez charger le fichier de données pour commencer l'analyse.")

#  Analyse du Top 5 Pays 
st.subheader("🥇 Top 5 des pays avec les meilleurs salaires")
# Agrégation par pays
top_5_pays = df.groupby('company_location')['salary_in_usd'].mean().sort_values(ascending=False).head(5).reset_index()
fig_top5 = px.bar(top_5_pays, x='company_location', y='salary_in_usd', 
                  color='salary_in_usd', text_auto='.3s',
                  title="Top 5 des pays (Moyenne en USD)",
                  labels={'salary_in_usd': 'Salaire moyen (USD)', 'company_location': 'Localisation'})
st.plotly_chart(fig_top5)

#  Tableau Croisé Expérience vs Télétravail 
st.subheader("📑 Synthèse : Salaire par Expérience et Mode de Travail")
# Création de la table pivot identique au notebook
pivot = df.pivot_table(values='salary_in_usd', index='experience_level', 
                        columns='remote_ratio', aggfunc='mean').round(0)
st.table(pivot)
st.markdown("**Analyse :** Ce tableau montre que les cadres (Expert) en télétravail total ont les moyennes les plus hautes.")