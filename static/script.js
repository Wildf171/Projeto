const linhasOriginais = Array.from(document.querySelectorAll("#corpoTabela tr"));
const buscaInput = document.getElementById("buscaComentario");
const filtroSentimento = document.getElementById("filtroSentimento");
const contadorComentarios = document.getElementById("contadorComentarios");

const btnAnterior = document.getElementById("btnAnterior");
const btnProxima = document.getElementById("btnProxima");
const infoPagina = document.getElementById("infoPagina");

let paginaAtual = 1;
const itensPorPagina = 10;
let linhasFiltradas = [...linhasOriginais];

function aplicarFiltros() {
    const textoBusca = buscaInput.value.toLowerCase().trim();
    const sentimentoSelecionado = filtroSentimento.value;

    linhasFiltradas = linhasOriginais.filter((linha) => {
        const comentario = linha.getAttribute("data-comentario");
        const sentimento = linha.getAttribute("data-sentimento");

        const correspondeTexto = comentario.includes(textoBusca);
        const correspondeSentimento =
            sentimentoSelecionado === "todos" || sentimento === sentimentoSelecionado;

        return correspondeTexto && correspondeSentimento;
    });

    paginaAtual = 1;
    renderizarTabela();
}

function renderizarTabela() {
    linhasOriginais.forEach(linha => linha.style.display = "none");

    const totalPaginas = Math.max(1, Math.ceil(linhasFiltradas.length / itensPorPagina));
    if (paginaAtual > totalPaginas) paginaAtual = totalPaginas;

    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;

    const linhasPagina = linhasFiltradas.slice(inicio, fim);

    linhasPagina.forEach(linha => {
        linha.style.display = "";
    });

    contadorComentarios.textContent = `Mostrando ${linhasPagina.length} de ${linhasFiltradas.length} comentários filtrados`;
    infoPagina.textContent = `Página ${paginaAtual} de ${totalPaginas}`;

    btnAnterior.disabled = paginaAtual === 1;
    btnProxima.disabled = paginaAtual === totalPaginas;
}

buscaInput.addEventListener("input", aplicarFiltros);
filtroSentimento.addEventListener("change", aplicarFiltros);

btnAnterior.addEventListener("click", () => {
    if (paginaAtual > 1) {
        paginaAtual--;
        renderizarTabela();
    }
});

btnProxima.addEventListener("click", () => {
    const totalPaginas = Math.ceil(linhasFiltradas.length / itensPorPagina);
    if (paginaAtual < totalPaginas) {
        paginaAtual++;
        renderizarTabela();
    }
});

renderizarTabela();