import os
from datetime import datetime

# Pasta para salvar os dossiês                                                                                                                                                      OUTPUT_DIR = ("Investigar pix: ")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def gerar_dossie_pix(chave_pix, nome_confirmado, banco):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = nome_confirmado.replace(" ", "_") if nome_confirmado else "ALVO_PIX"
    filename = f"DOSSIE_PIX_{nome_arquivo}_{timestamp}.html"
    filepath = os.path.join(OUTPUT_DIR, filename)                                                                                                                                   
    # Lógica de cruzamento de dados (Dorks de OSINT)
    nome_url = nome_confirmado.replace(" ", "+")
    links_cruzamento = {
        "1. Buscar Processos Criminais (JusBrasil)": f"https://www.jusbrasil.com.br/busca?q={nome_url}",
        "2. Identificar Local de Trabalho (LinkedIn)": f"https://www.google.com/search?q=site:linkedin.com/in/+%22{nome_url}%22",
        "3. Pesquisar CPF em Vazamentos (Google Dork)": f"https://www.google.com/search?q=%22{chave_pix}%22",
        "4. Verificar se é Sócio de Empresa (Portal Transparência)": f"https://www.google.com/search?q=socio+administrador+%22{nome_url}%22",
        "5. Antecedentes no Escavador": f"https://www.escavador.com/busca?q={nome_url}"
    }

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ background: #0a0a0a; color: #00ff41; font-family: 'Segoe UI', monospace; padding: 30px; }}
            .card {{ border: 2px solid #ff0055; background: #000; padding: 25px; border-radius: 8px; box-shadow: 0 0 15px #ff0055; }}
            h1 {{ color: #fff; text-transform: uppercase; border-bottom: 2px solid #ff0055; }}
            .field {{ margin: 15px 0; font-size: 1.2em; }}
            .label {{ color: #ff0055; font-weight: bold; }}
            .value {{ color: #ffffff; margin-left: 10px; }}
            .osint-links {{ background: #111; padding: 15px; border-radius: 5px; margin-top: 20px; }}
            a {{ color: #00d4ff; text-decoration: none; display: block; margin: 10px 0; font-size: 1.1em; }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>Relatório de Identificação: Alvo PIX</h1>
            <div class="field"><span class="label">Chave PIX Investigada:</span> <span class="value">{chave_pix}</span></div>
            <div class="field"><span class="label">Nome no Comprovante:</span> <span class="value">{nome_confirmado}</span></div>
            <div class="field"><span class="label">Banco de Destino:</span> <span class="value">{banco}</span></div>

            <div class="osint-links">
                <h3>CRUZAMENTO DE DADOS (CLIQUE PARA VER):</h3>
                {"".join([f'<a href="{v}" target="_blank">{k}</a>' for k, v in links_cruzamento.items()])}
            </div>
            <p style="margin-top: 30px; font-size: 0.8em; color: #555;">Documento gerado para fins de denúncia à Polícia Federal.</p>
        </div>
    </body>
    </html>
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filepath

# --- EXECUÇÃO DO SOFTWARE ---
if __name__ == "__main__":
    print("-" * 40)
    print(" SISTEMA DE IDENTIFICAÇÃO POR PIX ")
    print("-" * 40)

    chave = input("Digite a Chave PIX (CPF/Email/Tel): ")

    # IMPORTANTE: Você precisa simular o envio no seu banco para ver o nome real
    print("\n[!] Atenção: Verifique o nome que aparece na tela de confirmação do seu banco.")
    nome_alvo = input("Digite o NOME COMPLETO que apareceu no banco: ")
    banco_alvo = input("Digite o nome da Instituição Financeira (Ex: Nubank): ")

    caminho_arquivo = gerar_dossie_pix(chave, nome_alvo, banco_alvo)

    print(f"\n[+] Cruzamento concluído!")
    print(f"[+] Dossiê gerado: {os.path.abspath(caminho_arquivo)}")

    # Se estiver no seu Linux com servidor 8080, o arquivo aparecerá lá.