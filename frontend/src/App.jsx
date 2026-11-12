import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

async function api(path, options) {
  const response = await fetch(`${API}${path}`, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Não foi possível concluir a ação.");
  }

  return data;
}

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [category, setCategory] = useState("Geral");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function loadDocuments() {
    try {
      const result = await api("/api/documents");
      setDocuments(result);
    } catch {
      setMessage("Não consegui carregar os documentos. Confira se o backend está rodando.");
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function upload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setBusy(true);
    setMessage("");

    const form = new FormData();
    form.append("file", file);
    form.append("category", category);

    try {
      const result = await api("/api/documents", {
        method: "POST",
        body: form,
      });
      setMessage(`Documento indexado: ${result.title}`);
      await loadDocuments();
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
      event.target.value = "";
    }
  }

  async function ask(event) {
    event.preventDefault();
    if (!question.trim()) return;

    setBusy(true);
    setAnswer(null);
    setMessage("");

    try {
      setAnswer(
        await api("/api/ask", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ question }),
        })
      );
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app">
      <header className="topbar">
        <div className="brand"><span>DV</span><div>DataVision<small>BBTS · INTELIGÊNCIA EMPRESARIAL</small></div></div>
        <span className="connection">● PostgreSQL conectado</span>
      </header>

      <section className="intro">
        <p className="eyebrow">SEU ACERVO, MAIS INTELIGENTE</p>
        <h1>Decisões claras começam com <em>boas evidências.</em></h1>
        <p>Envie documentos e pergunte sobre prazos, obrigações, riscos e informações importantes.</p>
      </section>

      {message && <div className="message">{message}</div>}

      <section className="summary">
        <div><strong>{documents.length}</strong><span>documentos indexados</span></div>
        <div><strong>PDF</strong><span>formato aceito nesta versão</span></div>
        <div><strong>Fonte</strong><span>respostas com trechos e páginas</span></div>
      </section>

      <section className="columns">
        <div className="panel">
          <p className="eyebrow">01 · BASE DE CONHECIMENTO</p>
          <h2>Adicionar documento</h2>
          <p className="help">Envie um PDF para indexar o texto e torná-lo pesquisável.</p>

          <label className="field-label" htmlFor="category">Área</label>
          <select id="category" value={category} onChange={(e) => setCategory(e.target.value)}>
            <option>Geral</option>
            <option>Férias</option>
            <option>Inovação</option>
            <option>Locação</option>
          </select>

          <label className="upload">
            <span className="upload-icon">↑</span>
            <b>{busy ? "Processando..." : "Escolher arquivo PDF"}</b>
            <small>Clique para selecionar um documento</small>
            <input type="file" accept=".pdf,application/pdf" onChange={upload} disabled={busy} />
          </label>

          <div className="doc-heading"><h3>Documentos</h3><span>{documents.length}</span></div>
          {documents.length === 0 ? (
            <p className="empty">Seu acervo ainda está vazio.</p>
          ) : (
            <ul className="document-list">
              {documents.map((doc) => (
                <li key={doc.id}>
                  <span className="pdf">PDF</span>
                  <div><b>{doc.title}</b><small>{doc.category} · {doc.pages} páginas · v{doc.version}</small></div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel">
          <p className="eyebrow">02 · CONSULTA COM EVIDÊNCIAS</p>
          <h2>O que você quer descobrir?</h2>
          <p className="help">A resposta procura correspondências nos trechos indexados e mostra de onde vieram.</p>

          <form onSubmit={ask}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ex.: Quais documentos mencionam prazo para solicitar férias?"
              rows="4"
            />
            <button className="ask-button" disabled={busy || !question.trim()}>
              {busy ? "Buscando..." : "Buscar evidências →"}
            </button>
          </form>

          {answer && (
            <div className="answer">
              <h3>Resultado da consulta</h3>
              <p>{answer.answer}</p>
              {answer.needs_review && <div className="review">Confira as fontes antes de tomar uma decisão.</div>}
              {answer.citations.map((source, index) => (
                <article className="citation" key={`${source.document}-${index}`}>
                  <b>[{index + 1}] {source.document}</b>
                  <small>{source.category} · página {source.page} · versão {source.version}</small>
                  <blockquote>{source.excerpt}</blockquote>
                </article>
              ))}
            </div>
          )}
        </div>
      </section>
      <footer>DataVision BBTS <span>Protótipo em desenvolvimento</span></footer>
    </main>
  );
}