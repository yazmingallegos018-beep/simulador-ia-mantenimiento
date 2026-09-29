import streamlit as st
import pandas as pd
import plotly.express as px

from decision import run_decision_process

st.set_page_config(
    page_title="Simulador IA - Mantenimiento",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Simulador inteligente de mantenimiento")
st.caption(
    "Simulación + exploración de escenarios + toma de decisión bajo "
    "objetivos y restricciones definidos por el usuario."
)

st.info(
    "La metodología del proyecto separa la simulación de la interpretación: "
    "el modelo calcula los resultados y el módulo de decisión selecciona un "
    "escenario con base en los criterios establecidos."
)

# -------------------------
# 1. VARIABLES BASE
# -------------------------
st.header("1. Variables del sistema")

col1, col2, col3 = st.columns(3)

with col1:
    simulation_time = st.number_input(
        "Tiempo de simulación (min)",
        min_value=10.0,
        value=480.0,
        step=10.0
    )

    mean_time_between_failures = st.number_input(
        "Tiempo medio entre fallas (min)",
        min_value=1.0,
        value=120.0,
        step=5.0
    )

with col2:
    maintenance_time = st.number_input(
        "Tiempo de mantenimiento (min)",
        min_value=1.0,
        value=30.0,
        step=1.0
    )

    production_rate = st.number_input(
        "Producción (piezas/min)",
        min_value=0.1,
        value=5.0,
        step=0.1
    )

with col3:
    machines = st.number_input(
        "Número de máquinas",
        min_value=1,
        max_value=20,
        value=3,
        step=1
    )

base = {
    "simulation_time": simulation_time,
    "mean_time_between_failures": mean_time_between_failures,
    "maintenance_time": maintenance_time,
    "production_rate": production_rate,
    "machines": machines
}

# -------------------------
# 2. VARIABLES A EXPLORAR
# -------------------------
st.header("2. Variables que la simulación puede modificar")

variable_labels = {
    "mean_time_between_failures": "Tiempo entre fallas",
    "maintenance_time": "Tiempo de mantenimiento",
    "production_rate": "Producción por minuto",
    "machines": "Número de máquinas"
}

selected = []

for key, label in variable_labels.items():
    if st.checkbox(label, value=True, key=f"select_{key}"):
        selected.append(key)

default_ranges = {
    "mean_time_between_failures": (60.0, 240.0, 30.0),
    "maintenance_time": (10.0, 60.0, 10.0),
    "production_rate": (2.0, 10.0, 1.0),
    "machines": (1.0, 5.0, 1.0)
}

ranges = {}

for key in selected:
    label = variable_labels[key]
    dmin, dmax, dstep = default_ranges[key]

    c1, c2, c3 = st.columns(3)

    with c1:
        vmin = st.number_input(
            f"{label} — mínimo",
            min_value=0.1 if key != "machines" else 1.0,
            value=dmin,
            step=dstep,
            key=f"min_{key}"
        )

    with c2:
        vmax = st.number_input(
            f"{label} — máximo",
            min_value=vmin,
            value=max(dmax, vmin),
            step=dstep,
            key=f"max_{key}"
        )

    with c3:
        vstep = st.number_input(
            f"{label} — paso",
            min_value=0.1,
            value=dstep,
            step=dstep,
            key=f"step_{key}"
        )

    ranges[key] = {
        "min": vmin,
        "max": vmax,
        "step": vstep
    }

# -------------------------
# 3. RESTRICCIONES
# -------------------------
st.header("3. Restricciones del sistema")

c1, c2 = st.columns(2)

with c1:
    min_production = st.number_input(
        "Producción mínima aceptable",
        min_value=0.0,
        value=1500.0,
        step=100.0
    )

    min_utilization = st.number_input(
        "Utilización mínima (%)",
        min_value=0.0,
        max_value=100.0,
        value=70.0,
        step=5.0
    )

with c2:
    max_downtime = st.number_input(
        "Tiempo máximo de paro total (min)",
        min_value=0.0,
        value=300.0,
        step=10.0
    )

    max_failures = st.number_input(
        "Número máximo de fallas",
        min_value=0.0,
        value=30.0,
        step=1.0
    )

constraints = {
    "min_production": min_production,
    "max_downtime": max_downtime,
    "min_utilization": min_utilization,
    "max_failures": max_failures
}

# -------------------------
# 4. OBJETIVO
# -------------------------
st.header("4. Objetivo de decisión")

objective = st.selectbox(
    "¿Qué debe priorizar el sistema?",
    [
        "Mayor producción",
        "Menor tiempo de paro",
        "Mayor utilización",
        "Menor número de fallas",
        "Objetivo combinado"
    ]
)

repetitions = st.slider(
    "Repeticiones por escenario",
    min_value=1,
    max_value=50,
    value=10,
    help="Más repeticiones reducen el efecto de la aleatoriedad, pero aumentan el tiempo de cálculo."
)

run = st.button(
    "▶ Ejecutar simulación y tomar decisión",
    type="primary",
    use_container_width=True
)

if run:
    if not selected:
        st.error("Selecciona al menos una variable para explorar.")
        st.stop()

    with st.spinner("Generando escenarios, simulando y evaluando restricciones..."):
        all_rows, feasible_rows, selected_row = run_decision_process(
            base=base,
            selected_variables=selected,
            ranges=ranges,
            constraints=constraints,
            objective=objective,
            repetitions=repetitions
        )

    st.session_state["results"] = all_rows
    st.session_state["feasible"] = feasible_rows
    st.session_state["selected"] = selected_row
    st.session_state["objective"] = objective

if "results" in st.session_state:
    all_rows = st.session_state["results"]
    feasible_rows = st.session_state["feasible"]
    selected_row = st.session_state["selected"]
    objective = st.session_state["objective"]

    st.divider()
    st.header("5. Resultados de la simulación")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Escenarios evaluados", len(all_rows))
    m2.metric("Escenarios factibles", len(feasible_rows))
    m3.metric("Producción máxima", f"{max(r['production'] for r in all_rows):,.0f}")
    m4.metric("Utilización máxima", f"{max(r['utilization'] for r in all_rows):.1f}%")

    df = pd.DataFrame(all_rows)

    display_columns = [
        "scenario",
        "mean_time_between_failures",
        "maintenance_time",
        "production_rate",
        "machines",
        "production",
        "downtime",
        "failures",
        "utilization",
        "feasible"
    ]

    df_display = df[display_columns].copy()

    df_display.columns = [
        "Escenario",
        "Tiempo entre fallas",
        "Mantenimiento",
        "Producción/min",
        "Máquinas",
        "Producción total",
        "Paro total",
        "Fallas",
        "Utilización %",
        "Factible"
    ]

    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------
    # 6. DECISIÓN
    # -------------------------
    st.header("6. Decisión automática")

    if selected_row is None:
        st.warning(
            "No se encontró un escenario que cumpla simultáneamente "
            "todas las restricciones definidas."
        )
        st.write(
            "Puedes ampliar los rangos o modificar las restricciones para "
            "explorar más escenarios factibles."
        )
    else:
        st.success(
            "Se encontró un escenario factible de acuerdo con el objetivo "
            "y las restricciones configuradas."
        )

        selected_df = pd.DataFrame([selected_row])

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "Producción",
            f"{selected_row['production']:,.0f} piezas"
        )

        c2.metric(
            "Tiempo de paro",
            f"{selected_row['downtime']:.1f} min"
        )

        c3.metric(
            "Fallas",
            f"{selected_row['failures']:.1f}"
        )

        c4.metric(
            "Utilización",
            f"{selected_row['utilization']:.1f}%"
        )

        st.subheader("Configuración seleccionada")

        config_cols = [
            "simulation_time",
            "mean_time_between_failures",
            "maintenance_time",
            "production_rate",
            "machines"
        ]

        config = {
            "Tiempo de simulación (min)": selected_row["simulation_time"],
            "Tiempo medio entre fallas (min)": selected_row["mean_time_between_failures"],
            "Tiempo de mantenimiento (min)": selected_row["maintenance_time"],
            "Producción (piezas/min)": selected_row["production_rate"],
            "Número de máquinas": selected_row["machines"]
        }

        st.table(pd.DataFrame([config]))

        st.subheader("Justificación de la decisión")

        if objective == "Objetivo combinado":
            st.write(
                "El sistema seleccionó el escenario factible con mayor "
                "puntuación combinada. La puntuación considera producción, "
                "utilización, reducción del tiempo de paro y reducción del "
                "número de fallas, dentro del conjunto de escenarios simulados."
            )
        else:
            st.write(
                f"El sistema seleccionó, entre los escenarios que cumplen "
                f"las restricciones, el escenario que optimiza el criterio "
                f"seleccionado: **{objective}**."
            )

        st.caption(
            "La decisión depende de las variables, rangos, restricciones, "
            "modelo de simulación y repeticiones configuradas; no representa "
            "una decisión universal fuera de este modelo."
        )

    # -------------------------
    # 7. GRÁFICAS
    # -------------------------
    st.header("7. Visualización")

    chart_df = df.copy()
    chart_df["Estado"] = chart_df["feasible"].map(
        {True: "Factible", False: "No factible"}
    )

    fig1 = px.scatter(
        chart_df,
        x="downtime",
        y="production",
        color="Estado",
        hover_data=[
            "scenario",
            "machines",
            "maintenance_time",
            "mean_time_between_failures",
            "production_rate",
            "utilization"
        ],
        title="Producción vs. tiempo de paro"
    )

    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.scatter(
        chart_df,
        x="failures",
        y="utilization",
        color="Estado",
        hover_data=["scenario", "production", "downtime"],
        title="Fallas vs. utilización"
    )

    st.plotly_chart(fig2, use_container_width=True)

    # -------------------------
    # 8. EXPORTACIÓN
    # -------------------------
    st.header("8. Exportar resultados")

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "⬇ Descargar resultados CSV",
        data=csv,
        file_name="resultados_simulacion_mantenimiento.csv",
        mime="text/csv"
    )

st.divider()
st.caption(
    "Proyecto académico: simulación de paros de línea por fallas y mantenimiento. "
    "El módulo de decisión trabaja sobre resultados generados por el modelo."
)
