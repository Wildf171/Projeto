import pandas as pd
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans


def carregar_corpus(caminho_arquivo):
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        documentos = [linha.strip() for linha in f if linha.strip()]
    return documentos


def extrair_palavras(texto):
    return re.findall(r'\b[a-zà-ú]+\b', texto.lower())


def palavras_mais_importantes_por_cluster(df, n=10):
    resultado = {}

    for cluster in sorted(df["cluster"].unique()):
        textos = " ".join(df[df["cluster"] == cluster]["texto"])
        palavras = extrair_palavras(textos)
        frequencia = Counter(palavras).most_common(n)
        resultado[cluster] = frequencia

    return resultado


def sugerir_nome_cluster(palavras_frequentes):
    palavras = [palavra for palavra, _ in palavras_frequentes]

    if any(p in palavras for p in ["ucrânia", "ucrania", "rússia", "russia", "gás", "gas", "energia", "hungria"]):
        return "Guerra Rússia-Ucrânia e Energia"

    if any(p in palavras for p in ["trump", "presidente", "governo", "senado", "campanha", "eleição", "eleicoes"]):
        return "Política, Governo e Eleições"

    if any(p in palavras for p in ["irã", "ira", "militar", "defesa", "aviador", "resgate", "pentágono", "pentagono"]):
        return "Conflitos, Defesa e Irã"

    if any(p in palavras for p in ["tribunal", "sentença", "autoridade", "palestina", "israel"]):
        return "Justiça, Tribunal e Relações Internacionais"

    return "Tema Geral"


def executar_clustering(caminho_corpus="corpus_final_filtrado.txt", n_clusters=4):
    documentos = carregar_corpus(caminho_corpus)

    if len(documentos) < n_clusters:
        raise ValueError("Quantidade de documentos menor que o número de clusters.")

    vectorizer = TfidfVectorizer(max_features=1000)
    X = vectorizer.fit_transform(documentos)

    modelo = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    clusters = modelo.fit_predict(X)

    df = pd.DataFrame({
        "texto": documentos,
        "cluster": clusters
    })

    palavras_cluster = palavras_mais_importantes_por_cluster(df, n=10)

    nomes_clusters = {}
    for cluster, palavras in palavras_cluster.items():
        nomes_clusters[cluster] = sugerir_nome_cluster(palavras)

    df["nome_cluster"] = df["cluster"].map(nomes_clusters)

    df.to_csv("resultados_clusters.csv", index=False, encoding="utf-8")

    with open("resultados_clusters.txt", "w", encoding="utf-8") as f:
        f.write("RESULTADOS DO CLUSTERING DE NOTÍCIAS\n")
        f.write("=" * 70 + "\n\n")

        for cluster in sorted(palavras_cluster.keys()):
            f.write(f"CLUSTER {cluster}\n")
            f.write(f"Nome sugerido: {nomes_clusters[cluster]}\n")
            f.write("-" * 50 + "\n")
            f.write("Palavras mais frequentes:\n")
            f.write(", ".join([f"{palavra} ({qtd})" for palavra, qtd in palavras_cluster[cluster]]))
            f.write("\n\n")

            exemplos = df[df["cluster"] == cluster]["texto"].head(3).tolist()
            f.write("Exemplos de textos:\n")
            for i, exemplo in enumerate(exemplos, start=1):
                f.write(f"{i}. {exemplo[:500]}...\n\n")

            f.write("=" * 70 + "\n\n")

    print("Clustering concluído com sucesso.")
    print("Arquivos gerados:")
    print("- resultados_clusters.csv")
    print("- resultados_clusters.txt")


if __name__ == "__main__":
    executar_clustering("corpus_final_filtrado.txt", n_clusters=4)