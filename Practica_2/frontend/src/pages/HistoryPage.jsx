import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import {
  AnswerBadge,
  EmptyState,
  ErrorBox,
  LoadingState,
} from "../components/Ui";


const PAGE_SIZE = 10;


function formatDate(value) {
  return new Intl.DateTimeFormat(
    "es-GT",
    {
      dateStyle: "medium",
      timeStyle: "medium",
    }
  ).format(new Date(value));
}


function HistoryPage({ token }) {
  const [data, setData] = useState({
    items: [],
    total: 0,
    page: 1,
    page_size: PAGE_SIZE,
  });

  const [page, setPage] = useState(1);
  const [search, setSearch] =
    useState("");

  const [answeredFilter, setAnsweredFilter] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] = useState("");

  const loadLogs = async (
    targetPage = page
  ) => {
    setLoading(true);
    setError("");

    const params = new URLSearchParams({
      page: String(targetPage),
      page_size: String(PAGE_SIZE),
    });

    if (search.trim()) {
      params.set("search", search.trim());
    }

    if (answeredFilter !== "") {
      params.set(
        "was_answered",
        answeredFilter
      );
    }

    try {
      const response = await apiRequest(
        `/query-logs?${params.toString()}`,
        { token }
      );

      setData(response);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLogs(page);
  }, [page, token]);

  const totalPages = Math.max(
    1,
    Math.ceil(data.total / PAGE_SIZE)
  );

  const applyFilters = (event) => {
    event.preventDefault();

    if (page === 1) {
      loadLogs(1);
    } else {
      setPage(1);
    }
  };

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <h2>Historial de consultas</h2>

          <p>
            Revise los mensajes recibidos,
            respuestas enviadas y consultas no
            reconocidas.
          </p>
        </div>

        <div className="header-counter">
          <strong>{data.total}</strong>
          <span>registros</span>
        </div>
      </section>

      <ErrorBox message={error} />

      <section className="panel">
        <form
          className="toolbar"
          onSubmit={applyFilters}
        >
          <label className="field field-grow">
            <span>Buscar</span>

            <input
              type="search"
              value={search}
              placeholder="Consulta, usuario o nombre"
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />
          </label>

          <label className="field">
            <span>Resultado</span>

            <select
              value={answeredFilter}
              onChange={(event) =>
                setAnsweredFilter(
                  event.target.value
                )
              }
            >
              <option value="">
                Todos
              </option>
              <option value="true">
                Respondidas
              </option>
              <option value="false">
                Sin respuesta
              </option>
            </select>
          </label>

          <button
            type="submit"
            className="btn btn-secondary toolbar-button"
          >
            Filtrar
          </button>
        </form>

        {loading ? (
          <LoadingState />
        ) : data.items.length === 0 ? (
          <EmptyState
            title="No hay consultas"
            description="Las interacciones realizadas desde Telegram aparecerán aquí."
          />
        ) : (
          <>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Usuario</th>
                    <th>Consulta</th>
                    <th>Respuesta</th>
                    <th>Resultado</th>
                  </tr>
                </thead>

                <tbody>
                  {data.items.map((item) => (
                    <tr key={item.id}>
                      <td className="date-cell">
                        {formatDate(
                          item.created_at
                        )}
                      </td>

                      <td>
                        <strong>
                          {item.telegram_first_name ||
                            "Sin nombre"}
                        </strong>

                        <span className="table-secondary">
                          {item.telegram_username
                            ? `@${item.telegram_username}`
                            : `ID ${item.telegram_user_id ?? "—"}`}
                        </span>
                      </td>

                      <td className="message-cell">
                        {item.original_query}
                      </td>

                      <td className="message-cell">
                        {item.response_text}
                      </td>

                      <td>
                        <AnswerBadge
                          answered={
                            item.was_answered
                          }
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <footer className="pagination">
              <span>
                Página {page} de {totalPages}
              </span>

              <div>
                <button
                  type="button"
                  className="btn btn-small btn-secondary"
                  disabled={page <= 1}
                  onClick={() =>
                    setPage((value) =>
                      Math.max(1, value - 1)
                    )
                  }
                >
                  Anterior
                </button>

                <button
                  type="button"
                  className="btn btn-small btn-secondary"
                  disabled={
                    page >= totalPages
                  }
                  onClick={() =>
                    setPage((value) =>
                      Math.min(
                        totalPages,
                        value + 1
                      )
                    )
                  }
                >
                  Siguiente
                </button>
              </div>
            </footer>
          </>
        )}
      </section>
    </div>
  );
}


export default HistoryPage;
