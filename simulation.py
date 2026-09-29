import random
import math

def simulate_scenario(
    simulation_time,
    mean_time_between_failures,
    maintenance_time,
    production_rate,
    machines,
    seed=None
):
    """
    Simula una línea de producción con varias máquinas.
    Cada máquina genera fallas aleatorias y cada falla requiere mantenimiento.
    La producción se calcula mientras la máquina está operativa.
    """
    if seed is not None:
        random.seed(seed)

    total_failures = 0
    total_downtime = 0.0
    total_production = 0.0
    total_available_time = simulation_time * machines
    total_operating_time = 0.0

    machine_results = []

    for machine in range(1, machines + 1):
        t = 0.0
        operating_time = 0.0
        downtime = 0.0
        failures = 0

        while t < simulation_time:
            # Tiempo aleatorio hasta la siguiente falla.
            u = random.random()
            u = max(u, 1e-12)
            time_to_failure = -mean_time_between_failures * math.log(1 - u)

            operating_segment = min(time_to_failure, simulation_time - t)
            operating_time += operating_segment
            t += operating_segment

            if t >= simulation_time:
                break

            # Ocurrió una falla.
            failures += 1
            total_failures += 1

            actual_maintenance = min(maintenance_time, simulation_time - t)
            downtime += actual_maintenance
            t += actual_maintenance

        production = operating_time * production_rate

        total_operating_time += operating_time
        total_downtime += downtime
        total_production += production

        machine_results.append({
            "machine": machine,
            "operating_time": operating_time,
            "downtime": downtime,
            "failures": failures,
            "production": production
        })

    utilization = (
        total_operating_time / total_available_time * 100
        if total_available_time > 0 else 0
    )

    return {
        "production": total_production,
        "downtime": total_downtime,
        "failures": total_failures,
        "utilization": utilization,
        "operating_time": total_operating_time,
        "machines": machines,
        "machine_results": machine_results,
    }


def evaluate_scenario(parameters, repetitions=10):
    """
    Ejecuta varias repeticiones del mismo escenario y devuelve promedios.
    """
    results = []

    for i in range(repetitions):
        result = simulate_scenario(
            simulation_time=parameters["simulation_time"],
            mean_time_between_failures=parameters["mean_time_between_failures"],
            maintenance_time=parameters["maintenance_time"],
            production_rate=parameters["production_rate"],
            machines=parameters["machines"],
            seed=parameters.get("seed", 1000) + i
        )
        results.append(result)

    avg = {
        "production": sum(r["production"] for r in results) / repetitions,
        "downtime": sum(r["downtime"] for r in results) / repetitions,
        "failures": sum(r["failures"] for r in results) / repetitions,
        "utilization": sum(r["utilization"] for r in results) / repetitions,
        "operating_time": sum(r["operating_time"] for r in results) / repetitions,
    }

    return avg
