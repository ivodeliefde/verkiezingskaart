import os
import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static
import folium

from uitslagen import uitslag, uitslag_totaal_stemmen, partijen, stemgedrag, uitslag_verschil_stemmen


st.set_page_config(
    page_title="Verkiezingskaart 2021",
     # page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded")

resultaat = {
    "Grootste Partij" : uitslag_totaal_stemmen.loc[uitslag_totaal_stemmen["Aantal stemmen"] == uitslag_totaal_stemmen["Aantal stemmen"].max(), "Partij"].values[0],
    "Grootste Winnaar" : uitslag_verschil_stemmen.loc[uitslag_verschil_stemmen["Verschil stemmen"] == uitslag_verschil_stemmen["Verschil stemmen"].max(), "Partij"].values[0],
    "Grootste Verliezer" : uitslag_verschil_stemmen.loc[uitslag_verschil_stemmen["Verschil stemmen"] == uitslag_verschil_stemmen["Verschil stemmen"].min(), "Partij"].values[0]
}


gemeenten = gpd.read_file(os.path.join(os.getcwd(), "data", "municipalities_simplified_2.geojson"))
gemeenten = gemeenten.merge(uitslag, on="gemeentenaam")
gemeentenamen = list(gemeenten.gemeentenaam.sort_values())

st.sidebar.write("### Selecteer een partij")
statistiek = st.sidebar.radio(
    "",
    ('Grootste Partij', 'Grootste Winnaar', 'Grootste Verliezer'))

# map_style = st.radio(
#     "",
#     ('Gemeentegrenzen', 'Gemeenten als Cartogram'))

partij = st.sidebar.selectbox(
    'Partij',
    (partijen),
    partijen.index(resultaat[statistiek])
)

st.sidebar.write("### Selecteer een gemeente")
gemeente = st.sidebar.selectbox(
    'Gemeente',
    (gemeentenamen))


st.title("Verkiezingen Tweede Kamer 2021")

st.write(alt.Chart(uitslag_totaal_stemmen, width=1000, height=485).mark_bar().encode(
    x=alt.X('Partij', sort="-y"),
    y='Aantal stemmen',
    color=alt.condition(
        alt.datum.Partij == partij,
        alt.value('red'),
        alt.value('lightgrey')
    )
).configure_axisX(labelAngle=-45))

m = folium.Map(location=[52.35, 5.3878],
               zoom_start=7,
               tiles='https://api.mapbox.com/styles/v1/ivo11235/ckjx01y2e1brw17nqdictt5wk/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiaXZvMTEyMzUiLCJhIjoieV82bFVfNCJ9.G8mrfJOA07edDDj6Bep2bQ',
               attr='© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <a href="https://www.mapbox.com/map-feedback/">(Improve this map)</a>',
               height=485)


choropleth = folium.Choropleth(geo_data = gemeenten,
             data=uitslag,
             columns=['gemeentenaam', f"Percentage {partij}"],
             key_on='feature.properties.gemeentenaam',
             fill_color='YlGnBu',
             bins = list(range(0, 51, 10)),
             fill_opacity=0.5,
             line_opacity=0.2,
             # line_color="black",
             legend_name=f"Percentage stemmen voor {partij} per gemeente.",
             smooth_factor=1).add_to(m)

style_function = lambda x: {
                                    'fillOpacity':0,
                            'lineColor':'#0000ff'}

highlight_gemeente = folium.GeoJson(
        data = gemeenten.loc[gemeenten["gemeentenaam"] == gemeente,:],
        # fill_opacity=0,
        # line_opacity = 1,
        # line_color = "red",
        style_function=style_function,
        smooth_factor=1).add_to(m)

choropleth.geojson.add_child(
    folium.features.GeoJsonTooltip(['gemeentenaam', f'Percentage {partij}'])
)

highlight_gemeente.add_child(
    folium.features.GeoJsonTooltip(['gemeentenaam', f'Percentage {partij}'])
)


folium_static(m)


