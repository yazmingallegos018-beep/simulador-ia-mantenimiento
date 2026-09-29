import itertools
from simulation import evaluate_scenario


OBJECTIVES = {
    "Mayor producción": "production",
    "Menor tiempo de paro": "downtime",
    "Mayor utilización": "utilization",
    "Menor número de fallas": "failures",
}


def generate_values(minimum, maximum, step):
    values = []
    value = minimum

    while value <= maximum + 1e-9:
        values.append(value)
        value += step

    return values


def generate_scenarios(base, selected_variables, ranges):
    """
    Genera escenarios combinando únicamente las variables seleccionadas.
    """
    variable_values = {}

    for variable in selected_variables:
        r = ranges[variable]
        vals = generate_values(r["min"], r["max"], r["step"])

        # Las máquinas deben ser enteros.
        if variable == "machines":
            vals = sorted(set(int(round(v)) for v in vals if int(round(v)) >= 1))

        variable_values[variable] = vals

    if not selected_variables:
        return [base.copy()]

    scenarios = []

    for combination in itertools.product(
        *[variable_values[v] for v in selected_variables]
    ):
        scenario = base.copy()

        for variable, value in zip(selected_variables, combination):
            scenario[variable] = value

        scenarios.append(scenario)

    return scenarios


def satisfies_constraints(result, constraints):
    return (
        result["production"] >= constraints["min_production"]
        and result["downtime"] <= constraints["max_downtime"]
        and result["utilization"] >= constraints["min_utilization"]
        and result["failures"] <= constraints["max_failures"]
    )


def normalize(values, reverse=False):
    """
    Normalización 0-1 para combinar criterios.
    """
    if not values:
        return []

    low = min(values)
    high = max(values)

    if abs(high - low) < 1e-12:
        normalized = [1.0 for _ in values]
    else:
        normalized = [(v - low) / (high - low) for v in values]

    if reverse:
        normalized = [1 - v for v in normalized]

    return normalized


def choose_scenario(evaluated):
    """
    Selecciona el escenario según el objetivo definido por el usuario.
    No declara que sea universalmente mejor: es el mejor dentro del
    conjunto simulado y bajo las restricciones seleccionadas.
    """
    objective = evaluated["objective"]
    rows = evaluated["feasible"]

    if not rows:
        return None

    if objective == "Mayor producción":
        return max(rows, key=lambda x: x["production"])

    if objective == "Menor tiempo de paro":
        return min(rows, key=lambda x: x["downtime"])

    if objective == "Mayor utilización":
        return max(rows, key=lambda x: x["utilization"])

    if objective == "Menor número de fallas":
        return min(rows, key=lambda x: x["failures"])

    # Objetivo combinado:
    prod = normalize([r["production"] for r in rows])
    util = normalize([r["utilization"] for r in rows])
    down = normalize([r["downtime"] for r in rows], reverse=True)
    fail = normalize([r["failures"] for r in rows], reverse=True)

    for i, row in enumerate(rows):
        row["decision_score"] = (
            0.40 * prod[i]
            + 0.30 * util[i]
            + 0.20 * down[i]
            + 0.10 * fail[i]
        )

    return max(rows, key=lambda x: x["decision_score"])


def run_decision_process(base, selected_variables, ranges, constraints, objective, repetitions=10):
    scenarios = generate_scenarios(base, selected_variables, ranges)

    evaluated_rows = []

    for index, scenario in enumerate(scenarios, start=1):
        result = evaluate_scenario(
            scenario,
            repetitions=repetitions
        )

        row = {
            "scenario": index,
            **scenario,
            **result,
            "feasible": satisfies_constraints(result, constraints)
        }

        evaluated_rows.append(row)

    feasible = [r for r in evaluated_rows if r["feasible"]]

    package = {
        "all": evaluated_rows,
        "feasible": feasible,
        "objective": objective
    }

    selected = choose_scenario(package)

    return evaluated_rows, feasible, selected
