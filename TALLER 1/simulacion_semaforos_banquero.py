"""
Simulación de una vía en cruz con 4 nodos/hilos y algoritmo del banquero.

Caso solicitado:
- 50 vehículos: A -> B
- 35 vehículos: B -> A
- 100 vehículos: D -> C (subiendo, por accidente)
- 20 vehículos: C -> D (bajando)
- 30 segundos por vehículo al cruzar.

Modelo:
- A, B, C y D son nodos y cada nodo es un hilo Python.
- El cruce central es un recurso compartido de capacidad 1.
- Con Banquero: antes de conceder el recurso se ejecuta la prueba de
  estado seguro del algoritmo del banquero.
- Sin Banquero: se usa disciplina FIFO sobre el recurso, sin prueba
  de estado seguro.
- El tiempo es VIRTUAL para que el programa termine inmediatamente:
  cada vehículo suma 30 segundos al reloj simulado. No se usa sleep(30).

Ejecutar:
    python simulacion_semaforos_banquero.py
"""

import threading
from collections import defaultdict

FLOWS = {
    "A->B": ("A", "B", 50),
    "B->A": ("B", "A", 35),
    "D->C": ("D", "C", 100),
    "C->D": ("C", "D", 20),
}
ORDER = ["A->B", "B->A", "D->C", "C->D"]
SERVICE_SECONDS = 30


def simulate(use_banker=True, accident=True):
    remaining = {
        "A->B": 50,
        "B->A": 35,
        "D->C": 100 if accident else 0,
        "C->D": 20,
    }
    completed = {f: 0 for f in FLOWS}
    finish = defaultdict(list)

    lock = threading.Lock()
    cv = threading.Condition(lock)

    # Recurso compartido: el cruce central.
    available = 1

    # Estado de Banquero: 1 recurso.
    allocation = {n: 0 for n in "ABCD"}
    max_claim = {n: 1 for n in "ABCD"}

    pending = []
    pending_set = set()
    virtual_time = 0
    node_load = {n: 0 for n in "ABCD"}
    events = []

    def banker_safe_after_grant(node):
        """Prueba de seguridad del algoritmo del banquero."""
        work = available
        alloc = allocation.copy()
        need = {n: max_claim[n] - alloc[n] for n in "ABCD"}

        if work < 1:
            return False

        # Simular concesión.
        work -= 1
        alloc[node] += 1
        need[node] -= 1

        done = {n: False for n in "ABCD"}

        changed = True
        while changed:
            changed = False
            for n in "ABCD":
                if not done[n] and need[n] <= work:
                    work += alloc[n]
                    done[n] = True
                    changed = True

        return all(done.values())

    def choose_next():
        if not pending:
            return None

        # Sin Banquero: FIFO.
        if not use_banker:
            return pending[0]

        # Con Banquero: primera solicitud cuyo estado sea seguro.
        for flow in pending:
            node = FLOWS[flow][0]
            if banker_safe_after_grant(node):
                return flow

        return None

    def node_worker(node):
        nonlocal available, virtual_time

        while True:
            with cv:
                own = [
                    f for f, (src, _, _) in FLOWS.items()
                    if src == node and remaining[f] > 0
                ]
                if not own:
                    return

                flow = own[0]

                if flow not in pending_set:
                    pending.append(flow)
                    pending_set.add(flow)
                    events.append((virtual_time, "REQUEST", flow, node))

                while True:
                    selected = choose_next()
                    if selected == flow and available == 1:
                        pending.remove(flow)
                        pending_set.remove(flow)
                        available = 0
                        allocation[node] = 1
                        events.append((virtual_time, "GRANT", flow, node))
                        break
                    cv.wait()

                # El vehículo cruza en 30 s de tiempo simulado.
                start = virtual_time
                virtual_time += SERVICE_SECONDS
                end = virtual_time

                remaining[flow] -= 1
                completed[flow] += 1
                finish[flow].append(end)
                node_load[node] += SERVICE_SECONDS
                events.append((end, "PASS", flow, node))

                # Liberación del recurso.
                allocation[node] = 0
                available = 1
                cv.notify_all()

    threads = [
        threading.Thread(target=node_worker, args=(node,), name=f"Nodo-{node}")
        for node in "ABCD"
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total = sum(completed.values())
    makespan = virtual_time

    print("=" * 70)
    print("SIMULACIÓN DE SEMÁFOROS - ALGORITMO DEL BANQUERO")
    print("=" * 70)
    print(f"Algoritmo: {'BANQUERO' if use_banker else 'SIN BANQUERO'}")
    print(f"Accidente: {'SÍ' if accident else 'NO'}")
    print(f"Vehículos procesados: {total}")
    print(f"Tiempo total: {makespan} s = {makespan/60:.2f} min")
    print(f"Rendimiento: {total/(makespan/60):.2f} vehículos/min")
    print("-" * 70)
    print(f"{'Sentido':<10}{'Solicitados':>14}{'Pasaron':>12}{'Tiempo (s)':>14}{'Fin (s)':>12}")
    for flow in ORDER:
        requested = 100 if flow == "D->C" and accident else FLOWS[flow][2] if flow != "D->C" else 0
        print(
            f"{flow:<10}{requested:>14}{completed[flow]:>12}"
            f"{completed[flow]*SERVICE_SECONDS:>14}"
            f"{(finish[flow][-1] if finish[flow] else 0):>12}"
        )

    print("-" * 70)
    print("Carga de los hilos (tiempo de trabajo simulado):")
    for node in "ABCD":
        print(f"  Nodo {node}: {node_load[node]} s = {node_load[node]/60:.2f} min")

    print("\nPrimeros 12 eventos:")
    for e in events[:12]:
        print(f"  t={e[0]:>5} s | {e[1]:<7} | {e[2]:<5} | hilo {e[3]}")

    return {
        "completed": completed,
        "makespan": makespan,
        "node_load": node_load,
        "events": events,
    }


if __name__ == "__main__":
    print("\n*** CASO CON ACCIDENTE ***")
    simulate(use_banker=True, accident=True)

    print("\n*** CASO CON ACCIDENTE, SIN BANQUERO ***")
    simulate(use_banker=False, accident=True)
