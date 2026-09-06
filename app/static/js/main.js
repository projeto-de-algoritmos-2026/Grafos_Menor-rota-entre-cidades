// Ponto central aproximado da região GO/DF, só para centralizar o mapa inicial.
const CENTRO_MAPA = [-16.3, -48.3];

const mapa = L.map("mapa").setView(CENTRO_MAPA, 7);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(mapa);

// Estilos de linha por status de aresta — usados tanto no desenho inicial
// (tudo "nao_considerada") quanto depois de calcular uma rota.
const ESTILO_ARESTA = {
  nao_considerada: { color: "#7a837a", weight: 3, opacity: 0.7, dashArray: null },
  descartada:      { color: "#e0a53a", weight: 3, opacity: 0.9, dashArray: "6 4" },
  usada:           { color: "#1f6f43", weight: 5, opacity: 0.95, dashArray: null },
};

function chaveAresta(a, b) {
  // chave estável independente da ordem (grafo é não-direcionado)
  return [a, b].sort().join("|||");
}

const estado = {
  cidades: {},            // nome -> {lat, lon}
  marcadores: {},          // nome -> L.marker
  linhasArestas: {},       // chaveAresta(a,b) -> L.polyline
  linhaCaminho: null,      // linha grossa destacando o caminho final, por cima das arestas
  timersAnimacao: [],      // setTimeout pendentes da animação de eventos
};

async function carregarCidades() {
  const resposta = await fetch("/api/cidades");
  const cidades = await resposta.json();

  const selectOrigem = document.getElementById("origem");
  const selectDestino = document.getElementById("destino");

  cidades.forEach((cidade) => {
    estado.cidades[cidade.nome] = { lat: cidade.lat, lon: cidade.lon };

    const marcador = L.marker([cidade.lat, cidade.lon]).addTo(mapa);
    marcador.bindPopup(cidade.nome);
    estado.marcadores[cidade.nome] = marcador;

    [selectOrigem, selectDestino].forEach((select) => {
      const opcao = document.createElement("option");
      opcao.value = cidade.nome;
      opcao.textContent = cidade.nome;
      select.appendChild(opcao);
    });
  });

  if (cidades.length > 1) {
    selectDestino.selectedIndex = 1;
  }
}

async function carregarArestas() {
  const resposta = await fetch("/api/arestas");
  const arestas = await resposta.json();

  arestas.forEach((aresta) => {
    const origem = estado.cidades[aresta.origem];
    const destino = estado.cidades[aresta.destino];
    if (!origem || !destino) return;

    const estilo = ESTILO_ARESTA.nao_considerada;
    const linha = L.polyline(
      [
        [origem.lat, origem.lon],
        [destino.lat, destino.lon],
      ],
      estilo
    ).addTo(mapa);

    linha.bindTooltip(`${aresta.origem} → ${aresta.destino}: ${aresta.peso} km`, { sticky: true });
    estado.linhasArestas[chaveAresta(aresta.origem, aresta.destino)] = linha;
  });
}

function limparResultadoAnterior() {
  if (estado.linhaCaminho) {
    mapa.removeLayer(estado.linhaCaminho);
    estado.linhaCaminho = null;
  }
  estado.timersAnimacao.forEach((t) => clearTimeout(t));
  estado.timersAnimacao = [];

  Object.values(estado.marcadores).forEach((m) => {
    m.getElement()?.classList.remove("marcador-visitado");
  });

  Object.values(estado.linhasArestas).forEach((linha) => {
    linha.setStyle(ESTILO_ARESTA.nao_considerada);
  });

  document.getElementById("log-eventos").innerHTML = "";
  document.getElementById("resultado").classList.add("oculto");
  document.getElementById("erro").classList.add("oculto");
}

function textoDoEvento(evento) {
  if (evento.tipo === "visita") {
    return `Visitando ${evento.no} — menor distância conhecida até aqui: ${evento.distancia} km.`;
  }
  if (evento.aceito) {
    return `Aresta ${evento.de} → ${evento.para} (${evento.peso} km): melhora a distância de ${evento.para} para ${evento.nova_distancia} km.`;
  }
  return `Aresta ${evento.de} → ${evento.para} (${evento.peso} km): descartada, já existe um caminho igual ou mais curto até ${evento.para}.`;
}

function adicionarLinhaDeLog(evento) {
  const lista = document.getElementById("log-eventos");
  const item = document.createElement("li");
  item.textContent = textoDoEvento(evento);
  item.className =
    evento.tipo === "visita"
      ? "evento-visita"
      : evento.aceito
      ? "evento-aceito"
      : "evento-descartado";
  lista.appendChild(item);
  lista.parentElement.scrollTop = lista.parentElement.scrollHeight;
}

function animarEventos(eventos, arestasStatus, aoTerminar) {
  // Roda os eventos do Dijkstra em sequência: acende o nó em cada "visita"
  // e destaca a aresta correspondente em amarelo no momento em que ela é
  // examinada (aceita ou não). Só depois de todos os eventos passarem é
  // que aplicamos as cores finais (usada / descartada / não considerada).
  eventos.forEach((evento, indice) => {
    const timer = setTimeout(() => {
      if (evento.tipo === "visita") {
        estado.marcadores[evento.no]?.getElement()?.classList.add("marcador-visitado");
      } else {
        const linha = estado.linhasArestas[chaveAresta(evento.de, evento.para)];
        linha?.setStyle({ color: "#e6c34a", weight: 4, opacity: 1, dashArray: null });
      }
      adicionarLinhaDeLog(evento);

      if (indice === eventos.length - 1) {
        aplicarCoresFinais(arestasStatus);
        aoTerminar();
      }
    }, indice * 350);
    estado.timersAnimacao.push(timer);
  });
}

function aplicarCoresFinais(arestasStatus) {
  arestasStatus.forEach((aresta) => {
    const linha = estado.linhasArestas[chaveAresta(aresta.origem, aresta.destino)];
    if (linha) {
      linha.setStyle(ESTILO_ARESTA[aresta.status]);
    }
  });
}

function desenharCaminho(caminho) {
  const pontos = caminho.map((nome) => {
    const cidade = estado.cidades[nome];
    return [cidade.lat, cidade.lon];
  });

  estado.linhaCaminho = L.polyline(pontos, ESTILO_ARESTA.usada).addTo(mapa);
  mapa.fitBounds(estado.linhaCaminho.getBounds(), { padding: [30, 30] });
}

function mostrarErro(mensagem) {
  const caixaErro = document.getElementById("erro");
  caixaErro.textContent = mensagem;
  caixaErro.classList.remove("oculto");
}

function mostrarResultado(caminho, distancia) {
  document.getElementById("resultado-caminho").textContent =
    "Caminho: " + caminho.join(" → ");
  document.getElementById("resultado-distancia").textContent =
    "Distância total: " + distancia + " km";
  document.getElementById("resultado").classList.remove("oculto");
}

async function calcularRota(origem, destino) {
  const resposta = await fetch("/api/rota", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ origem, destino }),
  });

  const dados = await resposta.json();

  if (!resposta.ok) {
    throw new Error(dados.erro || "Erro ao calcular a rota.");
  }

  return dados;
}

document.getElementById("form-rota").addEventListener("submit", async (evento) => {
  evento.preventDefault();

  const origem = document.getElementById("origem").value;
  const destino = document.getElementById("destino").value;

  limparResultadoAnterior();

  if (origem === destino) {
    mostrarErro("Origem e destino não podem ser a mesma cidade.");
    return;
  }

  try {
    const { caminho, distancia, eventos, arestas_status } = await calcularRota(origem, destino);
    animarEventos(eventos, arestas_status, () => {
      desenharCaminho(caminho);
      mostrarResultado(caminho, distancia);
    });
  } catch (erro) {
    mostrarErro(erro.message);
  }
});

(async function iniciar() {
  await carregarCidades();
  await carregarArestas();
})();
