import os
import webbrowser
from datetime import datetime

# Estrutura de pastas para os relatórios
OUTPUT_FOLDER = "DOSSIES_CRIPTO"
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

def analisar_rede(endereco):
    """Identifica automaticamente a rede pelo formato do endereço"""
    if endereco.startswith("T") and len(endereco) > 30:
        return "TRON (TRC-20) - Comum para USDT"
    elif endereco.startswith("0x"):
        return "ETHEREUM/BSC (ERC-20/BEP-20)"                                                                                                                                           elif endereco.startswith(("1", "3", "bc1")):
        return "BITCOIN (BTC)"
    return "REDE NÃO IDENTIFICADA"

def gerar_dossie_cripto(carteira):
    rede = analisar_rede(carteira)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Nome do arquivo de saída
    filename = f"INVESTIGACAO_CRIPTO_{file_timestamp}.html"
    filepath = os.path.join(OUTPUT_FOLDER, filename)

    # Links de Cruzamento de Dados (OSINT)
    # Estes links abrem a busca direto no rastro da carteira
    links = {
        "Rastrear Transações (Tronscan)": f"https://tronscan.org/#/address/{carteira}",
        "Identificar Corretora/Exchange (Blockchair)": f"https://blockchair.com/search?q={carteira}",
        "Buscar Endereço no Google (Fóruns/Vazamentos)": f"https://www.google.com/search?q=%22{carteira}%22",
        "Verificar Blacklists de Fraude (Scam Search)": f"https://www.google.com/search?q=%22{carteira}%22+scam+fraud+stolen",
        "Visualizar Conexões de Carteiras (Breadcrumbs)": f"https://www.breadcrumbs.app/home?search={carteira}"
    }

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Dossiê Investigativo - Cripto</title>
        <style>
            body {{ background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; padding: 40px; }}
            .container {{ border: 2px solid #238636; border-radius: 10px; padding: 30px; background-color: #161b22; box-shadow: 0 0 20px #238636; }}
            h1 {{ color: #2ea043; border-bottom: 2px solid #2ea043; padding-bottom: 10px; }}
            .info-box {{ background: #0d1117; padding: 15px; border-left: 5px solid #2ea043; margin: 20px 0; }}
            .label {{ color: #8b949e; font-weight: bold; text-transform: uppercase; }}
            .value {{ color: #58a6ff; font-size: 1.2em; word-break: break-all; }}
            .link-card {{ background: #21262d; margin: 10px 0; padding: 15px; border-radius: 5px; border: 1px solid #30363d; }}
            a {{ color: #ffa657; text-decoration: none; font-weight: bold; font-size: 1.1em; }}
            a:hover {{ text-decoration: underline; color: #ff7b72; }}
            .footer {{ margin-top: 50px; font-size: 0.8em; color: #484f58; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>RELATÓRIO DE INTELIGÊNCIA BLOCKCHAIN</h1>

            <div class="info-box">
                <p><span class="label">Endereço Investigado:</span><br><span class="value">{carteira}</span></p>
                <p><span class="label">Rede Detectada:</span><br><span class="value">{rede}</span></p>
                <p><span class="label">Data da Coleta:</span><br><span class="value">{timestamp}</span></p>
            </div>

            <h3>CRUZAMENTO DE DADOS E RASTREAMENTO:</h3>
            <p>Clique nos links abaixo para verificar o fluxo do dinheiro e identificar a autoria:</p>

            {"".join([f'<div class="link-card"><a href="{url}" target="_blank">>> {nome}</a></div>' for nome, url in links.items()])}

            <div class="footer">
                Este documento é uma prova técnica de rastreabilidade de ativos digitais.
                ID do Telegram Relacionado: 7553925220
            </div>
        </div>
    </body>
    </html>
    """

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filepath

# --- MENU DE EXECUÇÃO ---
if __name__ == "__main__":
    print("="*50)
    print("      SISTEMA DE RASTREAMENTO CRIPTO - OSINT")
    print("="*50)

    # Campo de Entrada (Input)
    carteira_alvo = input("\n[>] Cole o endereço da carteira da Binance/Cripto: ").strip()

    if len(carteira_alvo) < 10:
        print("[!] Erro: Endereço inválido.")
    else:
        print(f"[*] Processando rastro para a rede {analisar_rede(carteira_alvo)}...")
        caminho = gerar_dossie_cripto(carteira_alvo)

        print("\n" + "!"*50)
        print("   GERADO COM SUCESSO!")
        print(f"   Local: {os.path.abspath(caminho)}")
        print("!"*50)

        # Tenta abrir o arquivo automaticamente no navegador
        try:
            webbrowser.open('file://' + os.path.abspath(caminho))
        except:
            print("\n[i] Abra o arquivo manualmente no seu navegador para ver o cruzamento de dados.")




