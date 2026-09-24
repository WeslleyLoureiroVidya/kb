import os
import json
import requests

MOVIDESK_TOKEN = os.getenv("MOVIDESK_TOKEN")
# Substitua pelo endereço do seu Movidesk (ex: https://suaempresa.movidesk.com)
MOVIDESK_BASE_URL = "https://vidya-code.movidesk.com" 

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
                conteudo = artigo.get("body", "")
                
                # CORREÇÃO DE IMAGENS: Se o link da imagem vier relativo (ex: /file/download?...),
                # adicionamos o domínio do Movidesk na frente para o navegador conseguir carregar.
                if conteudo:
                    conteudo = conteudo.replace('src="/', f'src="{MOVIDESK_BASE_URL}/')
                    conteudo = conteudo.replace("src='/", f"src='{MOVIDESK_BASE_URL}/")

                artigos_formatados.append({
                    "id": artigo.get("id"),
                    "title": artigo.get("title"),
                    "category": artigo.get("category"),
                    "createdDate": artigo.get("createdDate"),
                    "content": conteudo 
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
