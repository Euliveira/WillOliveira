import os
import re
import json
import cv2
import pytesseract
from datetime import datetime

class RastreadorFinanceiroForense:
    def __init__(self):
        self.transacoes_extraidas = []
        # Lista de mapeamento de bancos para o OCR identificar com mais precisão
        self.padroes_bancos = [
            "C6 S.A.", "C6 BANK", "BRADESCO", "ITAÚ", "ITAU", "SANTANDER", 
            "BANCO DO BRASIL", "NUBANK", "INTER", "STONE", "PAGSEGURO", "MERCADO PAGO"
        ]

    def pre_processar_imagem(self, caminho_imagem):
        """Aplica filtros avançados para isolar o texto do fundo do comprovante"""
        imagem = cv2.imread(caminho_imagem)
        cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        
        # Redimensiona para aumentar a resolução se a imagem for pequena (melhora o OCR)
        cinza = cv2.resize(cinza, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # Aplica thresholding adaptativo para remover sombras e focar nas letras
        filtrada = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return filtrada

    def extrair_dados_comprovante(self, caminho_imagem):
        """Varre o print buscando a materialidade completa da transação"""
        img_processada = self.pre_processar_imagem(caminho_imagem)
        texto = pytesseract.image_to_string(img_processada, lang='por')
        
        dados = {
            "arquivo": os.path.basename(caminho_imagem),
            "id_transacao_hash": "NÃO IDENTIFICADO",
            "destino_cnpj_cpf": "NÃO IDENTIFICADO",
            "instituicao_destino": "NÃO IDENTIFICADO",
            "valor": "NÃO IDENTIFICADO",
            "data": "NÃO IDENTIFICADO"
        }

        # 1. Captura de ID de Transação / Código de Autenticação / End-to-End ID do Pix
        # Captura o padrão oficial do Banco Central (letra E seguida de 31 caracteres alfanuméricos)
        id_pix_match = re.search(r'\b(E[A-Za-z0-9]{31})\b', texto)
        if id_pix_match:
            dados["id_transacao_hash"] = id_pix_match.group(1).strip()
        else:
            # Padrão secundário para códigos de autenticação bancária comuns (TED/DOC ou internos)
            autenticacao_match = re.search(r'(?:Autenticação|Controle|Transação|ID):\s*([A-Za-z0-9\.\-\s]{15,})', texto, re.IGNORECASE)
            if autenticacao_match:
                dados["id_transacao_hash"] = autenticacao_match.group(1).replace("\n", "").strip()

        # 2. Captura de CNPJ ou CPF do Destinatário
        cnpj_match = re.search(r'\b(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})\b', texto)
        if cnpj_match:
            dados["destino_cnpj_cpf"] = cnpj_match.group(1)

        # 3. Captura do Valor Financeiro
        valor_match = re.search(r'(?:Valor|Total|Quantia)[^\d]*R\$\s*([\d\.,]+)', texto, re.IGNORECASE)
        if not valor_match:
            valor_match = re.search(r'R\$\s*([\d\.,]+)', texto)
        if valor_match:
            dados["valor"] = valor_match.group(1).strip()

        # 4. Captura da Data da Operação
        data_match = re.search(r'\b(\d{2}/\d{2}/\d{4})\b', texto)
        if data_match:
            dados["data"] = data_match.group(1)

        # 5. Identificação Inteligente da Instituição Financeira Recebedora
        for banco in self.padroes_bancos:
            if re.search(rf'\b{banco}\b', texto, re.IGNORECASE):
                dados["instituicao_destino"] = banco
                break

        return dados

    def executar_fluxo(self):
        print("="*60)
        print("PARSER FORENSE DE COMPROVANTES PIX/BANCÁRIOS")
        print("="*60)
        
        diretorio = input("\n[>] Digite a pasta com os prints dos comprovantes: ")
        
        if not os.path.exists(diretorio):
            print("[!] Erro: Diretório inválido.")
            return

        formatos_validos = ('.jpg', '.jpeg', '.png')
        arquivos = [f for f in os.listdir(diretorio) if f.lower().endswith(formatos_validos)]
        
        print(f"\n[+] Encontrados {len(arquivos)} arquivos de imagem.")

        for arquivo in arquivos:
            caminho_completo = os.path.join(diretorio, arquivo)
            print(f"\n[*] Analisando metadados e imagem de: {arquivo}")
            
            try:
                dados = self.extrair_dados_comprovante(caminho_completo)
            except Exception as e:
                print(f"[!] Falha no motor OCR para este arquivo: {str(e)}")
                dados = {"arquivo": arquivo, "id_transacao_hash": "MHA-FALHA", "destino_cnpj_cpf": "MHA-FALHA", "instituicao_destino": "MHA-FALHA", "valor": "MHA-FALHA", "data": "MHA-FALHA"}

            # Exibição dos dados coletados para checagem do analista
            print(f"    -> Banco Destino: {dados['instituicao_destino']}")
            print(f"    -> Beneficiário (CNPJ/CPF): {dados['destino_cnpj_cpf']}")
            print(f"    -> ID / Hash Pix: {dados['id_transacao_hash']}")
            print(f"    -> Valor Extraído: R$ {dados['valor']}")
            print(f"    -> Data: {dados['data']}")
            
            # Interatividade de segurança: Blindagem de Cadeia de Custódia
            corrigir = input("    [?] Deseja validar/corrigir estes dados manualmente? (s/N): ").lower()
            if confirmar == 's':
                dados["instituicao_destino"] = input("    [->] Nome correto da Instituição Bancária: ").upper()
                dados["id_transacao_hash"] = input("    [->] ID de Transação correto: ")
                dados["destino_cnpj_cpf"] = input("    [->] CNPJ/CPF correto do destinatário: ")
                dados["valor"] = input("    [->] Valor real da transação: ")
                dados["data"] = input("    [->] Data correta (DD/MM/AAAA): ")

            self.transacoes_extraidas.append(dados)

        nome_relatorio = input("\n[>] Nome do arquivo para salvar o mapeamento (ex: fluxo_saida.json): ")
        if not nome_relatorio.endswith('.json'):
            nome_relatorio += '.json'

        relatorio_final = {
            "meta_analise": {
                "analista_responsavel": "Willian de Oliveira",
                "timestamp_execucao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "metodologia": "Extração Híbrida (OCR Computacional + Validação Manual)"
            },
            "rastreamento_fluxo_destino": self.transacoes_extraidas
        }

        with open(nome_relatorio, 'w', encoding='utf-8') as f:
            json.dump(relatorio_final, f, indent=4, ensure_ascii=False)
            
        print(f"\n[+] Mapeamento de destino concluído. Arquivo salvo: {nome_relatorio}")

if __name__ == "__main__":
    rastreador = RastreadorFinanceiroForense()
    rastreador.executar_fluxo()