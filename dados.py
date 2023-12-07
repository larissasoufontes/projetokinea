## Importando as bibliotecas a serem utilizadas 
import sqlite3
import json
import pandas as pd
import requests
import timedelta
import datetime 
import numpy as np 

## Criando a base de dados com a cotacao do dolar

conexao = sqlite3.connect("cotacao_dolar.db")

ponte = conexao.cursor()

ponte.execute("CREATE TABLE IF NOT EXISTS dolar_valores(data REAL, cotacao NUMERIC)")

#Criando a interface para o usuário

tela_de_inicio = """" ----- INSIRA A DATA -----

1) DIGITE A DATA
2) SAIR DA TELA

SELECIONE:

"""

def visualiza_cotacao_por_data(conexao, data):
    with conexao:
        return conexao.execute("SELECT cotacao FROM dolar_valores WHERE data = ?;",(data, )).fetchall() 
    
def inicio():
    while(seleciona:= input(tela_de_inicio)) != "2":
        if seleciona == "1":
            data = input("Digite a data de escolha (ex: dd/mm/yyyy):")
            ponte.execute("SELECT cotacao FROM dolar_valores WHERE data=?", (data,))
            ct_resultado = ponte.fetchall()
            if len(ct_resultado) == 0:
                link = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao=" 
                        + data +"&$top=100&$skip=0&$format=json&$select=cotacaoVenda,dataHoraCotacao")
                requisicao = requests.get(link)
                info = requisicao.json()
                dado = pd.DataFrame(info['value'])
                dado['dataHoraCotacao'] = dado['dataHoraCotacao'].apply(lambda x: x[:-12])
                x = dado["dataHoraCotacao"]
                dado['data_final'] = pd.to_datetime(x) - pd.DateOffset(days=30)
                print(dado)
                data_i = input("Insira a data final (ex: dd/mm/yyyy):")
                link_2 = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/CotacaoDolarPeriodo(dataInicial=@dataInicial,dataFinalCotacao=@dataFinalCotacao)?@dataInicial=" 
                         + data_i  + "&@dataFinalCotacao=" + data + "&$top=100&$format=json&$select=cotacaoVenda")
                requisicao_2 = requests.get(link_2)
                info_2 = requisicao_2.json()
                dado_2 = pd.DataFrame(info_2['value'])
                dado_2['retorno'] = (dado_2.cotacaoVenda - dado_2.cotacaoVenda.shift(1))/ dado_2.cotacaoVenda.shift(1)
                media = np.nanmean(dado_2["retorno"])
                desvio_pdr = np.nanstd(dado_2['retorno'])
                Lsp = ((1.96)*desvio_pdr)+media
                Lin = ((-1.96)*desvio_pdr)+media 

                resposta = ("Se a variação diária do câmbio estiver contido no intervalo %.4f , então a variação não é estatisticamente significativa. Do contrário, pode-se dizer que é estatisticamente diferente de zero." % Lsp)
                print(resposta)



            else: 

                resultado = visualiza_cotacao_por_data(conexao,data)
                print(f"{resultado[0]}")

inicio()
