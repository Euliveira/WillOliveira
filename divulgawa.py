import os
import time
import random
from datetime import datetime
from playwright.sync_api import sync_playwright

# ================= CONFIGURAÇÕES PRINCIPAIS =================
CONFIG = {
    # 🚫 LISTA DE EXCEÇÕES: O bot vai ignorar estes grupos automaticamente
    "EXCECOES": [
        "Adoradores",
        "DESAFIO BIBLICO",
        "📖 DESAFIO BIBLICO",
        "Enquete Biblica",
        "Anotações",
        "Você" # Evita mandar no seu próprio chat privado
    ],
    
    # O link do canal fixado no rodapé do texto
    "LINK_RODAPE": "https://whatsapp.com/channel/0029VaI00LD8PgsByJRPLi0D",
    
    # Intervalo de envio entre os ciclos gerais: 20 minutos (1200 segundos)
    "INTERVALO_ENVIO": 1200
}

MENSAGENS_BASE = [
    """Olá irmãos, gostaria de indicar este canal do WhatsApp.
Aqui vocês encontram o melhor da adoração ao Senhor Jesus:

➡️ Devocionais
➡️ Pedido de oração
➡️ Louvores
➡️ Testemunhos
➡️ Mensagens motivacionais

Não perca mais tempo, entre agora mesmo e vamos adorar ao Senhor"""
]

def digitar_como_humano(page, seletor, texto):
    """Simula a digitação real e trata o Shift+Enter para pular linha."""
    page.focus(seletor)
    for caractere in texto:
        if caractere == '\n':
            page.keyboard.down("Shift")
            page.keyboard.press("Enter")
            page.keyboard.up("Shift")
        else:
            page.keyboard.type(caractere)
        time.sleep(random.uniform(0.01, 0.03))

def carregar_pagina_com_retry(page, url, tentativas=3):
    for i in range(tentativas):
        try:
            print(f"[WhatsApp] Acessando a plataforma (Tentativa {i+1}/{tentativas})...")
            page.goto(url, timeout=60000, wait_until="load")
            return True
        except Exception as e:
            print(f"[Aviso] Falha ao carregar página: {e}")
            if i < tentativas - 1:
                time.sleep(5)
            else:
                raise e

def disparar_rotina_automatica():
    print(f"\n--- Iniciando ciclo automático de varredura (Texto): {datetime.now().strftime('%H:%M:%S')} ---")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            './minha_sessao_robotica',
            headless=False,
            args=['--start-maximized']
        )
        
        page = context.new_page()
        
        try:
            carregar_pagina_com_retry(page, "https://web.whatsapp.com")
        except Exception:
            context.close()
            return
        
        painel_lateral = 'div[id="pane-side"]'
        
        print("[WhatsApp] Verificando conexão...")
        try:
            page.wait_for_selector(painel_lateral, timeout=180000)
            print("⚡ Conectado e lista de chats carregada!")
        except Exception:
            print("\n[Erro] Tempo limite de carregamento esgotado após 3 minutos.")
            input("👉 Pressione ENTER para fechar...")
            context.close()
            return

        time.sleep(5) 
        
        grupos_processados = set()
        seletor_titulo_chat = 'span[title][dir="auto"]'
        
        # Caixa de texto padrão do chat do WhatsApp Web
        seletor_caixa_texto = 'div[contenteditable="true"][data-testid="conversation-compose-box-input"]'
        
        for scroll in range(5):
            elementos_chats = page.query_selector_all(seletor_titulo_chat)
            
            for elemento in elementos_chats:
                nome_chat = elemento.get_attribute("title")
                
                if not nome_chat:
                    continue
                    
                if nome_chat in grupos_processados:
                    continue
                    
                if any(excecao.lower() in nome_chat.lower() for excecao in CONFIG["EXCECOES"]):
                    print(f"[Ignorado] O chat '{nome_chat}' está na lista de exceções.")
                    grupos_processados.add(nome_chat)
                    continue
                
                try:
                    print(f"\n[Bot] Grupo descoberto: {nome_chat}")
                    grupos_processados.add(nome_chat)
                    
                    # Clica no grupo para abrir a conversa
                    elemento.click(force=True)
                    time.sleep(2)
                    
                    # Verifica se o chat permite envio de mensagens (se a caixa de texto existe e está visível)
                    if not page.is_visible(seletor_caixa_texto):
                        print(f"[Aviso] O grupo '{nome_chat}' parece estar restrito para administradores. Pulando...")
                        continue
                    
                    mensagem_aleatoria = random.choice(MENSAGENS_BASE)
                    texto_final = f"{mensagem_aleatoria}\n\n👉 {CONFIG['LINK_RODAPE']}"
                    
                    print("[Texto] Digitando a mensagem...")
                    digitar_como_humano(page, seletor_caixa_texto, texto_final)
                        
                    time.sleep(1.5)
                    page.keyboard.press("Enter")
                    print(f"[Sucesso] Enviado para o grupo auto-descoberto: {nome_chat}")
                    
                    tempo_espera = random.uniform(35.0, 65.0)
                    print(f"Aguardando {int(tempo_espera)} segundos antes do próximo alvo (Antiban)...")
                    time.sleep(tempo_espera)
                    
                except Exception as e:
                    print(f"[Aviso] Não foi possível interagir com o chat '{nome_chat}': {e}")
                    try:
                        page.keyboard.press("Escape")
                        time.sleep(1)
                    except:
                        pass
            
            print("[Sistema] Rolando a barra lateral para buscar novos grupos...")
            try:
                page.evaluate(f'document.querySelector("{painel_lateral}").scrollBy(0, 500)')
                time.sleep(3) # Tempo extra para o WhatsApp carregar os novos nomes após o scroll
            except:
                pass
        
        print(f"\n[Concluído] Ciclo encerrado. Total de chats validados: {len(grupos_processados)}")
        context.close()

if __name__ == "__main__":
    print("Robô de Varredura Automática (Apenas Texto) Inicializado.")
    while True:
        disparar_rotina_automatica()
        print("Aguardando intervalo de 20 minutos para o próximo ciclo completo...")
        time.sleep(CONFIG["INTERVALO_ENVIO"])
