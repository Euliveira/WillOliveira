import requests
import json
from datetime import datetime

def rastrear_carteira_v2(wallet_alvo, api_key):
    # Nova URL Base para a API V2 do Etherscan
    url = "https://api.etherscan.io/v2/api"
    
    # Parâmetros ajustados para o padrão V2
    params = {
        "chainid": "1",  # Define a rede Ethereum Mainnet na V2
        "module": "account",
        "action": "txlist",
        "address": wallet_alvo,
        "startblock": 0,
        "endblock": 99999999,
        "page": 1,
        "offset": 10,  # Traz as últimas 10 transações
        "sort": "desc",
        "apikey": api_key
    }
    
    print(f"[*] Iniciando varredura (API V2) na carteira: {wallet_alvo}\n")
    
    try:
        response = requests.get(url, params=params)
        dados = response.json()
        
        # A V2 costuma retornar os dados diretamente ou sob validação do status
        if "result" not in dados or (isinstance(dados.get("status"), str) and dados["status"] == "0"):
            msg_erro = dados.get("message", "Erro desconhecido")
            print(f"[-] Erro na API V2: {msg_erro}")
            if "result" in dados and isinstance(dados["result"], str):
                print(f"[-] Detalhe: {dados['result']}")
            return

        transacoes = dados["result"]
        
        if not isinstance(transacoes, list):
            print("[-] Nenhuma transação localizada ou formato inesperado.")
            return

        print(f" {'  FLUXO  ':^11} | {'  VALOR (ETH)  ':^15} | {'  CONTRA PARTE (ORIGEM/DESTINO)  ':^42} | {'DATA'}")
        print("-" * 90)
        
        for tx in transacoes:
            valor_eth = float(tx["value"]) / 10**18
            data_tx = datetime.fromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S')
            
            if tx["from"].lower() == wallet_alvo.lower():
                fluxo = "SAÍDA (OUT)"
                contra_parte = tx.get("to", "Contrato Criado / Vazio")
            else:
                fluxo = "ENTRADA (IN)"
                contra_parte = tx["from"]
                
            print(f" {fluxo:<11} | {valor_eth:>15.6f} | {contra_parte:<42} | {data_tx}")
            
    except Exception as e:
        print(f"[-] Erro ao executar a requisição na V2: {e}")

# --- CONFIGURAÇÃO ---
CARTEIRA_ALVO = "0x8df156a74cf192bdad23eb2853c33df656ae83be922fb160301fd6c2194b9f03"
API_KEY_ETHERSCAN = "UTJMEEEVPAH28IDDBG6FDNZ3XYBK2UXH1X"

if __name__ == "__main__":
    rastrear_carteira_v2(CARTEIRA_ALVO, API_KEY_ETHERSCAN)
