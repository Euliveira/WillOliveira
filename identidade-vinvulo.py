import os
import subprocess
import sys
import webbrowser


def banner():
    print("\n" + "=" * 60)
    print("     SISTEMA CENTRALIZADO DE INVESTIGAÇÃO DE VÍNCULOS")
    print("         Interface Automática para Engine Maigret")
    print("=" * 60)


def menu():
    banner()
    print("[1] Rastrear Username (Gerar Relatório Completo HTML)")
    print("[2] Rastrear Username (Modo Rápido - Apenas Redes Comuns)")
    print("[3] Abrir Pasta de Relatórios Gerados")
    print("[0] Sair do Sistema")
    print("=" * 60)


def verificar_maigret():
    """Verifica se o Maigret está instalado no ambiente Python."""
    try:
        # Tenta rodar o comando de ajuda do maigret em segundo plano
        subprocess.run(
            ["maigret", "--help"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except FileNotFoundError:
        return False


def executar_maigret(modo_completo=True):
    if not verificar_maigret():
        print("\n[!] Erro: O Maigret não está instalado ou não está no PATH.")
        print(" -> Execute no seu terminal: pip install maigret")
        return

    username = input("\nDigite o username do alvo (ex: @joao_silva): ").strip()
    # Remove o '@' caso o usuário digite com ele
    username = username.replace("@", "")

    if not username:
        print("[-] Username inválido.")
        return

    print(f"\n[+] Iniciando varredura global para: {username}")
    print("[*] Isso pode levar alguns minutos dependendo da rede...")

    # Define os parâmetros do comando
    # -H gera o relatório HTML interativo com gráficos
    comando = ["maigret", username, "-H"]

    if not modo_completo:
        # Limita a busca aos top sites para ser mais rápido
        comando.extend(["--tags", "social"])

    try:
        # Executa o Maigret e mostra a saída do terminal em tempo real
        subprocess.run(comando, check=True)

        print(f"\n[✓] Varredura concluída para {username}!")

        # O Maigret salva os relatórios em uma pasta com o nome do usuário
        caminho_relatorio = os.path.join(
            f"reports_{username}", f"report_{username}.html"
        )

        if os.path.exists(caminho_relatorio):
            print(f"[+] Abrindo relatório visual no navegador...")
            webbrowser.open(os.path.abspath(caminho_relatorio))
        else:
            print(
                "[!] Varredura concluída, mas o relatório HTML não foi gerado (nenhum perfil público encontrado)."
            )

    except subprocess.CalledProcessError as e:
        print(f"[-] Erro durante a execução do Maigret: {e}")


def abrir_pasta_reports():
    diretorio_atual = os.getcwd()
    print(f"\n[*] Abrindo diretório de trabalho: {diretorio_atual}")
    # Abre o gerenciador de arquivos dependendo do Sistema Operacional
    if sys.platform == "win32":
        os.startfile(diretorio_atual)
    elif sys.platform == "darwin":
        subprocess.run(["open", diretorio_atual])
    else:
        subprocess.run(["xdg-open", diretorio_atual])


def main():
    # Garante que a pasta onde o script roda é o diretório de trabalho atual
    while True:
        menu()
        opcao = input("Escolha uma opção de análise: ").strip()

        if opcao == "1":
            executar_maigret(modo_completo=True)
        elif opcao == "2":
            executar_maigret(modo_completo=False)
        elif opcao == "3":
            abrir_pasta_reports()
        elif opcao == "0":
            print("\n[!] Encerrando sistema de investigação.")
            break
        else:
            print("\n[-] Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()