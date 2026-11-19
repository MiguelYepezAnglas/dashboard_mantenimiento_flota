# 🛠️ Dashboard de Mantenimiento · Flota 2015

Dashboard interactivo en **Streamlit** para analizar fallas, errores, reemplazos y sensores de una flota de 100 máquinas durante 2015.

> BSG Institute · *Programación en Python para Análisis de Datos en Mantenimiento* · Clase 4 · Docente: **Miguel Yépez**

## ¿Qué responde?

*"Quiero una sola vista que me diga cómo le fue a la flota en 2015: cuántas fallas, de qué componentes, en qué meses, qué modelos y qué máquinas preocupan, y cómo se ven sus sensores antes de fallar."*

| Pestaña | Contenido |
|---|---|
| 📊 Resumen de la flota | KPIs, fallas por componente y por mes, fallas por modelo, top 10 máquinas, antigüedad vs. fallas, sensores de la máquina crítica |
| 🔧 Vista por máquina | Selector de máquina y sensores, fallas marcadas por componente, errores por tipo, reemplazos por componente |
| 📥 Exportar | Excel con tablas resumen, HTML interactivo, PNG y PDF del dashboard estático |
| 💡 Conclusiones | Hallazgos para el gerente de mantenimiento |

En la barra lateral se filtra por **modelo de máquina**; todos los gráficos, títulos y exportaciones se recalculan.

## Datos

[Microsoft Azure Predictive Maintenance](https://www.kaggle.com/datasets/arnabbiswas1/microsoft-azure-predictive-maintenance) (Kaggle), leído desde un repositorio público de GitHub. La telemetría horaria (~80 MB) se resume a promedio diario por máquina al cargar y queda en caché.

## Estructura

```
├── app.py                 # Interfaz Streamlit
├── src/
│   ├── datos.py           # Carga de datos y tablas resumen
│   └── graficos.py        # Gráficos Plotly y exportaciones (HTML, PNG, PDF)
├── .streamlit/config.toml # Tema con los colores del curso
└── requirements.txt
```

## Correr en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publicar en Streamlit Community Cloud

1. Sube esta carpeta a un repositorio de GitHub (público o privado).
2. Entra a [share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub → **Create app**.
3. Elige el repositorio, la rama `main` y el archivo `app.py` → **Deploy**.

La primera carga tarda ~30–60 s mientras descarga la telemetría; después queda en caché.
