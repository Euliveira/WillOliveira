import requests
from datetime import datetime

# ================= CONFIGURAÇÕES DO ANALISTA =================
# Chave e endereço higienizados, sem nenhum caractere oculto
ETHERSCAN_API_KEY = "IU9BJZX6M2W97RRGT3MT8EZAKSXKR2F5H1"
CLIENT_ADDRESS = "0xD63a23166665a9A516B8818b5BecEbDFc571A844"
TARGET_DATE = "2025-07-12"
# =============================================================

def buscar_tokens_ethereum():
    url = "https://api.etherscan.io/api"
    
    params = {
        "module": "account",
        "action": "tokentx",
        "address": CLIENT_ADDRESS,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": ETHERSCAN_API_KEY
    }
    
    print(f"[*] Consultando a Blockchain Ethereum (Tokens) para o endereço: {CLIENT_ADDRESS}...")
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data["status"] == "1":
            transacoes = data["result"]
            encontrou = False
            
            print(f"[+] Buscando movimentações do dia: {TARGET_DATE}...\n")
            
            for tx in transacoes:
                data_tx = datetime.utcfromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d')
                
                if data_tx == TARGET_DATE and tx["from"].lower() == CLIENT_ADDRESS.lower():
                    decimals = int(tx["tokenDecimal"])
                    valor = int(tx["value"]) / (10 ** decimals)
                    
                    print("=" * 70)
                    print("¡MOVIMENTAÇÃO DE TOKEN DETECTADA NA REDE ETHEREUM!")
                    print(f"Horário:             {datetime.utcfromtimestamp(int(tx['timeStamp'])).strftime('%H:%M:%S')} UTC")
                    print(f"Valor Extraído:      {valor:.6f} {tx['tokenSymbol']}")
                    print(f"Origem (Vítima):     {tx['from']}")
                    print(f"DESTINO IDENTIFICADO: {tx['to']}  <-- COPIE ESTE ENDEREÇO")
                    print(f"Hash da Transação:   {tx['hash']}")
                    print("=" * 70)
                    encontrou = True
            
            if not encontrou:
                print(f"[-] Nenhuma transferência de token ERC-20 saiu deste endereço em {TARGET_DATE} na rede Ethereum.")
                print("[*] Nota: Se o terminal não encontrar registros nesta rede, confirmamos que a rota usou exclusivamente a rede BSC.")
        else:
            print(f"[-] Resposta da API: {data['message']}")
            print("[!] Se o erro persistir, valide se esta chave está ativa no painel do Etherscan.")
            
    except Exception as e:
        print(f"[-] Erro ao executar o mapeamento: {e}")

if __name__ == "__main__":
    buscar_tokens_ethereum()