"""Gráficos del dashboard: Plotly (interactivo) y Matplotlib (exportación PNG/PDF)."""

import io

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.datos import SENSORES

# Paleta del curso (misma del notebook)
AZUL, NARANJA, VERDE, MORADO, ROJO = "#3B5BC2", "#E07800", "#159A8A", "#A2479E", "#D7263D"
AZUL_OSCURO, GRIS = "#2C4290", "#4B5563"
COLOR_COMP = {"comp1": AZUL, "comp2": NARANJA, "comp3": VERDE, "comp4": MORADO}
FUENTE = "Arial, Helvetica, sans-serif"


def _estilo(fig, titulo, alto=380):
    fig.update_layout(
        title=dict(text=f"<b>{titulo}</b>", font=dict(size=15, color=AZUL_OSCURO), x=0, xanchor="left"),
        template="plotly_white",
        height=alto,
        margin=dict(l=10, r=10, t=55, b=10),
        font=dict(family=FUENTE, color=GRIS),
        showlegend=False,
        hoverlabel=dict(font_family=FUENTE),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ---------- Paneles de la flota ----------

def fig_componentes(fallas_comp):
    top = fallas_comp.idxmax() if len(fallas_comp) else "-"
    fig = go.Figure(go.Bar(
        x=fallas_comp.values, y=fallas_comp.index, orientation="h", text=fallas_comp.values,
        textposition="outside", cliponaxis=False, marker_color=[NARANJA if c == top else AZUL for c in fallas_comp.index],
        hovertemplate="%{y}: %{x} fallas<extra></extra>",
    ))
    fig.update_xaxes(range=[0, (fallas_comp.max() if len(fallas_comp) else 1) * 1.22], title="Fallas")
    return _estilo(fig, f"{top} es el componente que más falla")


def fig_mensual(fallas_mes):
    mes_max = fallas_mes.idxmax()
    fig = go.Figure(go.Scatter(
        x=fallas_mes.index, y=fallas_mes.values, mode="lines+markers+text", text=fallas_mes.values,
        textposition="top center", line=dict(color=AZUL, width=3), marker=dict(size=9),
        fill="tozeroy", fillcolor="rgba(59,91,194,0.08)",
        hovertemplate="%{x}: %{y} fallas<extra></extra>", cliponaxis=False,
    ))
    fig.update_xaxes(range=[-0.4, len(fallas_mes) - 0.6])
    fig.update_yaxes(range=[0, max(fallas_mes.max(), 1) * 1.25], title="Fallas")
    return _estilo(fig, f"{mes_max} es el mes con más fallas ({fallas_mes.max()})")


def fig_modelos(fallas_modelo):
    peor, mejor = fallas_modelo.idxmax(), fallas_modelo.idxmin()
    titulo = (f"{peor} falla {fallas_modelo.max() / fallas_modelo.min():.1f}× más que {mejor}"
              if len(fallas_modelo) > 1 and fallas_modelo.min() > 0 else "Fallas por máquina, según modelo")
    fig = go.Figure(go.Bar(
        x=fallas_modelo.index, y=fallas_modelo.values, text=fallas_modelo.values, textposition="outside", cliponaxis=False,
        marker_color=VERDE, hovertemplate="%{x}: %{y} fallas por máquina<extra></extra>",
    ))
    fig.update_yaxes(range=[0, fallas_modelo.max() * 1.2], title="Fallas por máquina")
    return _estilo(fig, titulo)


def fig_top10(top10):
    datos = top10.iloc[::-1]
    fig = go.Figure(go.Bar(
        x=datos["fallas"], y="Máq. " + datos["machineID"].astype(str), orientation="h",
        text=datos["fallas"], textposition="outside", cliponaxis=False, marker_color=NARANJA,
        customdata=datos[["model", "age"]],
        hovertemplate="%{y} · %{customdata[0]} · %{customdata[1]} años<br>%{x} fallas<extra></extra>",
    ))
    fig.update_xaxes(range=[0, datos["fallas"].max() * 1.18], title="Fallas")
    return _estilo(fig, "Top 10 máquinas con más fallas")


def fig_edad(flota):
    fig = go.Figure(go.Scatter(
        x=flota["age"], y=flota["fallas"], mode="markers",
        marker=dict(size=10, color=AZUL, opacity=0.6, line=dict(color="white", width=1)),
        customdata=flota[["machineID", "model"]],
        hovertemplate="Máq. %{customdata[0]} · %{customdata[1]}<br>%{x} años · %{y} fallas<extra></extra>",
    ))
    fig.update_xaxes(title="Antigüedad (años)")
    fig.update_yaxes(title="Fallas en 2015")
    return _estilo(fig, "Antigüedad vs. fallas por máquina")


# ---------- Vista por máquina ----------

def fig_maquina(diario_maq, eventos, info, id_maquina, sensores=SENSORES):
    fig = make_subplots(rows=len(sensores), cols=1, shared_xaxes=True, vertical_spacing=0.05,
                        subplot_titles=sensores)
    for i, sensor in enumerate(sensores, start=1):
        fig.add_trace(go.Scatter(x=diario_maq["datetime"], y=diario_maq[sensor], line=dict(color=GRIS, width=1.4),
                                 showlegend=False, hovertemplate="%{x|%d %b}: %{y:.1f}<extra>" + sensor + "</extra>"),
                      row=i, col=1)
    for _, fila in eventos.iterrows():
        fig.add_vline(x=fila["datetime"], line_color=COLOR_COMP[fila["failure"]], line_width=2, row="all", col=1)
    for comp, color in COLOR_COMP.items():
        fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=color, width=3), name=comp))
    fig.update_layout(
        height=190 * len(sensores) + 80, template="plotly_white", font=dict(family=FUENTE, color=GRIS),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, x=1, xanchor="right", title_text="Falla de: "),
        margin=dict(l=10, r=10, t=100, b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        title=dict(text=f"<b>Máquina {id_maquina}</b> · {info['model']} · {info['age']} años · "
                        f"{len(eventos)} fallas en 2015", font=dict(size=16, color=AZUL_OSCURO)),
    )
    return fig


def fig_barras_simple(serie, titulo, color, eje="Cantidad"):
    fig = go.Figure(go.Bar(x=serie.index, y=serie.values, text=serie.values, textposition="outside", cliponaxis=False,
                           marker_color=color))
    fig.update_yaxes(range=[0, max(serie.max(), 1) * 1.25], title=eje)
    return _estilo(fig, titulo, alto=320)


# ---------- Exportables ----------

def html_dashboard(kpis, fallas_comp, fallas_mes, fallas_modelo, top10, vib, fallas_maq, maq):
    """Dashboard interactivo completo en un solo HTML (Paso 3 del notebook)."""
    tarjetas = [("Fallas", kpis["Fallas"]), ("Máquinas con falla", kpis["Máquinas con falla"]),
                ("Errores registrados", kpis["Errores registrados"])]
    fig = make_subplots(
        rows=3, cols=3, row_heights=[0.16, 0.42, 0.42], vertical_spacing=0.1, horizontal_spacing=0.08,
        specs=[[{"type": "indicator"}] * 3, [{}, {"colspan": 2}, None], [{}, {}, {}]],
        subplot_titles=["", "", "", "Fallas por componente", "Fallas por mes", "Fallas por máquina, según modelo",
                        "Top 10 máquinas con más fallas", f"Vibración diaria · máquina {maq} (x roja = falla comp4)"])
    for i, (titulo, valor) in enumerate(tarjetas):
        fig.add_trace(go.Indicator(mode="number", value=valor, title=titulo, number_font_color=AZUL_OSCURO),
                      row=1, col=i + 1)
    fig.add_trace(go.Bar(x=fallas_comp.values, y=fallas_comp.index, orientation="h", text=fallas_comp.values,
                         marker_color=AZUL), row=2, col=1)
    fig.add_trace(go.Scatter(x=fallas_mes.index, y=fallas_mes.values, mode="lines+markers+text", text=fallas_mes.values,
                             textposition="top center", line_color=AZUL), row=2, col=2)
    fig.add_trace(go.Bar(x=fallas_modelo.index, y=fallas_modelo.values, text=fallas_modelo.values,
                         marker_color=VERDE), row=3, col=1)
    fig.add_trace(go.Bar(x=top10["fallas"][::-1], y="Máq. " + top10["machineID"].astype(str)[::-1],
                         orientation="h", marker_color=NARANJA), row=3, col=2)
    fig.add_trace(go.Scatter(x=vib.index, y=vib.values, line_color=AZUL), row=3, col=3)
    dias = fallas_maq["datetime"].dt.normalize()
    fig.add_trace(go.Scatter(x=dias, y=vib.reindex(dias), mode="markers",
                             marker=dict(color=ROJO, size=10, symbol="x")), row=3, col=3)
    fig.update_layout(height=950, showlegend=False, template="plotly_white", font_family=FUENTE,
                      title=dict(text="<b>Dashboard de mantenimiento · Flota 2015</b>", font_size=22))
    fig.update_yaxes(range=[0, fallas_mes.max() * 1.25], row=2, col=2)
    return fig.to_html(include_plotlyjs="cdn").encode("utf-8")


def imagen_dashboard(kpis, fallas_comp, fallas_mes, fallas_modelo, top10, vib, fallas_maq, maq, formato="png"):
    """Dashboard estático con Matplotlib (Paso 2 del notebook) → bytes PNG o PDF."""
    plt.rcParams.update({"font.family": "sans-serif", "axes.titleweight": "bold", "axes.titlelocation": "left",
                         "axes.spines.top": False, "axes.spines.right": False})
    fig = plt.figure(figsize=(18, 11))
    grid = fig.add_gridspec(3, 3, height_ratios=[0.4, 1, 1], hspace=0.45, wspace=0.28)
    fig.suptitle("Dashboard de mantenimiento · Flota 2015", fontsize=20, fontweight="bold",
                 x=0.06, ha="left", color=AZUL_OSCURO)

    tarjetas = [("Fallas", kpis["Fallas"]), ("Máquinas con falla", kpis["Máquinas con falla"]),
                ("Errores registrados", kpis["Errores registrados"])]
    for i, (titulo, valor) in enumerate(tarjetas):
        ax = fig.add_subplot(grid[0, i])
        ax.axis("off")
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, color="#EEF1F8"))
        ax.text(0.06, 0.55, f"{valor:,}", fontsize=32, fontweight="bold", color=AZUL_OSCURO, transform=ax.transAxes)
        ax.text(0.06, 0.18, titulo, fontsize=13, color=GRIS, transform=ax.transAxes)

    ax1 = fig.add_subplot(grid[1, 0])
    ax1.barh(fallas_comp.index, fallas_comp.values, color=AZUL)
    for i, v in enumerate(fallas_comp.values):
        ax1.text(v + 3, i, v, va="center")
    ax1.set_title(f"{fallas_comp.idxmax()} es el componente que más falla")

    ax2 = fig.add_subplot(grid[1, 1:])
    ax2.plot(fallas_mes.index, fallas_mes.values, marker="o", color=AZUL, linewidth=2)
    for x, y in zip(fallas_mes.index, fallas_mes.values):
        ax2.text(x, y + 2, y, ha="center")
    ax2.set_ylim(0, fallas_mes.max() * 1.25)
    ax2.set_title(f"{fallas_mes.idxmax()} es el mes con más fallas")

    ax3 = fig.add_subplot(grid[2, 0])
    ax3.bar(fallas_modelo.index, fallas_modelo.values, color=VERDE)
    ax3.set_title("Fallas por máquina, según modelo")
    ax3.set_ylabel("Fallas por máquina")

    ax4 = fig.add_subplot(grid[2, 1])
    ax4.barh("Máq. " + top10["machineID"].astype(str)[::-1], top10["fallas"][::-1], color=NARANJA)
    ax4.set_title("Top 10 máquinas con más fallas")
    ax4.set_xlabel("Fallas")

    ax5 = fig.add_subplot(grid[2, 2])
    ax5.plot(vib.index, vib.values, color=AZUL, linewidth=1.2)
    for f in fallas_maq["datetime"]:
        ax5.axvline(f, color=ROJO, linestyle="--", linewidth=1)
    ax5.set_title(f"Máquina {maq}: vibración diaria y fallas comp4")
    ax5.tick_params(axis="x", rotation=30)

    buffer = io.BytesIO()
    fig.savefig(buffer, format=formato, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return buffer.getvalue()
