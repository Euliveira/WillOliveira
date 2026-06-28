import requests
import json
from datetime import datetime

def rastrear_carteira(wallet_alvo, api_key):
    # Endpoint da API do Etherscan para listagem de transações normais
    url = f"https://api.etherscan.io/api"
    
    params = {
        "module": "account",
        "action": "txlist",
        "address": wallet_alvo,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 10,  # Traz as últimas 10 transações para análise
        "sort": "desc",
        "apikey": api_key
    }
    
    print(f"[*] Iniciando varredura na carteira: {wallet_alvo}\n")
    
    try:
        response = requests.get(url, params=params)
        dados = response.json()
        
        if dados["status"] != "1":
            print(f"[-] Erro na API: {dados['message']}")
            return

        transacoes = dados["result"]
        
        print(f" {'  FLUXO  ':^11} | {'  VALOR (ETH)  ':^15} | {'  CONTRA PARTE (ORIGEM/DESTINO)  ':^42} | {'DATA'}")
        print("-" * 90)
        
        for tx in transacoes:
            # Conversão do valor de Wei para Ether
            valor_eth = float(tx["value"]) / 10**18
            
            # Formatação da data
            data_tx = datetime.fromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S')
            
            # Identificação do Fluxo: De onde para onde?
            if tx["from"].lower() == wallet_alvo.lower():
                fluxo = "SAÍDA (OUT)"
                contra_parte = tx["to"]
            else:
                fluxo = "ENTRADA (IN)"
                contra_parte = tx["from"]
                
            # Exibe o resultado estruturado
            print(f" {fluxo:<11} | {valor_eth:>15.6f} | {contra_parte:<42} | {data_tx}")
            
    except Exception as e:
        print(f"[-] Erro ao executar a requisição: {e}")

# --- CONFIGURAÇÃO ---
# Carteira alvo do seu relatório técnico
CARTEIRA_ALVO = "0x8df156a74cf192bdad23eb2853c33df656ae83be922fb160301fd6c2194b9f03"

# DICA: Para rodar, você precisa de uma chave de API gratuita do Etherscan (crie em etherscan.io)
API_KEY_ETHERSCAN = "UTJMEEEVPAH28IDDBG6FDNZ3XYBK2UXH1X"

if __name__ == "__main__":
    if API_KEY_ETHERSCAN == "SUA_API_KEY_AQUI":
        print("[!] Atenção: Insira sua API Key do Etherscan para que o script funcione corretamente.")
    else:
        rastrear_carteira(CARTEIRA_ALVO, API_KEY_ETHERSCAN)
curl -s "https://api.etherscan.io/api?module=block&action=getbl
