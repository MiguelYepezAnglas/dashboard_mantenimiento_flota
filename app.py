"""
Dashboard de mantenimiento · Flota de 100 máquinas · 2015
BSG Institute · Programación en Python para Análisis de Datos en Mantenimiento · Clase 4
Docente: Miguel Yépez
"""

import io

import pandas as pd
import streamlit as st

from src.datos import SENSORES, calcular_tablas, cargar_datos
from src import graficos as g

st.set_page_config(
    page_title="Dashboard de Mantenimiento · Flota 2015",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------------------------------------------------ estilos
st.markdown(
    """
    <style>
    html, body, [class*="css"], .stMarkdown, .stTabs, button, input, select { font-family: Arial, Helvetica, sans-serif; }
    .block-container { padding-top: 3.2rem; padding-bottom: 2rem; max-width: 1400px; }
    .hero { background: linear-gradient(120deg, #2C4290 0%, #3B5BC2 100%); padding: 26px 32px; border-radius: 16px;
            color: white; margin-bottom: 1.2rem; box-shadow: 0 8px 24px rgba(44,66,144,.18); }
    .hero .kicker { font-size: 12px; letter-spacing: 2px; color: #FFB766; font-weight: bold; }
    .hero h1 { font-size: 30px; font-weight: bold; margin: 6px 0 4px 0; color: white; padding: 0; }
    .hero p { font-size: 15px; color: #DDE3F5; margin: 0; }
    .kpi { background: white; border: 1px solid #E5E9F5; border-left: 5px solid #3B5BC2; border-radius: 12px;
           padding: 16px 18px; box-shadow: 0 2px 10px rgba(44,66,144,.06); min-height: 108px; }
    .kpi .valor { font-size: 32px; font-weight: bold; color: #2C4290; line-height: 1.1; }
    .kpi .label { font-size: 13px; color: #4B5563; margin-top: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .kpi.naranja { border-left-color: #FF8600; } .kpi.verde { border-left-color: #159A8A; }
    .kpi.morado { border-left-color: #A2479E; } .kpi.rojo { border-left-color: #D7263D; }
    .seccion { background: #EEF1F8; padding: 12px 20px; border-radius: 10px; margin: 1.4rem 0 .8rem 0; }
    .seccion .paso { color: #FF8600; font-weight: bold; font-size: 11px; letter-spacing: 2px; }
    .seccion .titulo { color: #2C4290; font-weight: bold; font-size: 21px; }
    .hallazgo { background: white; border: 1px solid #E5E9F5; border-radius: 12px; padding: 16px 20px; margin-bottom: 10px; }
    .hallazgo b.num { display: inline-block; background: #FF8600; color: white; border-radius: 50%; width: 26px; height: 26px;
                      text-align: center; line-height: 26px; margin-right: 10px; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] { background: #EEF1F8; border-radius: 10px 10px 0 0; padding: 10px 20px; font-weight: bold; }
    .stTabs [data-baseweb="tab"] p { font-weight: bold; }
    .stTabs [aria-selected="true"] p { color: white !important; }
    .stTabs [aria-selected="true"] { background: #2C4290 !important; color: white !important; }
    div[data-testid="stPlotlyChart"] { background: white; border: 1px solid #E5E9F5; border-radius: 12px; padding: 6px; }
    .pie { text-align: center; color: #6B7280; font-size: 12px; margin-top: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi(col, valor, label, color=""):
    texto = f"{valor:,}" if isinstance(valor, (int,)) else str(valor)
    col.markdown(f'<div class="kpi {color}"><div class="valor">{texto}</div><div class="label">{label}</div></div>',
                 unsafe_allow_html=True)


def seccion(paso, titulo):
    st.markdown(f'<div class="seccion"><div class="paso">{paso}</div><div class="titulo">{titulo}</div></div>',
                unsafe_allow_html=True)


# ------------------------------------------------------------------ datos
maquinas, fallas, errores, mant, diario = cargar_datos()

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("### 🛠️ Flota 2015")
    st.caption("Microsoft Azure Predictive Maintenance · 100 máquinas · telemetría horaria de 4 sensores")
    st.divider()
    modelos_todos = sorted(maquinas["model"].unique())
    modelos = st.multiselect("Modelos de máquina", modelos_todos, default=modelos_todos,
                             help="Filtra todo el dashboard de la flota y las exportaciones.")
    if not modelos:
        st.warning("Selecciona al menos un modelo.")
        st.stop()
    st.divider()
    st.markdown(
        "**Curso:** Programación en Python para Análisis de Datos en Mantenimiento  \n"
        "**Clase 4:** Proyecto intermedio · dashboard  \n"
        "**Docente:** Miguel Yépez"
    )
    st.caption("Construido con Python · pandas · Plotly · Streamlit")

# filtro por modelo
ids = maquinas.loc[maquinas["model"].isin(modelos), "machineID"]
maq_f = maquinas[maquinas["machineID"].isin(ids)]
fal_f = fallas[fallas["machineID"].isin(ids)]
err_f = errores[errores["machineID"].isin(ids)]
man_f = mant[mant["machineID"].isin(ids)]

kpis, fallas_comp, fallas_mes, flota, fallas_modelo, top10 = calcular_tablas(maq_f, fal_f, err_f, man_f)

maq_top = int(top10.iloc[0]["machineID"])
vib_top = diario[diario["machineID"] == maq_top].set_index("datetime")["vibration"]
fallas_top = fal_f[(fal_f["machineID"] == maq_top) & (fal_f["failure"] == "comp4")]

# ------------------------------------------------------------------ encabezado
filtro_txt = "toda la flota" if len(modelos) == len(modelos_todos) else ", ".join(modelos)
st.markdown(
    f"""
    <div class="hero">
      <div class="kicker">BSG INSTITUTE · PYTHON PARA ANÁLISIS DE DATOS EN MANTENIMIENTO</div>
      <h1>Dashboard de mantenimiento · Flota 2015</h1>
      <p>¿Cuántas fallas, de qué componentes, en qué meses, qué modelos y qué máquinas preocupan? · Vista: <b>{filtro_txt}</b></p>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_flota, tab_maquina, tab_export, tab_concl = st.tabs(
    ["📊  Resumen de la flota", "🔧  Vista por máquina", "📥  Exportar", "💡  Conclusiones"]
)

# ================================================================== FLOTA
with tab_flota:
    c = st.columns(5)
    kpi(c[0], kpis["Máquinas"], "Máquinas")
    kpi(c[1], kpis["Fallas"], "Fallas", "rojo")
    kpi(c[2], kpis["Máquinas con falla"], "Máquinas con falla", "naranja")
    kpi(c[3], kpis["Errores registrados"], "Errores registrados", "morado")
    kpi(c[4], kpis["Reemplazos de componentes"], "Reemplazos", "verde")

    seccion("¿QUÉ FALLA Y CUÁNDO?", "Componentes y estacionalidad")
    c1, c2 = st.columns([1, 2])
    c1.plotly_chart(g.fig_componentes(fallas_comp), width="stretch")
    c2.plotly_chart(g.fig_mensual(fallas_mes), width="stretch")

    seccion("¿QUIÉN PREOCUPA?", "Modelos, máquinas críticas y antigüedad")
    c1, c2, c3 = st.columns(3)
    c1.plotly_chart(g.fig_modelos(fallas_modelo), width="stretch")
    c2.plotly_chart(g.fig_top10(top10), width="stretch")
    c3.plotly_chart(g.fig_edad(flota), width="stretch")

    seccion("¿HAY SEÑALES ANTES DE FALLAR?", f"Máquina {maq_top} · la que más falla")
    fig_vib = g.fig_maquina(diario[diario["machineID"] == maq_top], fal_f[fal_f["machineID"] == maq_top],
                            maquinas.set_index("machineID").loc[maq_top], maq_top, sensores=["vibration", "pressure"])
    st.plotly_chart(fig_vib, width="stretch")
    st.caption("Cada línea vertical es una falla, coloreada por componente. Explora todas las máquinas en la pestaña "
               "**Vista por máquina**.")

    with st.expander("Ver tabla de la flota"):
        st.dataframe(
            flota.sort_values("fallas", ascending=False),
            width="stretch", hide_index=True,
            column_config={
                "machineID": st.column_config.NumberColumn("Máquina", format="%d"),
                "model": "Modelo",
                "age": st.column_config.NumberColumn("Antigüedad (años)"),
                "fallas": st.column_config.ProgressColumn("Fallas 2015", min_value=0,
                                                          max_value=int(flota["fallas"].max()), format="%d"),
            },
        )

# ================================================================== MÁQUINA
with tab_maquina:
    c1, c2 = st.columns([1, 3])
    opciones = sorted(maquinas["machineID"])
    id_maq = c1.selectbox("Máquina", opciones, index=opciones.index(99),
                          format_func=lambda m: f"Máquina {m}")
    sensores = c2.multiselect("Sensores", SENSORES, default=SENSORES)

    info = maquinas.set_index("machineID").loc[id_maq]
    ev = fallas[fallas["machineID"] == id_maq]
    er = errores[errores["machineID"] == id_maq]
    mn = mant[mant["machineID"] == id_maq]

    c = st.columns(5)
    kpi(c[0], info["model"], "Modelo")
    kpi(c[1], f"{info['age']} años", "Antigüedad", "verde")
    kpi(c[2], len(ev), "Fallas en 2015", "rojo")
    kpi(c[3], len(er), "Errores registrados", "morado")
    kpi(c[4], len(mn), "Reemplazos", "naranja")

    st.write("")
    if sensores:
        st.plotly_chart(g.fig_maquina(diario[diario["machineID"] == id_maq], ev, info, id_maq, sensores),
                        width="stretch")
    else:
        st.info("Selecciona al menos un sensor.")

    c1, c2 = st.columns(2)
    c1.plotly_chart(g.fig_barras_simple(er["errorID"].value_counts().sort_index(), "Errores por tipo", g.MORADO,
                                        "Errores"), width="stretch")
    c2.plotly_chart(g.fig_barras_simple(mn["comp"].value_counts().sort_index(), "Reemplazos por componente",
                                        g.VERDE, "Reemplazos"), width="stretch")

    with st.expander(f"Fallas de la máquina {id_maq}"):
        st.dataframe(ev.rename(columns={"datetime": "Fecha y hora", "machineID": "Máquina", "failure": "Componente"}),
                     width="stretch", hide_index=True)

# ================================================================== EXPORTAR
with tab_export:
    st.markdown("Descarga el dashboard y las tablas resumen con el filtro actual "
                f"(**{filtro_txt}**). Igual que en el Paso 5 del notebook.")

    @st.cache_data(show_spinner="Generando archivos…")
    def exportables(modelos_sel):
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as excel:
            pd.Series(kpis, name="valor").to_excel(excel, sheet_name="kpis")
            fallas_comp.rename("fallas").to_excel(excel, sheet_name="fallas_componente")
            fallas_mes.rename("fallas").to_excel(excel, sheet_name="fallas_mes")
            flota.sort_values("fallas", ascending=False).to_excel(excel, sheet_name="flota", index=False)
        args = (kpis, fallas_comp, fallas_mes, fallas_modelo, top10, vib_top, fallas_top, maq_top)
        return (buffer.getvalue(), g.html_dashboard(*args),
                g.imagen_dashboard(*args, formato="png"), g.imagen_dashboard(*args, formato="pdf"))

    xlsx, html, png, pdf = exportables(tuple(modelos))

    c = st.columns(4)
    c[0].download_button("📗  Excel · tablas resumen", xlsx, "resumen_flota_2015.xlsx",
                         "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
    c[1].download_button("🌐  HTML · interactivo", html, "dashboard_flota_2015.html", "text/html",
                         width="stretch")
    c[2].download_button("🖼️  PNG · estático", png, "dashboard_flota_2015.png", "image/png", width="stretch")
    c[3].download_button("📄  PDF · estático", pdf, "dashboard_flota_2015.pdf", "application/pdf",
                         width="stretch")

    seccion("VISTA PREVIA", "Dashboard estático (Matplotlib)")
    st.image(png, width="stretch")

# ================================================================== CONCLUSIONES
with tab_concl:
    st.markdown("Un dashboard sin conclusiones es solo decoración. **Para toda la flota 2015:**")
    hallazgos = [
        "<b>comp2</b> es el componente que más falla (259 de 761): revisar su plan preventivo y el stock de repuestos.",
        "<b>Enero</b> concentra más fallas (94); el resto del año se mantiene entre 50 y 69, sin estacionalidad clara.",
        "<b>model1</b> tiene el doble de fallas por máquina que model4, y las máquinas más antiguas fallan más: "
        "priorizar inspecciones por modelo y antigüedad.",
        "Hay máquinas con muchas más fallas que el promedio (la <b>99</b> tiene 19): candidatas a análisis de causa "
        "raíz (RCA).",
        "Cada componente deja huella en un sensor antes de fallar (<b>comp4</b> en la vibración, <b>comp3</b> en la "
        "presión): en la Clase 5 aprenderemos a detectarlo automáticamente.",
    ]
    for i, h in enumerate(hallazgos, start=1):
        st.markdown(f'<div class="hallazgo"><b class="num">{i}</b>{h}</div>', unsafe_allow_html=True)

st.markdown('<div class="pie">BSG Institute · Programación en Python para Análisis de Datos en Mantenimiento · '
            'Docente: Miguel Yépez</div>', unsafe_allow_html=True)
