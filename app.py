import os
import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import geopandas as gpd
from streamlit_folium import folium_static
import folium

from uitslagen import uitslag, uitslag_totaal_stemmen, partijen, stemgedrag, uitslag_verschil_stemmen


st.set_page_config(layout="wide")

resultaat = {
    "Grootste Partij" : uitslag_totaal_stemmen.loc[uitslag_totaal_stemmen["Aantal stemmen"] == uitslag_totaal_stemmen["Aantal stemmen"].max(), "Partij"].values[0],
    "Grootste Winnaar" : uitslag_verschil_stemmen.loc[uitslag_verschil_stemmen["Verschil stemmen"] == uitslag_verschil_stemmen["Verschil stemmen"].max(), "Partij"].values[0],
    "Grootste Verliezer" : uitslag_verschil_stemmen.loc[uitslag_verschil_stemmen["Verschil stemmen"] == uitslag_verschil_stemmen["Verschil stemmen"].min(), "Partij"].values[0]
}


gemeenten = gpd.read_file(os.path.join(os.getcwd(), "data", "municipalities_simplified_2.geojson"))
gemeenten = gemeenten.merge(uitslag, on="gemeentenaam")

col1, col2 = st.beta_columns([4,3])
col3, col4, col5 = st.beta_columns([1,3,3])

st.write(uitslag)

with col3:
    statistiek = st.radio(
        "",
        ('Grootste Partij', 'Grootste Winnaar', 'Grootste Verliezer'))

    # map_style = st.radio(
    #     "",
    #     ('Gemeentegrenzen', 'Gemeenten als Cartogram'))

    gemeente = st.selectbox(
        'Gemeente',
        (gemeenten.gemeentenaam.sort_values()))

    partij = st.selectbox(
        'Partij',
        (partijen))

with col1:
    st.title("Verkiezingen Tweede Kamer 2021")

    st.write(alt.Chart(uitslag_totaal_stemmen, width=1000, height=485).mark_bar().encode(
        x=alt.X('Partij', sort="-y"),
        y='Aantal stemmen',
        color=alt.condition(
            alt.datum.Partij == resultaat[statistiek],
            alt.value('red'),
            alt.value('lightgrey')
        )
    ).configure_axisX(labelAngle=-45))

with col2:
    m = folium.Map(location=[52.35, 5.3878],
                   zoom_start=7,
                   tiles='https://api.mapbox.com/styles/v1/ivo11235/ckjx01y2e1brw17nqdictt5wk/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiaXZvMTEyMzUiLCJhIjoieV82bFVfNCJ9.G8mrfJOA07edDDj6Bep2bQ',
                   attr='© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <a href="https://www.mapbox.com/map-feedback/">(Improve this map)</a>',
                   height=485)


    choropleth = folium.Choropleth(geo_data = gemeenten,
                 data=uitslag,
                 columns=['gemeentenaam', f"Percentage {resultaat[statistiek]}"],
                 key_on='feature.properties.gemeentenaam',
                 # fill_color='YlGnBu',
                 bins = list(range(0, 51, 10)),
                 # fill_opacity=0.4,
                 line_opacity=0.2,
                 legend_name=resultaat[statistiek],
                 smooth_factor=1).add_to(m)

    # choropleth = folium.GeoJson(
    #         data = gemeenten,
    #         fill_color='YlGnBu',
    #         smooth_factor=1).add_to(m)

    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['gemeentenaam'])
    )

    folium_static(m)


with col4:
    st.write("x")


with col5:
    st.write("x")