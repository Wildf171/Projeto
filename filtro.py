PALAVRAS_TEMA = {
    "política", "politica", "eleição", "eleicoes", "eleitoral", "votação", "votacao",
    "presidente", "governo", "senado", "congresso", "tribunal", "campanha",
    "trump", "orçamento", "orcamento", "defesa", "pentágono", "pentagono",
    "guerra", "conflito", "militar", "militares", "irã", "ira",
    "ucrânia", "ucrania", "rússia", "russia", "energia", "gás", "gas",
    "otan", "israel", "hamas", "diplomacia", "internacional"
}

with open("corpus_processado.txt", "r", encoding="utf-8") as f:
    linhas = [linha.strip() for linha in f if linha.strip()]

filtradas = []
for linha in linhas:
    if any(p in linha for p in PALAVRAS_TEMA):
        filtradas.append(linha)

with open("corpus_final_filtrado.txt", "w", encoding="utf-8") as f:
    for linha in filtradas:
        f.write(linha + "\n")

print("Corpus final filtrado gerado com sucesso.")
print("Total de documentos:", len(filtradas))