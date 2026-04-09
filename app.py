from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route("/")
def index():
    df = pd.read_csv("resultados_clusters.csv", encoding="utf-8")

    total_noticias = len(df)

    contagem_clusters = (
        df.groupby(["cluster", "nome_cluster"])
        .size()
        .reset_index(name="quantidade")
        .sort_values("cluster")
    )

    clusters = contagem_clusters.to_dict(orient="records")
    noticias = df.to_dict(orient="records")

    return render_template(
        "index.html",
        total_noticias=total_noticias,
        clusters=clusters,
        noticias=noticias
    )

if __name__ == "__main__":
    app.run(debug=True)