"""Carga y preparación de datos: Microsoft Azure Predictive Maintenance (100 máquinas, 2015)."""

import pandas as pd
import streamlit as st

URL_PDM = (
    "https://raw.githubusercontent.com/ashishpatel26/"
    "Predictive_Maintenance_using_Machine-Learning_Microsoft_Casestudy/master/data/PdM_{}.csv"
)
SENSORES = ["volt", "rotate", "pressure", "vibration"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]


@st.cache_data(show_spinner="Descargando datos de la flota (solo la primera vez)…", ttl=60 * 60 * 24)
def cargar_datos():
    maquinas = pd.read_csv(URL_PDM.format("machines"))
    fallas = pd.read_csv(URL_PDM.format("failures"), parse_dates=["datetime"])
    errores = pd.read_csv(URL_PDM.format("errors"), parse_dates=["datetime"])
    mant = pd.read_csv(URL_PDM.format("maint"), parse_dates=["datetime"])

    errores = errores[errores["datetime"].dt.year == 2015]
    mant = mant[mant["datetime"].dt.year == 2015]

    # La telemetría horaria pesa ~80 MB: se resume a promedio diario por máquina
    # (lo mismo que hace el notebook con resample("D").mean()) para que la app vuele.
    telemetria = pd.read_csv(
        URL_PDM.format("telemetry"),
        parse_dates=["datetime"],
        dtype={"machineID": "int16", **{s: "float32" for s in SENSORES}},
    )
    diario = (
        telemetria.set_index("datetime")
        .groupby("machineID")[SENSORES]
        .resample("D")
        .mean()
        .reset_index()
    )
    return maquinas, fallas, errores, mant, diario


def calcular_tablas(maquinas, fallas, errores, mant):
    """Tablas que alimentan cada panel del dashboard (Paso 1 del notebook)."""
    kpis = {
        "Máquinas": maquinas["machineID"].nunique(),
        "Fallas": len(fallas),
        "Máquinas con falla": fallas["machineID"].nunique(),
        "Errores registrados": len(errores),
        "Reemplazos de componentes": len(mant),
    }

    fallas_comp = fallas["failure"].value_counts().sort_values()

    fallas_mes = (
        fallas.set_index("datetime")["failure"]
        .resample("MS")
        .size()
        .reindex(pd.date_range("2015-01-01", "2015-12-01", freq="MS"), fill_value=0)
    )
    fallas_mes.index = MESES

    flota = maquinas.merge(
        fallas.groupby("machineID").size().rename("fallas"), on="machineID", how="left"
    ).fillna({"fallas": 0})
    flota["fallas"] = flota["fallas"].astype(int)
    fallas_modelo = flota.groupby("model")["fallas"].mean().round(1)
    top10 = flota.sort_values("fallas", ascending=False).head(10)

    return kpis, fallas_comp, fallas_mes, flota, fallas_modelo, top10
