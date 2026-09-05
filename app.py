from flask import Flask
import heapq

app = Flask(__name__)

#nós das cidade e arestas com as dintacias em km

CIDADE = {
    "Brasília":               {"lat": -15.7801, "lon": -47.9292},
    "Goiânia":                {"lat": -16.6869, "lon": -49.2648},
    "Anápolis":               {"lat": -16.3281, "lon": -48.9530},
    "Aparecida de Goiânia":   {"lat": -16.8233, "lon": -49.2437},
    "Trindade":               {"lat": -16.6499, "lon": -49.4889},
    "Luziânia":               {"lat": -16.2525, "lon": -47.9500},
    "Valparaíso de Goiás":    {"lat": -16.0653, "lon": -47.9761},
    "Formosa":                {"lat": -15.5372, "lon": -47.3346},
    "Caldas Novas":           {"lat": -17.7444, "lon": -48.6250},
}
#lista das arestas com os pesos, distâncias em km, entre as cidades

VERTICE = [
    ("Goiânia", "Anápolis", 55),
    ("Goiânia", "Aparecida de Goiânia", 20),
    ("Goiânia", "Trindade", 25),
    ("Goiânia", "Caldas Novas", 165),
    ("Anápolis", "Brasília", 130),
    ("Anápolis", "Formosa", 150),
    ("Brasília", "Luziânia", 60),
    ("Brasília", "Valparaíso de Goiás", 45),
    ("Brasília", "Formosa", 80),
    ("Luziânia", "Valparaíso de Goiás", 15),
]
#Thigas, aqui monta a lista de adjacência do grafo, onde cada cidade é uma chave

GRAFICO = {cidade: {} for cidade in CIDADE}
for a, b, peso in VERTICE:
    GRAFICO[a][b] = peso
    GRAFICO[b][a] = peso

#Implemetação do algoritmo de Dijkstra para encontrar o caminho mais curto.

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