import csv
import json
import os
import re
from datetime import datetime


class RastreadorFinanceiroForenseTexto:

    def __init__(self):
        self.transacoes_extraidas = []
        self.padroes_bancos = [
            "C6 S.A.",
            "C6 BANK",
            "BRADESCO",
            "ITAÚ",
            "ITAU",
            "SANTANDER",
            "BANCO DO BRASIL",
            "NUBANK",
            "INTER",
            "STONE",
            "PAGSEGURO",
            "MERCADO PAGO",
            "PICPAY",
            "NEON",
            "SAFRA",
            "BTG",
            "SICOOB",
            "SICREDI",
        ]

    # --- FUNÇÕES DE VALIDAÇÃO FORENSE ---

    def validar_end_to_end_id_pix(self, hash_pix: str) -> tuple[bool, str, dict]:
        """Valida a estrutura oficial do EndToEndId Pix segundo o Banco Central (32 caracteres)"""
        hash_pix = hash_pix.strip()
        if not re.match(r"^E[a-zA-Z0-9]{31}$", hash_pix):
            return (
                False,
                "ESTRUTURA INVÁLIDA (Deve iniciar com 'E' e ter 32 caracteres)",
                {},
            )

        ispb = hash_pix[1:9]
        data_str = hash_pix[9:17]
        hora_str = hash_pix[17:21]

        try:
            data_obj = datetime.strptime(data_str, "%Y%m%d")
            data_formatada = data_obj.strftime("%d/%m/%Y")
        except ValueError:
            return False, f"DATA CORROMPIDA NO HASH ({data_str})", {}

        try:
            hora = int(hora_str[:2])
            minuto = int(hora_str[2:])
            if not (0 <= hora <= 23 and 0 <= minuto <= 59):
                return False, f"HORA INVÁLIDA NO HASH ({hora_str})", {}
            hora_formatada = f"{hora:02d}:{minuto:02d} UTC"
        except ValueError:
            return False, "COMPONENTE DE TEMPO INVÁLIDO", {}

        detalhes = {
            "ispb": ispb,
            "data": data_formatada,
            "hora": hora_formatada,
        }

        msg = f"VÁLIDO (ISPB: {ispb} | Timestamp UTC: {data_formatada} às {hora_formatada})"
        return True, msg, detalhes

    def validar_cpf(self, cpf: str) -> bool:
        """Valida se o CPF é matematicamente verdadeiro (Módulo 11)"""
        numeros = [int(digit) for digit in cpf if digit.isdigit()]
        if len(numeros) != 11 or len(set(numeros)) == 1:
            return False

        soma = sum(a * b for a, b in zip(numeros[:9], range(10, 1, -1)))
        digito_1 = (soma * 10 % 11) % 10
        if digito_1 != numeros[9]:
            return False

        soma = sum(a * b for a, b in zip(numeros[:10], range(11, 1, -1)))
        digito_2 = (soma * 10 % 11) % 10
        return digito_2 == numeros[10]

    def validar_cnpj(self, cnpj: str) -> bool:
        """Valida se o CNPJ é matematicamente verdadeiro (Módulo 11)"""
        numeros = [int(digit) for digit in cnpj if digit.isdigit()]
        if len(numeros) != 14 or len(set(numeros)) == 1:
            return False

        pesos_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(a * b for a, b in zip(numeros[:12], pesos_1))
        resto = soma % 11
        digito_1 = 0 if resto < 2 else 11 - resto
        if digito_1 != numeros[12]:
            return False

        pesos_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
        soma = sum(a * b for a, b in zip(numeros[:13], pesos_2))
        resto = soma % 11
        digito_2 = 0 if resto < 2 else 11 - resto
        return digito_2 == numeros[13]

    def validar_documento(self, doc_str: str) -> tuple[str, str]:
        """Identifica o tipo de documento, detecta máscaras LGPD ou aplica validação matemática"""
        if "*" in doc_str or "x" in doc_str.lower():
            if "/" in doc_str or len(re.sub(r"[^\d\*xX]", "", doc_str)) == 14:
                return "CNPJ", "MASCARADO (LGPD)"
            return "CPF", "MASCARADO (LGPD)"

        apenas_numeros = re.sub(r"\D", "", doc_str)
        if len(apenas_numeros) == 11:
            valido = self.validar_cpf(apenas_numeros)
            return "CPF", "VÁLIDO" if valido else "INVÁLIDO (FALSO)"
        elif len(apenas_numeros) == 14:
            valido = self.validar_cnpj(apenas_numeros)
            return "CNPJ", "VÁLIDO" if valido else "INVÁLIDO (FALSO)"

        return "DESCONHECIDO", "FORMATO INCORRETO"

    # --- EXTRAÇÃO E PARSER DE TEXTO ---

    def extrair_dados_texto(self, texto, identificador_fonte="Entrada Manual"):
        dados = {
            "fonte": identificador_fonte,
            "nome_beneficiario": "NÃO IDENTIFICADO",
            "id_transacao_hash": "NÃO IDENTIFICADO",
            "hash_pix_valido": "N/A",
            "destino_cnpj_cpf": "NÃO IDENTIFICADO",
            "doc_tipo": "N/A",
            "doc_valido": "N/A",
            "instituicao_destino": "NÃO IDENTIFICADO",
            "valor": "NÃO IDENTIFICADO",
            "data": "NÃO IDENTIFICADO",
        }

        # 1. Captura do Nome do Beneficiário / Favorecido
        padroes_nome = [
            r"(?:Beneficiário|Beneficiario|Favorecido|Destinatário|Destinatario|Recebedor|Para):\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]{3,50})",
            r"(?:Nome do Favorecido|Nome do Recebedor|Nome):\s*([A-Za-zÀ-ÖØ-öø-ÿ\s]{3,50})",
        ]

        for padrao in padroes_nome:
            nome_match = re.search(padrao, texto, re.IGNORECASE)
            if nome_match:
                nome_bruto = nome_match.group(1).strip()
                nome_limpo = re.split(r"[\n\r]", nome_bruto)[0].strip()
                if len(nome_limpo) > 2:
                    dados["nome_beneficiario"] = nome_limpo.upper()
                    break

        # 2. Captura e Validação do ID Pix / Hash
        hash_capturado = None
        id_pix_match = re.search(r"\b(E[A-Za-z0-9]{31})\b", texto)

        if id_pix_match:
            hash_capturado = id_pix_match.group(1).strip()
        else:
            autenticacao_match = re.search(
                r"(?:Autenticação|Controle|Transação|ID|Autenticacao):\s*([A-Za-z0-9\.\-\s]{15,})",
                texto,
                re.IGNORECASE,
            )
            if autenticacao_match:
                hash_capturado = (
                    autenticacao_match.group(1).replace("\n", "").strip()
                )

        if hash_capturado:
            dados["id_transacao_hash"] = hash_capturado
            if hash_capturado.startswith("E") and len(hash_capturado) == 32:
                valido, msg_detalhe, _ = self.validar_end_to_end_id_pix(
                    hash_capturado
                )
                dados["hash_pix_valido"] = msg_detalhe
            else:
                dados["hash_pix_valido"] = "CÓDIGO DE AUTENTICAÇÃO GENÉRICO"

        # 3. Captura e Validação de CNPJ ou CPF
        cnpj_cpf_regex = r"\b([\d\*xX]{2,3}\.[\d\*xX]{3}\.[\d\*xX]{3}[\-/][\d\*xX]{2,4}[\-]?[\d\*xX]{0,2})\b"
        doc_match = re.search(cnpj_cpf_regex, texto)

        if doc_match:
            doc_encontrado = doc_match.group(1)
            dados["destino_cnpj_cpf"] = doc_encontrado
            tipo_doc, status_valida = self.validar_documento(doc_encontrado)
            dados["doc_tipo"] = tipo_doc
            dados["doc_valido"] = status_valida

        # 4. Valor Financeiro
        valor_match = re.search(
            r"(?:Valor|Total|Quantia)[^\d]*R\$\s*([\d\.,]+)", texto, re.IGNORECASE
        )
        if not valor_match:
            valor_match = re.search(r"R\$\s*([\d\.,]+)", texto)
        if valor_match:
            dados["valor"] = valor_match.group(1).strip()

        # 5. Data
        data_match = re.search(r"\b(\d{2}/\d{2}/\d{4})\b", texto)
        if data_match:
            dados["data"] = data_match.group(1)

        # 6. Instituição Financeira
        for banco in self.padroes_bancos:
            if re.search(rf"\b{banco}\b", texto, re.IGNORECASE):
                dados["instituicao_destino"] = banco
                break

        return dados

    # --- ENTRADA DIRETA VIA INPUT DE HASH E NOME ---

    def processar_entrada_direta_hash_nome(self):
        print("\n" + "=" * 60)
        print("ENTRADA DIRETA DE DADOS FORENSES (HASH + RECEPTOR)")
        print("=" * 60)

        hash_input = input("\n[>] Digite/Cole o Hash Pix (EndToEndId): ").strip()
        nome_input = input("[>] Digite o Nome do Receptor/Beneficiário: ").strip()
        banco_input = input("[>] Digite o Banco de Destino (Opcional): ").strip()
        cpf_mascarado_input = input(
            "[>] Digite o CPF Mascarado/Parcial se houver (Opcional): "
        ).strip()

        valido, msg_detalhe, detalhes = self.validar_end_to_end_id_pix(hash_input)

        dados = {
            "fonte": "Entrada Direta via Terminal",
            "nome_beneficiario": nome_input.upper() if nome_input else "NÃO INFORMADO",
            "id_transacao_hash": hash_input,
            "hash_pix_valido": msg_detalhe,
            "destino_cnpj_cpf": (
                cpf_mascarado_input if cpf_mascarado_input else "MASCARADO (LGPD)"
            ),
            "doc_tipo": "CPF" if cpf_mascarado_input else "N/A",
            "doc_valido": "MASCARADO (LGPD)",
            "instituicao_destino": (
                banco_input.upper() if banco_input else "NÃO INFORMADO"
            ),
            "valor": "CONSULTAR COMPROVANTE",
            "data": detalhes.get("data", "VERIFICAR NO HASH"),
        }

        self.transacoes_extraidas.append(dados)

        print("\n--- ANÁLISE FORENSE DA ENTRADA ---")
        print(f" -> Receptor / Titular: {dados['nome_beneficiario']}")
        print(f" -> Hash Pix (EndToEndId): {dados['id_transacao_hash']}")
        print(f" -> Status da Validação: {dados['hash_pix_valido']}")
        if detalhes:
            print(f" -> ISPB Banco de Origem: {detalhes['ispb']}")
            print(f" -> Data Registrada no Hash: {detalhes['data']}")
            print(f" -> Horário UTC Registrado: {detalhes['hora']}")

        print("\n" + "-" * 60)
        print("TEXTO DE FUNDAMENTAÇÃO PRONTO PARA O BOLETIM DE OCORRÊNCIA / RELATÓRIO:")
        print("-" * 60)
        print(
            f"O requerente identifica a transação financeira de destino através do "
            f"EndToEndId (Hash Pix) nº {dados['id_transacao_hash']}, vinculado ao titular "
            f"declarado como {dados['nome_beneficiario']}. O referido Hash atesta a "
            f"materialidade da transferência realizada em {dados['data']}.\n"
            f"Diante da ocultação parcial dos dígitos do CPF por imposição de privacidade "
            f"bancária (LGPD), solicita-se a requisição formal ao Banco Central do Brasil "
            f"(via SPI/SISBAJUD/SISTECRED) para que forneça a qualificação cadastral integral "
            f"(CPF/CNPJ completo, endereço e dados bancários) atrelada ao EndToEndId informado."
        )
        print("-" * 60)

    def salvar_csv(self, nome_arquivo_csv):
        if not self.transacoes_extraidas:
            return

        campos = [
            "fonte",
            "data",
            "nome_beneficiario",
            "instituicao_destino",
            "destino_cnpj_cpf",
            "doc_tipo",
            "doc_valido",
            "valor",
            "id_transacao_hash",
            "hash_pix_valido",
        ]

        with open(nome_arquivo_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=campos, delimiter=";")
            writer.writeheader()
            writer.writerows(self.transacoes_extraidas)

    def executar_fluxo(self):
        print("=" * 60)
        print("PARSER FORENSE BANCÁRIO & INVESTIGAÇÃO DE CHAVE HASH")
        print("=" * 60)

        while True:
            print("\n[1] Cole o texto completo do comprovante no terminal")
            print("[2] Processar um arquivo de texto (.txt)")
            print("[3] Cruzar Comprovantes Extraídos com Base de Suspeitos")
            print("[4] Consulta/Validação Manual via Hash + Nome do Receptor")
            print("[0] Sair e gerar relatórios (JSON e CSV/Excel)")

            opcao = input("\n[>] Escolha uma opção: ").strip()

            if opcao == "1":
                print(
                    "\n[+] Cole o texto do comprovante (ENTER em linha vazia para finalizar):"
                )
                linhas = []
                while True:
                    linha = input()
                    if linha == "":
                        break
                    linhas.append(linha)

                texto_bruto = "\n".join(linhas)
                if not texto_bruto.strip():
                    print("[!] Nenhum texto foi colado.")
                    continue

                dados = self.extrair_dados_texto(
                    texto_bruto,
                    identificador_fonte="Entrada Manual via Terminal",
                )

                print("\n--- DADOS EXTRAÍDOS ---")
                print(f" -> Beneficiário: {dados['nome_beneficiario']}")
                print(f" -> Banco Destino: {dados['instituicao_destino']}")
                print(
                    f" -> Documento ({dados['doc_tipo']}): {dados['destino_cnpj_cpf']} [{dados['doc_valido']}]"
                )
                print(
                    f" -> ID / Hash Pix: {dados['id_transacao_hash']} [{dados['hash_pix_valido']}]"
                )
                print(f" -> Valor Extraído: R$ {dados['valor']}")
                print(f" -> Data: {dados['data']}")

                self.transacoes_extraidas.append(dados)

            elif opcao == "2":
                caminho_txt = input("\n[>] Digite o caminho do arquivo .txt: ").strip()
                if not os.path.exists(caminho_txt):
                    print("[!] Arquivo não encontrado.")
                    continue

                with open(caminho_txt, "r", encoding="utf-8") as f:
                    conteudo = f.read()

                dados = self.extrair_dados_texto(
                    conteudo,
                    identificador_fonte=os.path.basename(caminho_txt),
                )

                print("\n--- DADOS EXTRAÍDOS ---")
                print(f" -> Beneficiário: {dados['nome_beneficiario']}")
                print(f" -> Banco Destino: {dados['instituicao_destino']}")
                print(
                    f" -> Documento ({dados['doc_tipo']}): {dados['destino_cnpj_cpf']} [{dados['doc_valido']}]"
                )
                print(
                    f" -> ID / Hash Pix: {dados['id_transacao_hash']} [{dados['hash_pix_valido']}]"
                )
                print(f" -> Valor Extraído: R$ {dados['valor']}")
                print(f" -> Data: {dados['data']}")

                self.transacoes_extraidas.append(dados)

            elif opcao == "3":
                if not self.transacoes_extraidas:
                    print(
                        "\n[!] Processe ou insira pelo menos uma transação antes de realizar o cruzamento."
                    )
                    continue

                base_suspeitos_exemplo = [
                    {
                        "nome": "JOAO DA SILVA GOLPE",
                        "cpf": "123.456.789-00",
                        "banco": "NUBANK",
                    },
                    {
                        "nome": "MARIA FAKE SANTOS",
                        "cpf": "987.654.321-11",
                        "banco": "BRADESCO",
                    },
                ]

                cruzador = CruzadorSuspeitosForense(base_suspeitos_exemplo)
                cruzador.executar_cruzamento(self.transacoes_extraidas)

            elif opcao == "4":
                self.processar_entrada_direta_hash_nome()

            elif opcao == "0":
                if not self.transacoes_extraidas:
                    print("\n[!] Nenhuma transação foi processada.")
                    break

                nome_base = input("\n[>] Digite o nome base dos relatórios: ").strip()
                if nome_base.endswith(".json") or nome_base.endswith(".csv"):
                    nome_base = os.path.splitext(nome_base)[0]

                nome_json = f"{nome_base}.json"
                nome_csv = f"{nome_base}.csv"

                relatorio_final = {
                    "meta_analise": {
                        "timestamp_execucao": datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "metodologia": "Parser Forense com Detecção de Máscara LGPD, Captura de Beneficiário, Módulo 11 (CPF/CNPJ) e Estrutura Bacen (EndToEndId)",
                    },
                    "rastreamento_fluxo_destino": self.transacoes_extraidas,
                }

                with open(nome_json, "w", encoding="utf-8") as f:
                    json.dump(relatorio_final, f, indent=4, ensure_ascii=False)

                self.salvar_csv(nome_csv)

                print(
                    f"\n[+] Relatórios gerados com sucesso:\n    - JSON: {nome_json}\n    - CSV/Excel: {nome_csv}"
                )
                break
            else:
                print("[!] Opção inválida.")


# --- CLASSE DE CRUZAMENTO BI-FACTORIAL DE SUSPEITOS ---


class CruzadorSuspeitosForense:

    def __init__(self, lista_suspeitos: list):
        self.lista_suspeitos = lista_suspeitos

    def comparar_cpf_mascarado(self, cpf_mascarado: str, cpf_suspeito: str) -> bool:
        mask_clean = re.sub(r"[^\d\*xX]", "", cpf_mascarado)
        susp_clean = re.sub(r"\D", "", cpf_suspeito)

        if len(mask_clean) != len(susp_clean):
            return False

        for char_mask, char_susp in zip(mask_clean, susp_clean):
            if char_mask not in ["*", "x", "X"]:
                if char_mask != char_susp:
                    return False
        return True

    def comparar_banco(self, banco_comprovante: str, banco_suspeito: str) -> bool:
        if (
            banco_comprovante == "NÃO IDENTIFICADO"
            or not banco_comprovante
            or not banco_suspeito
        ):
            return False

        b_comp = banco_comprovante.upper()
        b_susp = banco_suspeito.upper()

        return b_comp in b_susp or b_susp in b_comp

    def executar_cruzamento(self, transacoes: list):
        print("\n" + "=" * 60)
        print("RESULTADO DO CRUZAMENTO DE SEGURANÇA (CPF + BANCO DESTINO)")
        print("=" * 60)

        match_encontrado = False

        for idx, tx in enumerate(transacoes, 1):
            cpf_comp = tx.get("destino_cnpj_cpf", "")
            banco_comp = tx.get("instituicao_destino", "")
            nome_comp = tx.get("nome_beneficiario", "NÃO IDENTIFICADO")

            print(
                f"\n[Transação #{idx}] Fonte: {tx['fonte']} | Beneficiário: {nome_comp} | Banco: {banco_comp} | Doc: {cpf_comp}"
            )

            for suspeito in self.lista_suspeitos:
                cpf_match = self.comparar_cpf_mascarado(cpf_comp, suspeito["cpf"])
                banco_match = self.comparar_banco(banco_comp, suspeito["banco"])

                if cpf_match and banco_match:
                    match_encontrado = True
                    print(f"  [!!!] ALERTA DE MATCH CONFIRMADO (ALTA FIDELIDADE):")
                    print(f"        -> Suspeito: {suspeito['nome']}")
                    print(f"        -> CPF Completo: {suspeito['cpf']}")
                    print(f"        -> Banco Registrado: {suspeito['banco']}")
                elif cpf_match and not banco_match:
                    print(
                        f"  [?] COINCIDÊNCIA PARCIAL (ALERTA DE FALSO POSITIVO DESCARTADO):"
                    )
                    print(
                        f"        -> Suspeito {suspeito['nome']} tem CPF compatível, mas opera no banco '{suspeito['banco']}'."
                    )

        if not match_encontrado:
            print("\n[-] Nenhum suspeito atendeu aos 2 critérios simultâneos.")


if __name__ == "__main__":
    rastreador = RastreadorFinanceiroForenseTexto()
    rastreador.executar_fluxo()
