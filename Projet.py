import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
plan = pd.read_csv('PlanProjet.csv', sep=';')
coast = pd.read_csv('actuel_coast.csv', sep=';')
duration = pd.read_csv('actual_duration.csv', sep=';')
pays = pd.read_csv('country.csv', encoding='latin-1', sep=';')
regions = pd.read_csv('regions.csv', encoding='latin-1', sep=';')
Type = pd.read_csv('type.csv', sep=';')

coast.rename(columns={'Proj_ID': 'Project ID'}, inplace=True)
duration.rename(columns={'Project': 'Project ID'}, inplace=True)

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Analyse AlphaDent",
    page_icon="📊",
    layout="wide"
)

def home():
    st.title("Analyse Project Management Office de AlphaDent")
    st.write("""
    Les objectifs de cette analyse c'est de crée un Dashboard qui contient des visuels afin de suivre l'avancement des projets et les coût, identifier les retards et contrôler les performances, afin que l’équipe puisse mener les actions adéquates tous cela à l'aide de l'application Streamlit.
    """)
    url_image = "https://miro.medium.com/v2/resize:fit:1400/0*5yINw4AB2CojpC0X.png"
    st.image(url_image, use_column_width=True)

def graphique_1():
    st.header("Portail d'introduction de l'analyse")

    merged_data = pd.merge(plan, duration, on=['Project ID', 'Phase'])
    merged_data['Terminé'] = merged_data['Actual_Duration'] >= merged_data['Planned_Duration']
    nbr_de_projet = plan['Project ID'].nunique()
    totale_cout_planifier = plan['Planned_Cost'].sum()
    totale_cout_actuel = coast['Actual_Cost'].sum()
    moyenne_phases_termines = (merged_data['Terminé'].mean()) * 100

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.info(f"Nombre des projets : {nbr_de_projet}")
    with col2:
        st.info(f"Cout planifier: {totale_cout_planifier}")
    with col3:
        st.info(f"Cout actuel: {totale_cout_actuel}")
    with col4:
        st.info(f"Moyenne des phases terminé: {moyenne_phases_termines}%")

    #Nombre de Projets par Pays_camembert
    projets_par_pays = pays['Country'].value_counts()
    projets_par_region = regions['Region'].value_counts()
    fig1 = px.pie(projets_par_pays, names=projets_par_pays.index, values=projets_par_pays.values,
    title='Nombre de Projets par Pays')
    st.plotly_chart(fig1)

    #Nombre de Projets par Region_camembert
    fig2 = px.pie(projets_par_region, names=projets_par_region.index, values=projets_par_region.values,
    title='Nombre de Projets par Région')
    st.plotly_chart(fig2)

    #Durée des Projets
    fig3 = px.bar(plan, x='Project ID', y='Planned_Duration', title='Durée des Projets')
    fig3.update_layout(xaxis_title='Projet ID', yaxis_title='jours')
    st.plotly_chart(fig3)

def graphique_2():
    st.header("Visuels directeur général")

    #coûts planifiés_(1ere_sous_graphe)
    fig1 = px.bar(plan, x='Phase', y='Planned_Cost', color='Phase', title='Coûts Planifiés')
    #coûts réels_(1ere_sous_graphe)
    fig2 = px.bar(coast, x='Phase', y='Actual_Cost', color='Phase', title='Coûts Réels')

    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

    # Fusionner les données
    data = pd.merge(plan, coast, on=['Project ID', 'Phase'])
    data = pd.merge(data, duration, on=['Project ID', 'Phase'])
    data = pd.merge(data, Type, on='Project ID')

    #Nuage de points
    fig = px.scatter(
        data,
        x='Actual_Cost',
        y='Actual_Duration',
        color='Project Type',
        size_max=30,
        opacity=0.7,
        title='Cout actuel en fonction des durées',)
    st.plotly_chart(fig)

    #sélectionner_les_projets_en_alertes
    coast['Difference_Relative'] = (coast['Actual_Cost'] - plan['Planned_Cost']) / plan['Planned_Cost'] * 100
    projets_en_alerte = coast[coast['Difference_Relative'] > 15]

    #Graphique à barres
    fig = px.bar(projets_en_alerte, x='Project ID', y='Difference_Relative',
             labels={'Difference_Relative': 'Difference Relative (%)'},
             title='Projets en alerte avec différence relative de coût > 15%',
             color='Difference_Relative')
    st.plotly_chart(fig)

    #nombre des projets en alertes
    nb_proj_alert = projets_en_alerte['Project ID'].nunique()
    col1 = st.columns(1)
    with col1[0]:
        st.info(f"Le nombre des projets en alertes : {nb_proj_alert}")


def graphique_3():

    #Carte du monde des projets en chaque pays
    #Fusionner_les_données
    data = pd.merge(coast, pays[['Project ID', 'Country']], on='Project ID', how='left')
    data = pd.merge(data, regions[['Country', 'Region']], on='Country', how='left')

    # Calculer les écarts de coût et différence relative
    data['Ecart_Coût'] = data['Actual_Cost'] - plan['Planned_Cost']
    data['Difference_Relative'] = (data['Ecart_Coût'] / plan['Planned_Cost']) * 100

    projets_avec_ecart = data[data['Difference_Relative'] > 15]
    fig = px.choropleth(projets_avec_ecart,
                    locations='Country',
                    locationmode='country names',
                    color='Difference_Relative',
                    color_continuous_scale="Reds",
                    title='Projets en retard dans le monde',)
    st.plotly_chart(fig)

    #Liste des projets en alerte par pays
    #le nombre de projets uniques par pays
    projets_par_pays = projets_avec_ecart.groupby('Country')['Project ID'].nunique().reset_index()
    st.write("Nombre de projets en alerte par pays :")
    st.table(projets_par_pays)

def graphique_4():

    merged_data = pd.merge(coast, pays[['Project ID', 'Country']], on='Project ID', how='left')
    merged_data = pd.merge(merged_data, regions[['Country', 'Region']], on='Country', how='left')

    #Calculer les écarts de coût
    merged_data['Ecart_Coût'] = merged_data['Actual_Cost'] - plan['Planned_Cost']
    merged_data['Difference_Relative'] = (merged_data['Ecart_Coût'] / plan['Planned_Cost']) * 100
    projets_avec_ecart_par_region = merged_data[merged_data['Difference_Relative'] > 15]
    projets_par_region = projets_avec_ecart_par_region.groupby('Region')['Project ID'].nunique().reset_index()

    #Graphique à barres
    fig = px.bar(projets_par_region, x='Region', y='Project ID', color='Region', labels={'Project ID': 'Nombre de projets en alerte', 'Region': 'Région'})
    fig.update_layout(title_text='Nombre de projets en alerte')
    st.plotly_chart(fig)

    # Afficher le nombre de projets en alerte par région
    st.write("Nombre de projets en alerte par région:")
    st.table(projets_par_region)

app_page = st.sidebar.selectbox(
    "Sélectionnez la visualisation",
    ["Accueil", "Portail d'introduction", "Visuels directeur général", "Visuels directeurs pays", "Visuels directeurs régionaux"]
)

# Affichage des pages
if app_page == "Accueil":
    home()
elif app_page == "Portail d'introduction":
    graphique_1()
elif app_page == "Visuels directeur général":
    graphique_2()
elif app_page == "Visuels directeurs pays":
    graphique_3()
elif app_page == "Visuels directeurs régionaux":
    graphique_4()
