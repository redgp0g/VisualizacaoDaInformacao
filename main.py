#fonte:https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem-por-escola 
from pandas import read_csv
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import folium
import json

dados_enem = read_csv(r"MICRODADOS_ENEM_ESCOLA.csv", sep=';')

#Gráfico geográfico
participantes_estado = dados_enem.groupby('SG_UF_ESCOLA')['NU_PARTICIPANTES'].sum().reset_index()

geo_json_path = r"br_states.json"

with open(geo_json_path, 'r', encoding='utf-8') as g:
    dados_geo = json.load(g)

for feature in dados_geo['features']:
    sigla = feature['properties']['SIGLA']
    participantes = participantes_estado[participantes_estado['SG_UF_ESCOLA']== sigla]['NU_PARTICIPANTES'].values
    feature['properties']['NU_PARTICIPANTES'] = int(participantes) if len(participantes) > 0 else 0

mapa_brasil_estados = folium.Map(location=(-16.5, -50.1),
                                 tiles="cartodbpositron",
                                 zoom_start=4.5)

folium.Choropleth(
    geo_data=dados_geo,
    data=participantes_estado,
    columns=["SG_UF_ESCOLA", "NU_PARTICIPANTES"],
    key_on="feature.properties.SIGLA",
    fill_color="GnBu",
    fill_opacity=0.9,
    line_opacity=0.8,
    legend_name="Número de Participantes do ENEM"
).add_to(mapa_brasil_estados)

estilo = lambda x: {"fillColor": "white",
                    "color": "black",
                    "fillOpacity": 0.001,
                    "weight": 0.001}

estilo_destacado = lambda x:{"fillColor": "darkblue",
                        "color": "black",
                        "fillOpacity": 0.5,
                        "weight": 1}

destaque_mapa = folium.features.GeoJson(
    data=dados_geo,
    style_function=estilo,
    highlight_function=estilo_destacado,
    tooltip=folium.features.GeoJsonTooltip(
        fields=["Estado", "NU_PARTICIPANTES"],
        aliases=["Estado:", "Nº Participantes:"],
        style=("background-color: white; color: black; font-family: arial; font-size:16px; padding: 5px;")
    )
)

mapa_brasil_estados.add_child(destaque_mapa)

mapa_brasil_estados.save("index.html")



#Gráficos com Plotly
media_redacao_ano = dados_enem.groupby('NU_ANO')['NU_MEDIA_RED'].mean().reset_index()

media_redacao_estado = dados_enem.groupby('SG_UF_ESCOLA')['NU_MEDIA_RED'].mean().reset_index()
media_redacao_estado = media_redacao_estado.sort_values(by='NU_MEDIA_RED', ascending=False)


plt.figure(figsize=(14, 10))

# Primeiro subplot: Evolução da Média das Notas de Redação ao Longo dos Anos
plt.subplot(2, 1, 1)
plt.plot(media_redacao_ano['NU_ANO'], media_redacao_ano['NU_MEDIA_RED'], marker='o', linestyle='-', color='b')
plt.title('Evolução da Média das Notas de Redação ao Longo dos Anos')
plt.xlabel('Ano')
plt.ylabel('Nota Média de Redação')
plt.grid(True)
plt.xticks(media_redacao_ano['NU_ANO'])

# Segundo subplot: Estados com Maiores Médias de Redação no Enem 2005 - 2015
plt.subplot(2, 1, 2)
formatter = ScalarFormatter(useOffset=False)
formatter.set_scientific(False)
plt.bar(media_redacao_estado['SG_UF_ESCOLA'], media_redacao_estado['NU_MEDIA_RED'])
plt.ylabel('Média da Redação')
plt.title('Estados com Maiores Média de Redação no Enem 2005 - 2015')
plt.gca().yaxis.set_major_formatter(formatter)
plt.xticks(rotation=45, ha='right')

plt.tight_layout()
plt.show()