import requests
from datetime import datetime

def varrer_rede_bsc_publico(wallet_alvo):
    # URL pública padrão da API do BscScan
    url = "https://api.bscscan.com/api"
    
    # Parâmetros configurados para rodar de forma pública (sem travar no NOTOK)
    params_tokens = {
        "module": "account",
        "action": "tokentx",
        "address": wallet_alvo,
        "page": 1,
        "offset": 10,
        "sort": "desc",
        "apikey": "none"  # Enviando 'none' a API aceita a requisição pública padrão
    }
    
    print(f"[*] Verificando fluxo de TOKENS na rede BSC para: {wallet_alvo}\n")
    
    try:
        response = requests.get(url, params=params_tokens)
        dados = response.json()
        
        # Se retornar NOTOK ou status 0 com erro de chave, avisa
        if dados.get("status") == "0" and "Invalid API Key" in dados.get("result", ""):
            print("[-] Erro de autenticação. Tentando requisição limpa...")
            params_tokens.pop("apikey", None)
            response = requests.get(url, params=params_tokens)
            dados = response.json()

        if dados.get("status") != "1":
            print(f"[-] Resultado da rede: {dados.get('message')} - {dados.get('result', '')}")
            return

        transacoes = dados["result"]
        
        if not transacoes:
            print("[-] Nenhuma movimentação de token encontrada nesta carteira na rede BSC.")
            return
        
        print(f" {'  FLUXO  ':^11} | {'  VALOR ':^12} | {'TOKEN':<6} | {'  CONTRA PARTE (ORIGEM/DESTINO)  ':^42} | {'DATA'}")
        print("-" * 110)
        
        for tx in transacoes:
            decimais = int(tx.get("tokenDecimal", 18))
            valor = float(tx["value"]) / 10**decimais
            simbolo_token = tx.get("tokenSymbol", "TOKEN")
            
            data_tx = datetime.fromtimestamp(int(tx["timeStamp"])).strftime('%Y-%m-%d %H:%M:%S')
            
            if tx["from"].lower() == wallet_alvo.lower():
                fluxo = "SAÍDA (OUT)"
                contra_parte = tx.get("to", "Desconhecido")
            else:
                fluxo = "ENTRADA (IN)"
                contra_parte = tx["from"]
                
            print(f" {fluxo:<11} | {valor:>12.2f} | {simbolo_token:<6} | {contra_parte:<42} | {data_tx}")
            
    except Exception as e:
        print(f"[-] Erro crítico na execução: {e}")

# --- EXECUÇÃO ---
CARTEIRA_ALVO = "0x8df156a74cf192bdad23eb2853c33df656ae83be922fb160301fd6c2194b9f03"

if __name__ == "__main__":
    varrer_rede_bsc_publico(CARTEIRA_ALVO)



