import os
import numpy as np
import pandas as pd
import json

with open(os.path.join(os.getcwd(), "data", "herindeling.json")) as f:
  herindeling = json.load(f)

def corrigeer_gemeentelijke_herindeling(uitslag):
    partijen_ = list(set(uitslag.columns).intersection(set(partijen)))

    uitslag["id"] = np.arange(uitslag.shape[0])

    for i, (nieuwe_gemeente, oude_gemeenten) in enumerate(herindeling.items()):
        gid = uitslag.shape[0] + i + 1
        uitslag.loc[uitslag.gemeentenaam.isin(oude_gemeenten + [nieuwe_gemeente]), "id"] = gid
        uitslag.loc[uitslag.gemeentenaam.isin(oude_gemeenten), "gemeentenaam"] = nieuwe_gemeente

    aggregate_dict = {}
    for c in uitslag.columns:
        if c in stemgedrag + partijen_:
            aggregate_dict[c] = np.sum
        elif c == "id":
            continue
        else:
            aggregate_dict[c] = lambda x: x.iloc[0]

    uitslag = uitslag.groupby("id").aggregate(aggregate_dict)

    opheffing_haren = uitslag.loc[uitslag.gemeentenaam == "Haaren", stemgedrag + partijen_] / 4
    for c in stemgedrag + partijen_:
        uitslag.loc[uitslag.gemeentenaam.isin(["Boxtel", "Oisterwijk", "Vught", "Tilburg"]), c] += opheffing_haren[
            c].values

    return (uitslag)

def hernoem_dubbele_gemeentenamen(uitslag):
    uitslag.loc[uitslag.gemeentenaam == "Hengelo", "gemeentenaam"] = "Hengelo (O.)"
    bergen_maastricht = (uitslag.gemeentenaam.str.contains("Bergen") & uitslag.OuderRegioNaam.str.contains("Maastricht"))
    uitslag.loc[bergen_maastricht, "gemeentenaam"] = "Bergen (L.)"
    bergen_denhelder = (uitslag.gemeentenaam.str.contains("Bergen") & uitslag.OuderRegioNaam.str.contains("Den Helder"))
    uitslag.loc[bergen_denhelder, "gemeentenaam"] = "Bergen (NH.)"

    return(uitslag)


# Lees uitslag in
uitslag = pd.read_csv(os.path.join(os.getcwd(), "data", "2017_per_gemeente.csv"), sep=";")
uitslag.rename(columns={"RegioNaam":"gemeentenaam"}, inplace=True)

# Kolommen voor partijstemmen en overige steminformatie
partijen = list(uitslag.loc[:, "VVD":].columns)
stemgedrag = ["Kiesgerechtigden","Opkomst","OngeldigeStemmen","BlancoStemmen","GeldigeStemmen"]

# Lees vorige uitslag in
vorige_uitslag = pd.read_csv(os.path.join(os.getcwd(), "data", "2012_per_gemeente.csv"), sep=";")
vorige_uitslag.rename(columns={"RegioNaam":"gemeentenaam"}, inplace=True)

# Corrigeer voor gemeentelijke herindeling en naamgevingsconventies
uitslag = corrigeer_gemeentelijke_herindeling(uitslag)
uitslag = hernoem_dubbele_gemeentenamen(uitslag)
vorige_uitslag = corrigeer_gemeentelijke_herindeling(vorige_uitslag)
vorige_uitslag = hernoem_dubbele_gemeentenamen(vorige_uitslag)

# Voorbewerking uitslagendata
uitslag_long = pd.melt(uitslag, id_vars=["gemeentenaam"], value_vars=partijen)
uitslag_totaal_stemmen = uitslag_long.groupby("variable").sum().reset_index()
uitslag_totaal_stemmen.columns = ["Partij", "Aantal stemmen"]

verschil_partijen = list(set(partijen).intersection(set(vorige_uitslag.columns)))
nieuwe_partijen = list(set(partijen).difference(set(verschil_partijen)))
verschil = uitslag.set_index("gemeentenaam").loc[:,verschil_partijen].subtract(vorige_uitslag.set_index("gemeentenaam").loc[:,verschil_partijen])
verschil = verschil.join(uitslag.set_index("gemeentenaam").loc[:, nieuwe_partijen])
verschil.reset_index(inplace=True)

uitslag_verschil_long = pd.melt(verschil, id_vars=["gemeentenaam"], value_vars=verschil_partijen+nieuwe_partijen)
uitslag_verschil_stemmen = uitslag_verschil_long.groupby("variable").sum().reset_index()
uitslag_verschil_stemmen.columns = ["Partij", "Verschil stemmen"]