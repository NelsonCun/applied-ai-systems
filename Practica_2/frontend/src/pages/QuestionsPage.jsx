import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import Modal from "../components/Modal";
import {
  AnswerBadge,
  EmptyState,
  ErrorBox,
  LoadingState,
  StatusBadge,
} from "../components/Ui";


const EMPTY_QUESTION = {
  category_id: "",
  question_text: "",
  is_active: true,
};

const EMPTY_ANSWER = {
  answer_text: "",
  is_active: true,
};


function QuestionsPage({
  token,
  notify,
}) {
  const [questions, setQuestions] =
    useState([]);

  const [categories, setCategories] =
    useState([]);

  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] =
    useState("");

  const [activeFilter, setActiveFilter] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] = useState("");
  const [saving, setSaving] =
    useState(false);

  const [questionModalOpen, setQuestionModalOpen] =
    useState(false);

  const [answerModalOpen, setAnswerModalOpen] =
    useState(false);

  const [editingQuestion, setEditingQuestion] =
    useState(null);

  const [selectedQuestion, setSelectedQuestion] =
    useState(null);

  const [questionForm, setQuestionForm] =
    useState(EMPTY_QUESTION);

  const [answerForm, setAnswerForm] =
    useState(EMPTY_ANSWER);

  const loadData = async () => {
    setLoading(true);
    setError("");

    const params = new URLSearchParams();

    if (search.trim()) {
      params.set("search", search.trim());
    }

    if (categoryFilter) {
      params.set(
        "category_id",
        categoryFilter
      );
    }

    if (activeFilter !== "") {
      params.set("is_active", activeFilter);
    }

    const suffix = params.toString()
      ? `?${params.toString()}`
      : "";

    try {
      const [
        categoriesData,
        questionsData,
      ] = await Promise.all([
        apiRequest(
          "/categories?is_active=true",
          { token }
        ),
        apiRequest(
          `/questions${suffix}`,
          { token }
        ),
      ]);

      setCategories(categoriesData);
      setQuestions(questionsData);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [token]);

  const openCreateQuestion = () => {
    if (categories.length === 0) {
      setError(
        "Debe crear al menos una categoría activa antes de registrar preguntas."
      );

      return;
    }

    setEditingQuestion(null);

    setQuestionForm({
      ...EMPTY_QUESTION,
      category_id: String(
        categories[0].id
      ),
    });

    setQuestionModalOpen(true);
  };

  const openEditQuestion = (question) => {
    setEditingQuestion(question);

    setQuestionForm({
      category_id: String(
        question.category_id
      ),
      question_text:
        question.question_text,
      is_active: question.is_active,
    });

    setQuestionModalOpen(true);
  };

  const saveQuestion = async (event) => {
    event.preventDefault();

    setSaving(true);
    setError("");

    const payload = {
      category_id: Number(
        questionForm.category_id
      ),
      question_text:
        questionForm.question_text,
      is_active: questionForm.is_active,
    };

    try {
      if (editingQuestion) {
        await apiRequest(
          `/questions/${editingQuestion.id}`,
          {
            method: "PUT",
            token,
            body: payload,
          }
        );

        notify(
          "Pregunta actualizada correctamente."
        );
      } else {
        await apiRequest(
          "/questions",
          {
            method: "POST",
            token,
            body: payload,
          }
        );

        notify(
          "Pregunta creada correctamente."
        );
      }

      setQuestionModalOpen(false);
      await loadData();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const deleteQuestion = async (question) => {
    const confirmed = window.confirm(
      "¿Desea eliminar esta pregunta y su respuesta asociada?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/questions/${question.id}`,
        {
          method: "DELETE",
          token,
        }
      );

      notify(
        "Pregunta eliminada correctamente."
      );

      await loadData();
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  const openAnswer = (question) => {
    setSelectedQuestion(question);

    setAnswerForm({
      answer_text:
        question.answer?.answer_text ?? "",
      is_active:
        question.answer?.is_active ?? true,
    });

    setAnswerModalOpen(true);
  };

  const saveAnswer = async (event) => {
    event.preventDefault();

    if (!selectedQuestion) {
      return;
    }

    setSaving(true);
    setError("");

    const payload = {
      answer_text: answerForm.answer_text,
      is_active: answerForm.is_active,
    };

    try {
      if (selectedQuestion.answer) {
        await apiRequest(
          `/answers/${selectedQuestion.answer.id}`,
          {
            method: "PUT",
            token,
            body: payload,
          }
        );

        notify(
          "Respuesta actualizada correctamente."
        );
      } else {
        await apiRequest(
          "/answers",
          {
            method: "POST",
            token,
            body: {
              question_id:
                selectedQuestion.id,
              ...payload,
            },
          }
        );

        notify(
          "Respuesta creada correctamente."
        );
      }

      setAnswerModalOpen(false);
      await loadData();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const deleteAnswer = async () => {
    if (!selectedQuestion?.answer) {
      return;
    }

    const confirmed = window.confirm(
      "¿Desea eliminar la respuesta asociada?"
    );

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/answers/${selectedQuestion.answer.id}`,
        {
          method: "DELETE",
          token,
        }
      );

      notify(
        "Respuesta eliminada correctamente."
      );

      setAnswerModalOpen(false);
      await loadData();
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <h2>Preguntas y respuestas</h2>

          <p>
            Administre el conocimiento utilizado
            por el bot para atender consultas.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={openCreateQuestion}
        >
          Nueva pregunta
        </button>
      </section>

      <ErrorBox message={error} />

      <section className="panel">
        <form
          className="toolbar"
          onSubmit={(event) => {
            event.preventDefault();
            loadData();
          }}
        >
          <label className="field field-grow">
            <span>Buscar</span>

            <input
              type="search"
              value={search}
              placeholder="Texto de la pregunta"
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />
          </label>

          <label className="field">
            <span>Categoría</span>

            <select
              value={categoryFilter}
              onChange={(event) =>
                setCategoryFilter(
                  event.target.value
                )
              }
            >
              <option value="">
                Todas
              </option>

              {categories.map(
                (category) => (
                  <option
                    key={category.id}
                    value={category.id}
                  >
                    {category.name}
                  </option>
                )
              )}
            </select>
          </label>

          <label className="field">
            <span>Estado</span>

            <select
              value={activeFilter}
              onChange={(event) =>
                setActiveFilter(
                  event.target.value
                )
              }
            >
              <option value="">
                Todos
              </option>
              <option value="true">
                Activas
              </option>
              <option value="false">
                Inactivas
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
        ) : questions.length === 0 ? (
          <EmptyState
            title="No hay preguntas registradas"
            description="Cree preguntas y asócieles respuestas para que el bot pueda utilizarlas."
            action={
              <button
                type="button"
                className="btn btn-primary"
                onClick={openCreateQuestion}
              >
                Crear pregunta
              </button>
            }
          />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Pregunta</th>
                  <th>Categoría</th>
                  <th>Respuesta</th>
                  <th>Estado</th>
                  <th className="actions-column">
                    Acciones
                  </th>
                </tr>
              </thead>

              <tbody>
                {questions.map((question) => (
                  <tr key={question.id}>
                    <td className="question-cell">
                      <strong>
                        {question.question_text}
                      </strong>

                      <span>
                        Coincidencia:{" "}
                        {question.normalized_text}
                      </span>
                    </td>

                    <td>
                      {question.category.name}
                    </td>

                    <td>
                      <div className="answer-cell">
                        <AnswerBadge
                          answered={
                            Boolean(
                              question.answer
                            )
                          }
                        />

                        {question.answer && (
                          <span>
                            {
                              question.answer
                                .answer_text
                            }
                          </span>
                        )}
                      </div>
                    </td>

                    <td>
                      <StatusBadge
                        active={
                          question.is_active
                        }
                      />
                    </td>

                    <td>
                      <div className="row-actions row-actions-wrap">
                        <button
                          type="button"
                          className="btn btn-small btn-primary-soft"
                          onClick={() =>
                            openAnswer(question)
                          }
                        >
                          {question.answer
                            ? "Editar respuesta"
                            : "Agregar respuesta"}
                        </button>

                        <button
                          type="button"
                          className="btn btn-small btn-secondary"
                          onClick={() =>
                            openEditQuestion(
                              question
                            )
                          }
                        >
                          Editar
                        </button>

                        <button
                          type="button"
                          className="btn btn-small btn-danger"
                          onClick={() =>
                            deleteQuestion(
                              question
                            )
                          }
                        >
                          Eliminar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <Modal
        open={questionModalOpen}
        title={
          editingQuestion
            ? "Editar pregunta"
            : "Nueva pregunta"
        }
        onClose={() =>
          !saving &&
          setQuestionModalOpen(false)
        }
        footer={
          <>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() =>
                setQuestionModalOpen(false)
              }
              disabled={saving}
            >
              Cancelar
            </button>

            <button
              type="submit"
              form="question-form"
              className="btn btn-primary"
              disabled={saving}
            >
              {saving
                ? "Guardando..."
                : "Guardar pregunta"}
            </button>
          </>
        }
      >
        <form
          id="question-form"
          className="form-grid"
          onSubmit={saveQuestion}
        >
          <label className="field">
            <span>Categoría</span>

            <select
              value={
                questionForm.category_id
              }
              onChange={(event) =>
                setQuestionForm({
                  ...questionForm,
                  category_id:
                    event.target.value,
                })
              }
              required
            >
              {categories.map(
                (category) => (
                  <option
                    key={category.id}
                    value={category.id}
                  >
                    {category.name}
                  </option>
                )
              )}
            </select>
          </label>

          <label className="field">
            <span>Pregunta</span>

            <textarea
              value={
                questionForm.question_text
              }
              onChange={(event) =>
                setQuestionForm({
                  ...questionForm,
                  question_text:
                    event.target.value,
                })
              }
              rows={5}
              minLength={2}
              maxLength={500}
              required
              autoFocus
            />
          </label>

          <label className="switch-field">
            <input
              type="checkbox"
              checked={
                questionForm.is_active
              }
              onChange={(event) =>
                setQuestionForm({
                  ...questionForm,
                  is_active:
                    event.target.checked,
                })
              }
            />

            <span>Pregunta activa</span>
          </label>
        </form>
      </Modal>

      <Modal
        open={answerModalOpen}
        title={
          selectedQuestion?.answer
            ? "Editar respuesta"
            : "Agregar respuesta"
        }
        size="large"
        onClose={() =>
          !saving &&
          setAnswerModalOpen(false)
        }
        footer={
          <>
            {selectedQuestion?.answer && (
              <button
                type="button"
                className="btn btn-danger btn-left"
                onClick={deleteAnswer}
                disabled={saving}
              >
                Eliminar respuesta
              </button>
            )}

            <button
              type="button"
              className="btn btn-secondary"
              onClick={() =>
                setAnswerModalOpen(false)
              }
              disabled={saving}
            >
              Cancelar
            </button>

            <button
              type="submit"
              form="answer-form"
              className="btn btn-primary"
              disabled={saving}
            >
              {saving
                ? "Guardando..."
                : "Guardar respuesta"}
            </button>
          </>
        }
      >
        <div className="question-reference">
          <span>Pregunta asociada</span>
          <strong>
            {selectedQuestion?.question_text}
          </strong>
        </div>

        <form
          id="answer-form"
          className="form-grid"
          onSubmit={saveAnswer}
        >
          <label className="field">
            <span>Respuesta</span>

            <textarea
              value={answerForm.answer_text}
              onChange={(event) =>
                setAnswerForm({
                  ...answerForm,
                  answer_text:
                    event.target.value,
                })
              }
              rows={8}
              minLength={2}
              maxLength={4000}
              required
              autoFocus
            />
          </label>

          <label className="switch-field">
            <input
              type="checkbox"
              checked={answerForm.is_active}
              onChange={(event) =>
                setAnswerForm({
                  ...answerForm,
                  is_active:
                    event.target.checked,
                })
              }
            />

            <span>Respuesta activa</span>
          </label>
        </form>
      </Modal>
    </div>
  );
}


export default QuestionsPage;
