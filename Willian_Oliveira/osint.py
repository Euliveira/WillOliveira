from telethon import TelegramClient, events, sync
import os
import time

time.sleep(1)
os.system("figlet OSINT")

print("""
==========================================
        Instagram: @willoliveiradev
==========================================
""")
time.sleep(4)

# --- INSIRA SEUS DADOS AQUI ---
api_id = "..."
api_hash = "..."

async def investigar_telegram(alvo):
    # O alvo pode ser @usuario ou o link t.me/usuario
    client = TelegramClient('sessao_detetive', api_id, api_hash)
    await client.start()

    try:
        # Busca a entidade (o perfil do criminoso)
        entidade = await client.get_entity(alvo)

        dados_reais = {
            "ID Numérico": entidade.id,
            "Primeiro Nome": entidade.first_name,
            "Sobrenome": entidade.last_name if entidade.last_name else "N/A",
            "Username": f"@{entidade.username}" if entidade.username else "Sem Username",
            "Telefone Oculto": entidade.phone if entidade.phone else "Privado",
            "É Bot?": "Sim" if entidade.bot else "Não",
            "Bio/Descrição": "Extraível via busca profunda"
        }

        # Aqui geramos o HTML que você salva na pasta
        gerar_html_prova(dados_reais)
        print(f"[+] Alvo identificado! ID: {entidade.id}")

    except Exception as e:
        print(f"[-] Erro ao localizar alvo: {e}")
    finally:
        await client.disconnect()

def gerar_html_prova(dados):
    filename = f"EVIDENCIA_TG_{dados['ID Numérico']}.html"
    with open(filename, "w", encoding="utf-8") as f:
        # Estrutura HTML que você já conhece
        html = f"<html><body style='background:#000;color:#0f0;font-family:monospace;'>"
        html += f"<h1>DOSSIÊ TELEGRAM: {dados['Username']}</h1><hr>"
        for k, v in dados.items():
            html += f"<p><b>{k}:</b> {v}</p>"
        html += "</body></html>"
        f.write(html)
    os.system(f"start {filename}")

# --- INPUT DO USUÁRIO ---
alvo_input = input("Cole aqui o @username ou link do Telegram do golpista: ")
import asyncio
asyncio.run(investigar_telegram(alvo_input))
