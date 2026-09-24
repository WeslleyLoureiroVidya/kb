import os
import json
import requests

# Pega o token do Movidesk através das variáveis de ambiente do GitHub Actions
MOVIDESK_TOKEN = os.getenv("MOVIDESK_TOKEN")

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
            
            # Ajuste os campos conforme o retorno exato da API do Movidesk
            for artigo in dados:
                artigos_formatados.append({
                    "id": artigo.get("id"),
                    "title": artigo.get("title"),
                    "category": artigo.get("category"),
                    "createdDate": artigo.get("createdDate"),
                    # Aqui você pode puxar o corpo/resumo do artigo se disponível na API
                    "content": artigo.get("body", "Conteúdo restrito ou indisponível na listagem resumida.") 
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
    
    # Salva os artigos em um arquivo JSON na raiz do projeto (ou numa pasta publica)
    output_path = "artigos.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artigos, f, ensure_ascii=False, indent=4)
        
    print(f"Sucesso! {len(artigos)} artigos salvos em {output_path}.")
