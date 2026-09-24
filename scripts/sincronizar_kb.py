import os
import json
import time
import requests

# Pega o token do Movidesk através das variáveis de ambiente do GitHub Actions
MOVIDESK_TOKEN = os.getenv("MOVIDESK_TOKEN")

BASE_URL = "https://api.movidesk.com/public/v1"


def buscar_lista_artigos():
    """
    Busca a lista resumida de artigos (paginada) no endpoint de pesquisa.
    Retorna uma lista de dicts simplificados (sem o conteúdo completo).
    """
    if not MOVIDESK_TOKEN:
        print("Erro: MOVIDESK_TOKEN não configurado.")
        return []

    todos_items = []
    page = 0
    page_size = 50

    while True:
        url = f"{BASE_URL}/kb/article"
        params = {
            "token": MOVIDESK_TOKEN,
            "status": 1,  # 1 = Publicado. Remova este filtro se quiser incluir suspensos (4) também.
            "pageSize": page_size,
            "page": page,
        }

        try:
            response = requests.get(url, params=params, timeout=30)
        except Exception as e:
            print(f"Erro ao conectar com a API (lista, página {page}): {e}")
            break

        if response.status_code != 200:
            print(f"Erro na API do Movidesk (lista, página {page}): {response.status_code} - {response.text[:500]}")
            break

        dados = response.json()
        items = dados.get("items", [])
        total_size = dados.get("totalSize", 0)

        todos_items.extend(items)
        print(f"Página {page}: {len(items)} artigos recebidos (total esperado: {total_size}).")

        if len(items) < page_size or len(todos_items) >= total_size:
            break

        page += 1
        time.sleep(1)  # Respeita o limite de 10 requisições por minuto da API

    return todos_items


def buscar_conteudo_artigo(article_id):
    """
    Busca o artigo completo (com contentHtml) por ID.
    """
    url = f"{BASE_URL}/article/{article_id}"
    params = {"token": MOVIDESK_TOKEN}

    try:
        response = requests.get(url, params=params, timeout=30)
    except Exception as e:
        print(f"Erro ao buscar conteúdo do artigo {article_id}: {e}")
        return None

    if response.status_code != 200:
        print(f"Erro ao buscar artigo {article_id}: {response.status_code} - {response.text[:300]}")
        return None

    return response.json()


def buscar_artigos_movidesk():
    lista_resumida = buscar_lista_artigos()
    if not lista_resumida:
        return []

    artigos_formatados = []

    for item in lista_resumida:
        article_id = item.get("id")

        # Busca o conteúdo completo do artigo (respeitando o limite de 10 req/min)
        detalhe = buscar_conteudo_artigo(article_id)
        time.sleep(6.5)  # ~9 requisições por minuto, com margem de segurança

        # Categoria: pode vir como lista de objetos {id, name}
        categorias = item.get("category") or []
        categoria_nome = categorias[0]["name"] if categorias else "Geral"

        conteudo = (
            detalhe.get("contentHtml")
            if detalhe
            else item.get("summary", "Conteúdo indisponível.")
        )

        artigos_formatados.append({
            "id": article_id,
            "title": item.get("title"),
            "category": categoria_nome,
            "createdDate": item.get("createdAt"),
            "updatedDate": item.get("updatedAt"),
            "content": conteudo or "Conteúdo indisponível.",
        })

    return artigos_formatados


if __name__ == "__main__":
    print("Iniciando sincronização com a base de conhecimento do Movidesk...")
    artigos = buscar_artigos_movidesk()

    output_path = "artigos.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(artigos, f, ensure_ascii=False, indent=4)

    print(f"Sucesso! {len(artigos)} artigos salvos em {output_path}.")
