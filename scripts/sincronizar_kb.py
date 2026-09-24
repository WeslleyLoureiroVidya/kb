import os
import json
import re
import requests

MOVIDESK_TOKEN = os.getenv("MOVIDESK_TOKEN")
# Substitua pelo endereço base do seu Movidesk (ex: https://suaempresa.movidesk.com)
MOVIDESK_BASE_URL = "https://suaempresa.movidesk.com"

def corrigir_urls_imagens(conteudo, token):
    if not conteudo:
        return ""
    
    # 1. Se a imagem apontar para caminhos relativos simples (/file/...), adiciona o domínio base
    conteudo = conteudo.replace('src="/', f'src="{MOVIDESK_BASE_URL}/')
    conteudo = conteudo.replace("src='/", f"src='{MOVIDESK_BASE_URL}/")

    # 2. Converte links internos de armazenamento do Movidesk para a rota oficial de download com token
    # Padrão comum de imagens anexadas no editor interno
    def substituir_src(match):
        url_original = match.group(1)
        # Se já tiver token ou for link externo completo válido, mantém
        if "token=" in url_original:
            return f'src="{url_original}"'
        
        # Se for um link de storage interno sem token, anexa o token da API
        if "/storage/" in url_original or "/file/" in url_original or "id=" in url_original:
            separador = "&" if "?" in url_original else "?"
            return f'src="{url_original}{separador}token={token}"'
        
        return f'src="{url_original}"'

    # Aplica a substituição em todas as tags img src="..."
    conteudo = re.sub(r'src="([^"]+)"', substituir_src, conteudo)
    conteudo = re.sub(r"src='([^']+)'", lambda m: substituir_src(m).replace('src="', "src='").replace('">', "'>"), conteudo)

    return conteudo

def buscar_artigos_movidesk():
    if not MOVIDESK_TOKEN:
        print("Erro: MOVIDESK_TOKEN não configurado.")
        return []

    url = f"https://api.movidesk.com/api/v1/kb/articles?token={MOVIDESK_TOKEN}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            dados = response.json()
            artigos_formatados = []
            
            for artigo in dados:
                conteudo_bruto = artigo.get("body", "")
                conteudo_tratado = corrigir_urls_imagens(conteudo_bruto, MOVIDESK_TOKEN)

                artigos_formatados.append({
                    "id": artigo.get("id"),
                    "title": artigo.get("title"),
                    "category": artigo.get("category"),
                    "createdDate": artigo.get("createdDate"),
                    "content": conteudo_tratado 
                })
            return artigos_formatados
        else:
            print(f"Erro na API do Movidesk: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")
        return []

if __name__ == "__main__":
    print("Iniciando sincronização com a base de conhecimento do Movidesk...")
    artigos = buscar_artigos_movidesk()
    
    output_path = "artigos.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artigos, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(artigos)} artigos salvos em {output_path}.")
