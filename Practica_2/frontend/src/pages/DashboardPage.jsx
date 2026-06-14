import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import {
  AnswerBadge,
  EmptyState,
  ErrorBox,
  LoadingState,
} from "../components/Ui";


const INITIAL_SUMMARY = {
  total_queries: 0,
  answered_queries: 0,
  unanswered_queries: 0,
  unique_users: 0,
  unique_chats: 0,
  total_categories: 0,
  total_questions: 0,
  total_answers: 0,
  answer_rate: 0,
};


function formatDate(value) {
  if (!value) {
    return "—";
  }

  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  ).format(new Date(value));
}


function DashboardPage({ token }) {
  const [summary, setSummary] =
    useState(INITIAL_SUMMARY);

  const [topQuestions, setTopQuestions] =
    useState([]);

  const [topQueries, setTopQueries] =
    useState([]);

  const [recentLogs, setRecentLogs] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] = useState("");

  const loadDashboard = async () => {
    setLoading(true);
    setError("");

    try {
      const [
        summaryData,
        questionsData,
        queriesData,
        logsData,
      ] = await Promise.all([
        apiRequest(
          "/statistics/summary",
          { token }
        ),
        apiRequest(
          "/statistics/top-questions?limit=5",
          { token }
        ),
        apiRequest(
          "/statistics/top-queries?limit=5",
          { token }
        ),
        apiRequest(
          "/query-logs?page=1&page_size=5",
          { token }
        ),
      ]);

      setSummary(summaryData);
      setTopQuestions(questionsData);
      setTopQueries(queriesData);
      setRecentLogs(logsData.items);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, [token]);

  if (loading) {
    return (
      <LoadingState message="Preparando el resumen del sistema..." />
    );
  }

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <h2>Estado general</h2>
          <p>
            Indicadores de contenido,
            interacciones y rendimiento del bot.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={loadDashboard}
        >
          Actualizar
        </button>
      </section>

      <ErrorBox message={error} />

      <section className="metric-grid">
        <article className="metric-card">
          <span className="metric-label">
            Consultas totales
          </span>

          <strong className="metric-value">
            {summary.total_queries}
          </strong>

          <span className="metric-helper">
            Interacciones registradas
          </span>
        </article>

        <article className="metric-card">
          <span className="metric-label">
            Tasa de respuesta
          </span>

          <strong className="metric-value">
            {summary.answer_rate}%
          </strong>

          <span className="metric-helper">
            {summary.answered_queries} respondidas
          </span>
        </article>

        <article className="metric-card">
          <span className="metric-label">
            Preguntas
          </span>

          <strong className="metric-value">
            {summary.total_questions}
          </strong>

          <span className="metric-helper">
            {summary.total_answers} respuestas
          </span>
        </article>

        <article className="metric-card">
          <span className="metric-label">
            Usuarios únicos
          </span>

          <strong className="metric-value">
            {summary.unique_users}
          </strong>

          <span className="metric-helper">
            {summary.unique_chats} chats
          </span>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <header className="panel-header">
            <div>
              <h3>Consultas recientes</h3>
              <p>
                Últimos mensajes procesados.
              </p>
            </div>
          </header>

          {recentLogs.length === 0 ? (
            <EmptyState
              title="Aún no hay consultas"
              description="Las interacciones de Telegram aparecerán en esta sección."
            />
          ) : (
            <div className="activity-list">
              {recentLogs.map((item) => (
                <article
                  className="activity-item"
                  key={item.id}
                >
                  <div>
                    <strong>
                      {item.original_query}
                    </strong>

                    <span>
                      {item.telegram_first_name ||
                        item.telegram_username ||
                        "Usuario de Telegram"}
                      {" · "}
                      {formatDate(item.created_at)}
                    </span>
                  </div>

                  <AnswerBadge
                    answered={item.was_answered}
                  />
                </article>
              ))}
            </div>
          )}
        </article>

        <article className="panel">
          <header className="panel-header">
            <div>
              <h3>Contenido registrado</h3>
              <p>
                Distribución del conocimiento.
              </p>
            </div>
          </header>

          <div className="content-summary">
            <div>
              <span>Categorías</span>
              <strong>
                {summary.total_categories}
              </strong>
            </div>

            <div>
              <span>Preguntas</span>
              <strong>
                {summary.total_questions}
              </strong>
            </div>

            <div>
              <span>Respuestas</span>
              <strong>
                {summary.total_answers}
              </strong>
            </div>

            <div>
              <span>No respondidas</span>
              <strong>
                {summary.unanswered_queries}
              </strong>
            </div>
          </div>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <header className="panel-header">
            <div>
              <h3>Preguntas más utilizadas</h3>
              <p>
                Respuestas encontradas con mayor frecuencia.
              </p>
            </div>
          </header>

          {topQuestions.length === 0 ? (
            <p className="muted-text">
              Todavía no existen preguntas con
              consultas asociadas.
            </p>
          ) : (
            <div className="ranking-list">
              {topQuestions.map(
                (item, index) => (
                  <div
                    className="ranking-item"
                    key={item.question_id}
                  >
                    <span className="ranking-number">
                      {index + 1}
                    </span>

                    <div>
                      <strong>
                        {item.question_text}
                      </strong>

                      <span>
                        {item.category_name}
                      </span>
                    </div>

                    <b>{item.query_count}</b>
                  </div>
                )
              )}
            </div>
          )}
        </article>

        <article className="panel">
          <header className="panel-header">
            <div>
              <h3>Consultas frecuentes</h3>
              <p>
                Textos recibidos con mayor frecuencia.
              </p>
            </div>
          </header>

          {topQueries.length === 0 ? (
            <p className="muted-text">
              No existen consultas registradas.
            </p>
          ) : (
            <div className="ranking-list">
              {topQueries.map(
                (item, index) => (
                  <div
                    className="ranking-item"
                    key={item.normalized_query}
                  >
                    <span className="ranking-number">
                      {index + 1}
                    </span>

                    <div>
                      <strong>
                        {item.sample_query}
                      </strong>

                      <span>
                        {item.answered_count} respondidas ·{" "}
                        {item.unanswered_count} sin respuesta
                      </span>
                    </div>

                    <b>{item.query_count}</b>
                  </div>
                )
              )}
            </div>
          )}
        </article>
      </section>
    </div>
  );
}


export default DashboardPage;
