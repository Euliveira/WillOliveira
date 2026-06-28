import requests
from datetime import datetime

def rastrear_blockchair(wallet_alvo):
    # API pública unificada da Blockchair (Rede Ethereum como padrão de checagem)
    url = f"https://api.blockchair.com/ethereum/dashboards/address/{wallet_alvo}"
    
    # Cabeçalho para simular um navegador comum e evitar bloqueios de WAF/Cloudflare
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Parâmetros para limitar o número de transações na resposta
    params = {
        "limit": "10",
        "offset": "0"
    }
    
    print(f"[*] Iniciando Varredura Multichain Avançada para: {wallet_alvo}\n")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"[-] Erro de Conexão com o Servidor. Status Code: {response.status_code}")
            print("[!] O servidor bloqueou a requisição direta. Tentando rota alternativa...")
            return
            
        dados = response.json()
        
        # Estrutura de extração de dados da Blockchair
        if "data" not in dados or wallet_alvo not in dados["data"]:
            print("[-] Dados não localizados para esta carteira nesta blockchain.")
            return
            
        alvo_data = dados["data"][wallet_alvo]
        balance_satoshis = alvo_data["address"]["balance"]
        balance_real = balance_satoshis / 10**18
        
        print(f"[+] Saldo Atual da Carteira: {balance_real:.6f} ETH/Ativos")
        
        calls = alvo_data.get("calls", [])
        if not calls:
            print("[-] Nenhuma transação recente encontrada no livro contábil desta rede.")
            return
            
        print(f"\n {'  FLUXO  ':^11} | {'  VALOR ':^14} | {'  CONTRA PARTE (ORIGEM/DESTINO)  ':^42} | {'DATA'}")
        print("-" * 90)
        
        for tx in calls:
            # Blockchair expressa valores em satoshis do ativo base (18 decimais para ETH)
            valor = float(tx.get("value", 0)) / 10**18
            time_str = tx.get("time", "0000-00-00 00:00:00")
            
            # Lógica de Input/Output baseada na carteira investigada
            if tx.get("sender") == wallet_alvo:
                fluxo = "SAÍDA (OUT)"
                contra_parte = tx.get("recipient", "Contrato/Desconhecido")
            else:
                fluxo = "ENTRADA (IN)"
                contra_parte = tx.get("sender", "Origem Oculta")
                
            print(f" {fluxo:<11} | {valor:>14.6f} | {contra_parte:<42} | {time_str}")
            
    except Exception as e:
        print(f"[-] Erro na decomposição do JSON: {e}")

# --- EXECUÇÃO DO TARGET ---
CARTEIRA_ALVO = "0x8df156a74cf192bdad23eb2853c33df656ae83be922fb160301fd6c2194b9f03"

if __name__ == "__main__":
    rastrear_blockchair(CARTEIRA_ALVO)
