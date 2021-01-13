import os
import streamlit as st
import altair as alt
import numpy as np
import pandas as pd
import geopandas as gpd
import pydeck as pdk


st.set_page_config(layout="wide")

uitslag = pd.read_csv(os.path.join(os.getcwd(), "data", "2017_per_gemeente.csv"), sep=";")
partijen = list(uitslag.loc[:, "VVD":].columns)
uitslag_long = pd.melt(uitslag, id_vars=["RegioNaam"], value_vars=partijen)
uitslag_totaal_stemmen = uitslag_long.groupby("variable").sum().reset_index()
uitslag_totaal_stemmen.columns = ["Partij", "Aantal stemmen"]

gemeenten = gpd.read_file(os.path.join(os.getcwd(), "data", "municipalities_simplified_2.geojson"))

col1, col2 = st.beta_columns([4,3])
col3, col4, col5 = st.beta_columns([1,3,3])

with col1:
    st.title("Verkiezingen Tweede Kamer 2021")

    st.write(alt.Chart(uitslag_totaal_stemmen, width=1000, height=400).mark_bar().encode(
        x=alt.X('Partij', sort="-y"),
        y='Aantal stemmen',
    ).configure_axisX(labelAngle=-45))

with col2:

    st.pydeck_chart(
        pdk.Deck(
            height=2000,
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=52,
                longitude=5,
                zoom=6,
                pitch=20,
            ),
            layers=[
                pdk.Layer("GeoJSONLayer",
                          data=gemeenten,
                          id="geojson",
                          opacity=0.8,
                          # stroked=False,
                          # get_polygon="coordinates",
                          # opacity=0.5,
                          # stroked=True,
                          # filled=False,
                          # extruded=True,
                          # wireframe=True,
                          # get_elevation='properties.valuePerSqm / 20',
                          # get_fill_color=None,
                          # get_line_color=[255, 255, 255],
                          # pickable=True
                          ),
            ],
        )
    )


with col3:
    map_statistic = st.radio(
        "",
        ('Grootste Partij', 'Grootste Winnaar', 'Grootste Verliezer'))

    map_style = st.radio(
        "",
        ('Gemeentegrenzen', 'Gemeenten als Cartogram'))

    map_style = st.selectbox(
    'Gemeente',
     (gemeenten.gemeentenaam.sort_values()))