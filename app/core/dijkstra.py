
import heapq


def dijkstra(grafico, inicio, fim):
 
    distancia = {nó: float("inf") for nó in grafico}
    previa = {nó: None for nó in grafico}
    distancia[inicio] = 0

    visitado = set()
    ordem_visit = []
    eventos = []
    prioridade = [(0, inicio)]

    while prioridade:
        distancia_atual, nó_atual = heapq.heappop(prioridade)

        if nó_atual in visitado:
            continue
        visitado.add(nó_atual)
        ordem_visit.append(nó_atual)
        eventos.append({"tipo": "visita", "no": nó_atual, "distancia": distancia_atual})

        if nó_atual == fim:
            break

        for vizinho, peso in grafico[nó_atual].items():
            if vizinho in visitado:
                continue
            nova_dist = distancia_atual + peso
            aceito = nova_dist < distancia[vizinho]
            eventos.append({
                "tipo": "aresta",
                "de": nó_atual,
                "para": vizinho,
                "peso": peso,
                "nova_distancia": nova_dist,
                "aceito": aceito,
            })
            if aceito:
                distancia[vizinho] = nova_dist
                previa[vizinho] = nó_atual
                heapq.heappush(prioridade, (nova_dist, vizinho))

    if distancia[fim] == float("inf"):
        return None, float("inf"), ordem_visit, eventos

    # reconstrói o caminho mais curto a partir do dicionário de prévias
    path = []
    node = fim
    while node is not None:
        path.append(node)
        node = previa[node]
    path.reverse()

    return path, distancia[fim], ordem_visit, eventos
