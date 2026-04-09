import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse
from deep_translator import GoogleTranslator

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

LINKS_FIXOS = [
    "https://apnews.com/article/iran-us-pilot-military-rescue-fde473d07fb59e871a71cd2ad2ffe4fe",
    "https://apnews.com/hub/elections",
    "https://apnews.com/projects/polling-tracker/",
    "https://apnews.com/hub/donald-trump",
    "https://apnews.com/hub/iran",
    "https://apnews.com/hub/russia-ukraine",
    "https://apnews.com/article/hungary-cut-gas-supplies-ukraine-russian-oil-dispute-4a8e4c31c5f10b768edba145b9fc1d4e"
]

STOPWORDS_PT = {
    "a", "o", "e", "de", "da", "do", "em", "um", "uma", "para", "pra",
    "com", "que", "os", "as", "na", "no", "por", "mais", "muito", "muita",
    "não", "nao", "mas", "como", "isso", "essa", "esse", "dos", "das",
    "foi", "ser", "ter", "ao", "até", "ate", "se", "sem", "já", "ja",
    "sobre", "entre", "também", "tambem", "após", "apos", "desde", "quando",
    "ele", "ela", "eles", "elas", "seu", "sua", "seus", "suas"
}

PADROES_REMOVER = [
    r"copyright the associated press all rights reserved",
    r"all rights reserved",
    r"associated press",
    r"ap photo",
    r"photo\s+[a-zà-ú0-9\s\-\.\,\/]+",
    r"video\s+[a-zà-ú0-9\s\-\.\,\/]+",
    r"this image provided by.*",
    r"follow ap.?s coverage.*",
    r"the associated press receives support.*",
]

def eh_artigo(url: str) -> bool:
    return "/article/" in url

def eh_hub(url: str) -> bool:
    return "/hub/" in url

def eh_project(url: str) -> bool:
    return "/projects/" in url

def limpar_texto(texto: str) -> str:
    texto = texto.lower()

    for padrao in PADROES_REMOVER:
        texto = re.sub(padrao, " ", texto, flags=re.IGNORECASE)

    texto = re.sub(r"http\S+|www\S+", " ", texto)
    texto = re.sub(r"\d+", " ", texto)
    texto = re.sub(r"[^\w\s]", " ", texto)
    texto = re.sub(r"_", " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()

    return texto

def remover_stopwords(texto: str) -> str:
    palavras = texto.split()
    filtradas = [p for p in palavras if p not in STOPWORDS_PT and len(p) > 2]
    return " ".join(filtradas)

def traduzir_texto_grande(texto: str, tamanho_bloco: int = 4000) -> str:
    if not texto.strip():
        return ""

    partes = [texto[i:i + tamanho_bloco] for i in range(0, len(texto), tamanho_bloco)]
    traducao_final = []

    for i, parte in enumerate(partes, start=1):
        try:
            print(f"  Traduzindo bloco {i}/{len(partes)}...")
            traducao = GoogleTranslator(source="auto", target="pt").translate(parte)
            traducao_final.append(traducao if traducao else parte)
            time.sleep(0.5)
        except Exception as e:
            print(f"  Erro na tradução do bloco {i}: {e}")
            traducao_final.append(parte)

    return " ".join(traducao_final)

def baixar_html(url: str):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def normalizar_link(href: str) -> str:
    if not href:
        return ""
    href = href.strip()
    if href.startswith("/"):
        return urljoin("https://apnews.com", href)
    return href

def extrair_links_artigos_da_pagina(url: str, limite_links: int = 12):
    """
    Para páginas /hub/ e /projects/, coleta apenas links de /article/.
    """
    print(f"Coletando links internos de artigos: {url}")
    soup = baixar_html(url)

    links = []
    vistos = set()

    for a in soup.find_all("a", href=True):
        href = normalizar_link(a["href"])

        if not href.startswith("https://apnews.com"):
            continue

        if "/article/" not in href:
            continue

        # evita duplicatas
        if href in vistos:
            continue

        vistos.add(href)
        links.append(href)

    print(f"  Artigos encontrados: {len(links)}")
    return links[:limite_links]

def extrair_texto_artigo(url: str):
    try:
        soup = baixar_html(url)

        titulo = soup.title.get_text(" ", strip=True) if soup.title else ""

        paragrafos = []
        for p in soup.find_all("p"):
            texto = p.get_text(" ", strip=True)
            if len(texto) >= 40:
                paragrafos.append(texto)

        if not paragrafos:
            print(f"Sem conteúdo textual útil no artigo: {url}")
            return None

        corpo = " ".join(paragrafos)
        texto_final = f"{titulo}\n{corpo}".strip()

        return {
            "url": url,
            "titulo": titulo,
            "texto_original": texto_final,
            "tipo_origem": "article"
        }

    except Exception as e:
        print(f"Erro ao extrair artigo {url}: {e}")
        return None

def extrair_texto_project(url: str):
    """
    Extrai texto direto de /projects/ quando houver conteúdo útil.
    """
    try:
        soup = baixar_html(url)
        titulo = soup.title.get_text(" ", strip=True) if soup.title else ""

        paragrafos = []
        for p in soup.find_all("p"):
            texto = p.get_text(" ", strip=True)
            if len(texto) >= 40:
                paragrafos.append(texto)

        if not paragrafos:
            return None

        corpo = " ".join(paragrafos)
        texto_final = f"{titulo}\n{corpo}".strip()

        return {
            "url": url,
            "titulo": titulo,
            "texto_original": texto_final,
            "tipo_origem": "project"
        }

    except Exception as e:
        print(f"Erro ao extrair project {url}: {e}")
        return None

def deduplicar_registros(registros):
    vistos = set()
    saida = []

    for item in registros:
        chave = limpar_texto(item["texto_original"])[:600]
        if chave not in vistos:
            vistos.add(chave)
            saida.append(item)

    return saida

def salvar_txt_bruto(registros, caminho_saida="noticias_brutas.txt"):
    with open(caminho_saida, "w", encoding="utf-8") as f:
        for i, item in enumerate(registros, start=1):
            f.write(f"[DOC_{i}]\n")
            f.write(f"TIPO: {item.get('tipo_origem', 'desconhecido')}\n")
            f.write(f"URL: {item['url']}\n")
            f.write(f"TITULO: {item['titulo']}\n")
            f.write(item["texto_original"])
            f.write("\n\n" + "=" * 80 + "\n\n")

    print(f"TXT bruto salvo em: {caminho_saida}")

def salvar_txt_traduzido(registros, caminho_saida="noticias_traduzidas.txt"):
    with open(caminho_saida, "w", encoding="utf-8") as f:
        for i, item in enumerate(registros, start=1):
            f.write(f"[DOC_{i}]\n")
            f.write(f"TIPO: {item.get('tipo_origem', 'desconhecido')}\n")
            f.write(f"URL: {item['url']}\n")
            f.write(f"TITULO: {item['titulo']}\n")
            f.write(item.get("texto_traduzido", ""))
            f.write("\n\n" + "=" * 80 + "\n\n")

    print(f"TXT traduzido salvo em: {caminho_saida}")

def salvar_corpus_processado(registros, caminho_saida="corpus_processado.txt"):
    with open(caminho_saida, "w", encoding="utf-8") as f:
        for item in registros:
            texto = item.get("texto_traduzido", "").strip()
            if not texto:
                continue

            texto_limpo = limpar_texto(texto)
            texto_limpo = remover_stopwords(texto_limpo)

            if len(texto_limpo.split()) >= 8:
                f.write(texto_limpo + "\n")

    print(f"Corpus processado salvo em: {caminho_saida}")

def expandir_links_iniciais(links_iniciais, limite_por_hub=8, limite_por_project=6):
    """
    Converte hub/project em artigos internos + mantém artigos diretos.
    """
    links_finais = []
    vistos = set()

    for url in links_iniciais:
        try:
            if eh_artigo(url):
                if url not in vistos:
                    vistos.add(url)
                    links_finais.append(url)

            elif eh_hub(url):
                artigos = extrair_links_artigos_da_pagina(url, limite_links=limite_por_hub)
                for art in artigos:
                    if art not in vistos:
                        vistos.add(art)
                        links_finais.append(art)

            elif eh_project(url):
                # tenta guardar o próprio project
                if url not in vistos:
                    vistos.add(url)
                    links_finais.append(url)

                # e também procura artigos internos
                artigos = extrair_links_artigos_da_pagina(url, limite_links=limite_por_project)
                for art in artigos:
                    if art not in vistos:
                        vistos.add(art)
                        links_finais.append(art)

            else:
                if url not in vistos:
                    vistos.add(url)
                    links_finais.append(url)

            time.sleep(0.5)

        except Exception as e:
            print(f"Erro ao expandir {url}: {e}")

    return links_finais

def coletar_registros(links_expandidos):
    registros = []

    for i, url in enumerate(links_expandidos, start=1):
        print(f"\nProcessando {i}/{len(links_expandidos)}")
        print(url)

        item = None

        if eh_artigo(url):
            item = extrair_texto_artigo(url)
        elif eh_project(url):
            item = extrair_texto_project(url)
        else:
            # fallback
            item = extrair_texto_artigo(url)

        if item:
            print("Extração OK")
            registros.append(item)
        else:
            print("Falha ao extrair")

        time.sleep(0.5)

    return registros

def executar_pipeline():
    print("Expandindo hubs e projects em links úteis...\n")
    links_expandidos = expandir_links_iniciais(LINKS_FIXOS)

    print(f"\nTotal de links finais para extração: {len(links_expandidos)}")
    for link in links_expandidos:
        print(link)

    registros = coletar_registros(links_expandidos)
    registros = deduplicar_registros(registros)

    print(f"\nTotal de documentos válidos após deduplicação: {len(registros)}")

    if not registros:
        print("Nenhum conteúdo válido foi extraído.")
        return

    salvar_txt_bruto(registros, "noticias_brutas.txt")

    print("\nIniciando tradução para português...\n")
    for i, item in enumerate(registros, start=1):
        print(f"Traduzindo documento {i}/{len(registros)}")
        item["texto_traduzido"] = traduzir_texto_grande(item["texto_original"])

    salvar_txt_traduzido(registros, "noticias_traduzidas.txt")
    salvar_corpus_processado(registros, "corpus_processado.txt")

    print("\nPipeline finalizado com sucesso.")

if __name__ == "__main__":
    executar_pipeline()