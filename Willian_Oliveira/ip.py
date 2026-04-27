import requests

def buscar_geolocalizacao():                                                                                                                                                            print("=== Willtech Solutions - IP Tracker OSINT ===")

    # Entrada do usuário                                                                                                                                                                ip_alvo = input("🔍 Digite o endereço IP para rastrear: ").strip()

    # Se o usuário não digitar nada, ele busca o próprio IP da máquina
    url = f"http://ip-api.com/json/{ip_alvo}"

    try:
        response = requests.get(url)
        dados = response.json()

        if dados['status'] == 'success':
            print(f"\n✅ Resultados para o IP: {dados['query']}")
            print("-" * 30)                                                                                                                                                                     print(f"🌍 País:    {dados['country']} ({dados['countryCode']})")
            print(f"🏙️  Cidade:  {dados['city']}")                                                                                                                                               print(f"📍 Região:  {dados['regionName']}")
            print(f"🏢 ISP:     {dados['isp']}")
            print(f"🛰️  Lat/Lon: {dados['lat']}, {dados['lon']}")
            print("-" * 30)

            # Link para o Google Maps caso queira ver no mapa
            print(f"🗺️  Mapa: https://www.google.com/maps?q={dados['lat']},{dados['lon']}")
        else:
            print(f"❌ Erro: Não foi possível localizar o IP '{ip_alvo}'. Verifique se ele é válido.")

    except Exception as e:
        print(f"⚠️ Erro na conexão: {e}")

if __name__ == "__main__":
    buscar_geolocalizacao()




