import { useEffect, useState } from "react";

import { apiRequest } from "../api/client";
import Modal from "../components/Modal";
import {
  EmptyState,
  ErrorBox,
  LoadingState,
  StatusBadge,
} from "../components/Ui";


const EMPTY_FORM = {
  name: "",
  description: "",
  is_active: true,
};


function CategoriesPage({
  token,
  notify,
}) {
  const [categories, setCategories] =
    useState([]);

  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] = useState("");
  const [saving, setSaving] =
    useState(false);

  const [modalOpen, setModalOpen] =
    useState(false);

  const [editingCategory, setEditingCategory] =
    useState(null);

  const [form, setForm] =
    useState(EMPTY_FORM);

  const loadCategories = async () => {
    setLoading(true);
    setError("");

    const params = new URLSearchParams();

    if (search.trim()) {
      params.set("search", search.trim());
    }

    if (activeFilter !== "") {
      params.set("is_active", activeFilter);
    }

    const suffix = params.toString()
      ? `?${params.toString()}`
      : "";

    try {
      const data = await apiRequest(
        `/categories${suffix}`,
        { token }
      );

      setCategories(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCategories();
  }, [token]);

  const openCreate = () => {
    setEditingCategory(null);
    setForm(EMPTY_FORM);
    setModalOpen(true);
  };

  const openEdit = (category) => {
    setEditingCategory(category);

    setForm({
      name: category.name,
      description: category.description ?? "",
      is_active: category.is_active,
    });

    setModalOpen(true);
  };

  const saveCategory = async (event) => {
    event.preventDefault();

    setSaving(true);
    setError("");

    try {
      const payload = {
        name: form.name,
        description:
          form.description.trim() || null,
        is_active: form.is_active,
      };

      if (editingCategory) {
        await apiRequest(
          `/categories/${editingCategory.id}`,
          {
            method: "PUT",
            token,
            body: payload,
          }
        );

        notify(
          "Categoría actualizada correctamente."
        );
      } else {
        await apiRequest(
          "/categories",
          {
            method: "POST",
            token,
            body: payload,
          }
        );

        notify(
          "Categoría creada correctamente."
        );
      }

      setModalOpen(false);
      await loadCategories();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setSaving(false);
    }
  };

  const deleteCategory = async (category) => {
    const confirmed = window.confirm(
      `¿Desea eliminar la categoría "${category.name}"?`
    );

    if (!confirmed) {
      return;
    }

    try {
      await apiRequest(
        `/categories/${category.id}`,
        {
          method: "DELETE",
          token,
        }
      );

      notify(
        "Categoría eliminada correctamente."
      );

      await loadCategories();
    } catch (requestError) {
      setError(requestError.message);
    }
  };

  return (
    <div className="page-stack">
      <section className="page-header">
        <div>
          <h2>Categorías</h2>
          <p>
            Organice las preguntas frecuentes
            por temas administrativos.
          </p>
        </div>

        <button
          type="button"
          className="btn btn-primary"
          onClick={openCreate}
        >
          Nueva categoría
        </button>
      </section>

      <ErrorBox message={error} />

      <section className="panel">
        <form
          className="toolbar"
          onSubmit={(event) => {
            event.preventDefault();
            loadCategories();
          }}
        >
          <label className="field field-grow">
            <span>Buscar</span>

            <input
              type="search"
              value={search}
              placeholder="Nombre de la categoría"
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />
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
        ) : categories.length === 0 ? (
          <EmptyState
            title="No hay categorías"
            description="Cree la primera categoría para comenzar a registrar preguntas."
            action={
              <button
                type="button"
                className="btn btn-primary"
                onClick={openCreate}
              >
                Crear categoría
              </button>
            }
          />
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Estado</th>
                  <th className="actions-column">
                    Acciones
                  </th>
                </tr>
              </thead>

              <tbody>
                {categories.map((category) => (
                  <tr key={category.id}>
                    <td>
                      <strong>
                        {category.name}
                      </strong>
                    </td>

                    <td>
                      {category.description ||
                        "Sin descripción"}
                    </td>

                    <td>
                      <StatusBadge
                        active={
                          category.is_active
                        }
                      />
                    </td>

                    <td>
                      <div className="row-actions">
                        <button
                          type="button"
                          className="btn btn-small btn-secondary"
                          onClick={() =>
                            openEdit(category)
                          }
                        >
                          Editar
                        </button>

                        <button
                          type="button"
                          className="btn btn-small btn-danger"
                          onClick={() =>
                            deleteCategory(
                              category
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
        open={modalOpen}
        title={
          editingCategory
            ? "Editar categoría"
            : "Nueva categoría"
        }
        onClose={() =>
          !saving && setModalOpen(false)
        }
        footer={
          <>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() =>
                setModalOpen(false)
              }
              disabled={saving}
            >
              Cancelar
            </button>

            <button
              type="submit"
              form="category-form"
              className="btn btn-primary"
              disabled={saving}
            >
              {saving
                ? "Guardando..."
                : "Guardar categoría"}
            </button>
          </>
        }
      >
        <form
          id="category-form"
          className="form-grid"
          onSubmit={saveCategory}
        >
          <label className="field">
            <span>Nombre</span>

            <input
              type="text"
              value={form.name}
              onChange={(event) =>
                setForm({
                  ...form,
                  name: event.target.value,
                })
              }
              minLength={2}
              maxLength={100}
              required
              autoFocus
            />
          </label>

          <label className="field">
            <span>Descripción</span>

            <textarea
              value={form.description}
              onChange={(event) =>
                setForm({
                  ...form,
                  description:
                    event.target.value,
                })
              }
              rows={4}
              maxLength={1000}
            />
          </label>

          <label className="switch-field">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(event) =>
                setForm({
                  ...form,
                  is_active:
                    event.target.checked,
                })
              }
            />

            <span>
              Categoría activa
            </span>
          </label>
        </form>
      </Modal>
    </div>
  );
}


export default CategoriesPage;
