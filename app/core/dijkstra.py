import heapq


def dijkstra(grafico, inicio, fim):
    #menor caminho entr inicio e fim, retorna o caminho, a distância e a ordem de visita dos nós

    distancia = {nó: float("inf") for nó in grafico}
    previa = {nó: None for nó in grafico}
    distancia[inicio] = 0

    visitado = set()
    ordem_visit = []
    prioridade = [(0, inicio)]

    while prioridade:
        distancia_atual, nó_atual = heapq.heappop(prioridade)

        if nó_atual in visitado:
            continue
        visitado.add(nó_atual)
        ordem_visit.append(nó_atual)

        if nó_atual == fim:
            break

        for vizinho, peso in grafico[nó_atual].items():
            if vizinho in visitado:
                continue
            nova_dist = distancia_atual + peso
            if nova_dist < distancia[vizinho]:
                distancia[vizinho] = nova_dist
                previa[vizinho] = nó_atual
                heapq.heappush(prioridade, (nova_dist, vizinho))

    if distancia[fim] == float("inf"):
        return None, float("inf"), ordem_visit

#recontroi o caminho mais curto a partir do dicionário de prévias
    path = []
    node = fim
    while node is not None:
        path.append(node)
        node = previa[node]
    path.reverse()

    return path, distancia[fim], ordem_visit