import { useEffect, useState } from "react";
import "./App.css";

const API = "http://127.0.0.1:8000";

async function api(path, options) {
  const response = await fetch(API + path, options);
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Não foi possível concluir a ação.");
  }

  return data;
}
export default function App() {
  const [documents, setDocuments] = useState([]);
  const [area, setArea] = useState("Geral");
  const [topic, setTopic] = useState("Geral");
  const [documentType, setDocumentType] = useState("Outro");
  const [documentDate, setDocumentDate] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState("Verificando conexão...");

  async function loadDocuments() {
    try {
      const result = await api("/api/documents");
      setDocuments(result);
      setConnectionStatus("PostgreSQL conectado");
    } catch {
      setConnectionStatus("Backend indisponível");
      setMessage("Não consegui carregar os documentos. Confira se o backend está rodando.");
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  async function upload(event) {
    const files = Array.from(event.target.files || []);
    if (!files.length) return;

    setBusy(true);
    setMessage("");
    const results = [];

    for (let index = 0; index < files.length; index += 1) {
      const file = files[index];
      setProgress({
        current: index + 1,
        total: files.length,
        filename: file.name,
        percent: Math.round((index / files.length) * 100),
      });

      const form = new FormData();
      form.append("file", file);
      form.append("area", area);
      form.append("topic", topic);
      form.append("document_type", documentType);
      if (documentDate) form.append("document_date", documentDate);

      try {
        const result = await api("/api/documents", {
          method: "POST",
          body: form,
        });
        if (result.duplicate) {
          results.push(file.name + ": duplicado; ignorado.");
        } else {
          results.push(file.name + ": processado.");
          if (result.warning) results.push(result.warning);
        }
      } catch (error) {
        results.push(file.name + ": " + error.message);
      }

      setProgress({
        current: index + 1,
        total: files.length,
        filename: file.name,
        percent: Math.round(((index + 1) / files.length) * 100),
      });
    }

    setMessage(results.join(" "));
    setProgress(null);
    await loadDocuments();
    setBusy(false);
    event.target.value = "";
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
        <span className="connection">● {connectionStatus}</span>
      </header>

      <section className="intro">
        <p className="eyebrow">SEU ACERVO, MAIS INTELIGENTE</p>
        <h1>Decisões claras começam com <em>boas evidências.</em></h1>
        <p>Envie documentos e pergunte sobre prazos, obrigações, riscos e informações importantes.</p>
      </section>

      {message && <div className="message">{message}</div>}

      <section className="summary">
        <div><strong>{documents.length}</strong><span>documentos indexados</span></div>
        <div><strong>PDF</strong><span>envio individual ou em lote</span></div>
        <div><strong>Fonte</strong><span>respostas com trechos e páginas</span></div>
      </section>

      <section className="columns">
        <div className="panel">
          <p className="eyebrow">01 · BASE DE CONHECIMENTO</p>
          <h2>Adicionar documentos</h2>
          <p className="help">Selecione um ou vários PDFs. O sistema identifica o nome, a versão e a data no arquivo quando disponíveis.</p>

          <label className="field-label" htmlFor="area">Área</label>
          <select id="area" value={area} onChange={(e) => setArea(e.target.value)}>
            <option>Geral</option>
            <option>RH</option>
            <option>Financeiro</option>
            <option>Jurídico</option>
            <option>Operações</option>
          </select>

          <label className="field-label" htmlFor="topic">Tema</label>
          <input id="topic" className="metadata-input" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Ex.: férias, locação, inovação" />

          <label className="field-label" htmlFor="documentType">Tipo de documento</label>
          <select id="documentType" value={documentType} onChange={(e) => setDocumentType(e.target.value)}>
            <option>Outro</option>
            <option>Norma</option>
            <option>Procedimento</option>
            <option>Contrato</option>
            <option>Formulário</option>
            <option>Relatório</option>
          </select>

          <label className="field-label" htmlFor="documentDate">Data do documento (opcional)</label>
          <input id="documentDate" className="metadata-input" type="date" value={documentDate} onChange={(e) => setDocumentDate(e.target.value)} />
          <small className="field-help">A data informada será aplicada a todos os PDFs selecionados. Deixe vazia para tentar identificá-la pelo nome do arquivo.</small>

          <label className="upload">
            <span className="upload-icon">↑</span>
            <b>{busy ? "Processando..." : "Escolher PDF(s)"}</b>
            <small>Clique e selecione um ou vários documentos</small>
            <input type="file" accept=".pdf,application/pdf" multiple onChange={upload} disabled={busy} />
          </label>

          {progress && (
            <div className="upload-progress">
              <div className="progress-label">
                <span>Processando {progress.current} de {progress.total}</span>
                <span>{progress.percent}%</span>
              </div>
              <div className="progress-track"><div style={{ width: progress.percent + "%" }} /></div>
              <small>{progress.filename}</small>
            </div>
          )}

          <div className="doc-heading"><h3>Documentos</h3><span>{documents.length}</span></div>
          {documents.length === 0 ? (
            <p className="empty">Seu acervo ainda está vazio.</p>
          ) : (
            <ul className="document-list">
              {documents.map((doc) => (
                <li key={doc.id}>
                  <span className="pdf">PDF</span>
                  <div>
                    <b>{doc.title}</b>
                    <small>{doc.area} · {doc.topic} · {doc.document_type} · {doc.pages} páginas · v{doc.version}</small>
                    <small>Arquivo: {doc.source_filename || doc.title} · Data: {doc.document_date || "não identificada"}</small>
                  </div>
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
                <article className="citation" key={source.document + "-" + index}>
                  <b>[{index + 1}] {source.document}</b>
                  <small>{source.source_filename || source.document} · {source.area} · {source.document_type} · página {source.page} · versão {source.version}</small>
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
