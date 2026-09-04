from flask import Flask

app = Flask(__name__)

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

GRAFICO = {cidade: {} for cidade in CIDADE}
for a, b, peso in VERTICE:
    GRAFICO[a][b] = peso
    GRAFICO[b][a] = peso