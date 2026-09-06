
from flask import Blueprint, jsonify, request

from app.core.grafo import CIDADE, GRAFICO, ARESTA
from app.core.dijkstra import dijkstra

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/cidades")
def cidades():
   #coordenadas para o front plotar os marcadores no mapa e popular os seletores de origem/destino
    dados = [
        {"nome": nome, "lat": info["lat"], "lon": info["lon"]}
        for nome, info in CIDADE.items()
    ]
    return jsonify(dados)


@api_bp.route("/arestas")
def arestas():
    #conexões do grafo para o front desenhar as arestas ao carregar o mapa
    dados = [
        {"origem": a, "destino": b, "peso": peso}
        for a, b, peso in ARESTA
    ]
    return jsonify(dados)


@api_bp.route("/rota", methods=["POST"])
def rota():
  #   Recebe origem e destino e devolve o caminho  mais curto calculado pelo algoritm
    dados = request.get_json(silent=True) or {}
    origem = dados.get("origem")
    destino = dados.get("destino")

    if not origem or not destino:
        return jsonify({"erro": "Informe 'origem' e 'destino' no corpo da requisição."}), 400

    if origem not in CIDADE:
        return jsonify({"erro": f"Cidade de origem desconhecida: {origem}"}), 400

    if destino not in CIDADE:
        return jsonify({"erro": f"Cidade de destino desconhecida: {destino}"}), 400

    if origem == destino:
        return jsonify({"erro": "Origem e destino não podem ser a mesma cidade."}), 400

    caminho, distancia, ordem_visit = dijkstra(GRAFICO, origem, destino)

    if caminho is None:
        return jsonify({"erro": f"Não existe caminho entre {origem} e {destino}."}), 404

    return jsonify({
        "caminho": caminho,
        "distancia": distancia,
        "ordem_visita": ordem_visit,
    })
