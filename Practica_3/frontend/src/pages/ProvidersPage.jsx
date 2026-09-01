import {
  Building2,
  LoaderCircle,
  Pencil,
  Plus,
  RefreshCw,
  Search,
  ToggleLeft,
  ToggleRight,
  UsersRound,
} from "lucide-react";

import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";

import apiClient, {
  getApiErrorMessage,
} from "../api/client";

import Modal from "../components/Modal";
import StatusBadge from "../components/StatusBadge";


const emptyForm = {
  name: "",
  nit: "",
  email: "",
  phone: "",
  address: "",
  category_id: "",
};


export default function ProvidersPage() {
  const [providers, setProviders] =
    useState([]);

  const [categories, setCategories] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [saving, setSaving] =
    useState(false);

  const [pageError, setPageError] =
    useState("");

  const [formError, setFormError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [search, setSearch] =
    useState("");

  const [statusFilter, setStatusFilter] =
    useState("ALL");

  const [modalOpen, setModalOpen] =
    useState(false);

  const [
    editingProvider,
    setEditingProvider,
  ] = useState(null);

  const [form, setForm] =
    useState(emptyForm);


  const loadData = useCallback(async () => {
    setLoading(true);
    setPageError("");

    try {
      const [
        providersResponse,
        categoriesResponse,
      ] = await Promise.all([
        apiClient.get("/providers", {
          params: {
            page: 1,
            page_size: 100,
          },
        }),
        apiClient.get("/categories"),
      ]);

      setProviders(
        providersResponse.data.items,
      );

      setCategories(
        categoriesResponse.data,
      );
    } catch (requestError) {
      setPageError(
        getApiErrorMessage(
          requestError,
          "No fue posible cargar los proveedores.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }, []);


  useEffect(() => {
    loadData();
  }, [loadData]);


  const filteredProviders = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return providers.filter((provider) => {
      const values = [
        provider.name,
        provider.nit,
        provider.email,
        provider.phone,
        provider.category_name,
      ]
        .filter(Boolean)
        .map((value) =>
          String(value).toLowerCase(),
        );

      const matchesSearch =
        !normalizedSearch ||
        values.some((value) =>
          value.includes(
            normalizedSearch,
          ),
        );

      const matchesStatus =
        statusFilter === "ALL" ||
        (
          statusFilter === "ACTIVE" &&
          provider.is_active
        ) ||
        (
          statusFilter === "INACTIVE" &&
          !provider.is_active
        );

      return (
        matchesSearch &&
        matchesStatus
      );
    });
  }, [
    providers,
    search,
    statusFilter,
  ]);


  const activeCount = useMemo(
    () =>
      providers.filter(
        (provider) =>
          provider.is_active,
      ).length,
    [providers],
  );


  const inactiveCount =
    providers.length - activeCount;


  function updateForm(field, value) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }


  function openCreateModal() {
    setEditingProvider(null);
    setForm(emptyForm);
    setFormError("");
    setModalOpen(true);
  }


  function openEditModal(provider) {
    setEditingProvider(provider);

    setForm({
      name: provider.name || "",
      nit: provider.nit || "",
      email: provider.email || "",
      phone: provider.phone || "",
      address: provider.address || "",
      category_id:
        provider.category_id?.toString() ||
        "",
    });

    setFormError("");
    setModalOpen(true);
  }


  function closeModal() {
    if (saving) {
      return;
    }

    setModalOpen(false);
    setFormError("");
  }


  async function saveProvider(event) {
    event.preventDefault();

    setSaving(true);
    setFormError("");
    setMessage("");

    const payload = {
      name: form.name.trim(),
      nit: form.nit.trim(),
      email:
        form.email.trim() || null,
      phone:
        form.phone.trim() || null,
      address:
        form.address.trim() || null,
      category_id:
        form.category_id
          ? Number(form.category_id)
          : null,
    };

    try {
      if (editingProvider) {
        await apiClient.put(
          `/providers/${editingProvider.id}`,
          payload,
        );

        setMessage(
          "Proveedor actualizado correctamente.",
        );
      } else {
        await apiClient.post(
          "/providers",
          payload,
        );

        setMessage(
          "Proveedor creado correctamente.",
        );
      }

      setModalOpen(false);
      setEditingProvider(null);
      setForm(emptyForm);

      await loadData();
    } catch (requestError) {
      setFormError(
        getApiErrorMessage(
          requestError,
          "No fue posible guardar el proveedor.",
        ),
      );
    } finally {
      setSaving(false);
    }
  }


  async function toggleProvider(provider) {
    const nextStatus =
      !provider.is_active;

    const confirmed = window.confirm(
      nextStatus
        ? `¿Desea reactivar a ${provider.name}?`
        : `¿Desea desactivar a ${provider.name}?`,
    );

    if (!confirmed) {
      return;
    }

    setPageError("");
    setMessage("");

    try {
      await apiClient.patch(
        `/providers/${provider.id}/status`,
        {
          is_active: nextStatus,
        },
      );

      setMessage(
        nextStatus
          ? "Proveedor reactivado correctamente."
          : "Proveedor desactivado correctamente.",
      );

      await loadData();
    } catch (requestError) {
      setPageError(
        getApiErrorMessage(
          requestError,
          "No fue posible cambiar el estado del proveedor.",
        ),
      );
    }
  }


  return (
    <div className="providers-page">
      <header className="page-header">
        <div>
          <span className="section-kicker">
            Catálogo administrativo
          </span>

          <h1>Proveedores</h1>

          <p>
            Administre las empresas asociadas
            al procesamiento y clasificación
            de facturas.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={openCreateModal}
        >
          <Plus size={18} />
          Nuevo proveedor
        </button>
      </header>

      <section className="compact-metric-grid">
        <article className="compact-metric compact-metric-yellow">
          <div>
            <span>Total registrado</span>
            <strong>
              {providers.length}
            </strong>
          </div>

          <UsersRound size={22} />
        </article>

        <article className="compact-metric compact-metric-green">
          <div>
            <span>Proveedores activos</span>
            <strong>{activeCount}</strong>
          </div>

          <ToggleRight size={23} />
        </article>

        <article className="compact-metric compact-metric-gray">
          <div>
            <span>Proveedores inactivos</span>
            <strong>{inactiveCount}</strong>
          </div>

          <ToggleLeft size={23} />
        </article>
      </section>

      {message && (
        <div className="form-alert form-alert-success">
          {message}
        </div>
      )}

      {pageError && (
        <div className="form-alert form-alert-error">
          {pageError}
        </div>
      )}

      <section className="content-card providers-table-card">
        <div className="table-toolbar">
          <div className="search-input">
            <Search size={18} />

            <input
              type="search"
              value={search}
              placeholder="Buscar por nombre, NIT, correo o categoría"
              onChange={(event) =>
                setSearch(
                  event.target.value,
                )
              }
            />
          </div>

          <div className="toolbar-actions">
            <select
              className="select-control toolbar-select"
              value={statusFilter}
              onChange={(event) =>
                setStatusFilter(
                  event.target.value,
                )
              }
            >
              <option value="ALL">
                Todos los estados
              </option>

              <option value="ACTIVE">
                Activos
              </option>

              <option value="INACTIVE">
                Inactivos
              </option>
            </select>

            <button
              className="secondary-button"
              type="button"
              onClick={loadData}
              disabled={loading}
            >
              <RefreshCw
                size={17}
                className={
                  loading
                    ? "spin"
                    : ""
                }
              />

              Actualizar
            </button>
          </div>
        </div>

        {loading ? (
          <div className="table-state">
            <LoaderCircle
              className="spin"
              size={30}
            />

            <p>
              Cargando proveedores...
            </p>
          </div>
        ) : (
          <>
            <div className="table-result-summary">
              <span>
                {filteredProviders.length}
                {" "}
                resultado
                {filteredProviders.length === 1
                  ? ""
                  : "s"}
              </span>
            </div>

            {filteredProviders.length === 0 ? (
              <div className="table-state">
                <Building2 size={36} />

                <h3>
                  No se encontraron proveedores
                </h3>

                <p>
                  Modifique los filtros o
                  registre un nuevo proveedor.
                </p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Proveedor</th>
                      <th>NIT</th>
                      <th>Categoría</th>
                      <th>Contacto</th>
                      <th>Estado</th>
                      <th className="table-actions-column">
                        Acciones
                      </th>
                    </tr>
                  </thead>

                  <tbody>
                    {filteredProviders.map(
                      (provider) => (
                        <tr key={provider.id}>
                          <td>
                            <div className="table-primary-cell">
                              <div className="table-avatar">
                                <Building2
                                  size={18}
                                />
                              </div>

                              <div>
                                <strong>
                                  {provider.name}
                                </strong>

                                <span>
                                  {provider.address ||
                                    "Sin dirección registrada"}
                                </span>
                              </div>
                            </div>
                          </td>

                          <td>
                            <span className="monospace">
                              {provider.nit}
                            </span>
                          </td>

                          <td>
                            <span className="category-chip">
                              {provider.category_name ||
                                "Sin categoría"}
                            </span>
                          </td>

                          <td>
                            <div className="stacked-value">
                              <span>
                                {provider.email ||
                                  "Sin correo"}
                              </span>

                              <small>
                                {provider.phone ||
                                  "Sin teléfono"}
                              </small>
                            </div>
                          </td>

                          <td>
                            <StatusBadge
                              status={
                                provider.is_active
                                  ? "ACTIVE"
                                  : "INACTIVE"
                              }
                            />
                          </td>

                          <td>
                            <div className="row-actions">
                              <button
                                className="table-icon-button"
                                type="button"
                                title="Editar proveedor"
                                onClick={() =>
                                  openEditModal(
                                    provider,
                                  )
                                }
                              >
                                <Pencil size={17} />
                              </button>

                              <button
                                className={[
                                  "table-icon-button",
                                  provider.is_active
                                    ? "table-icon-button-danger"
                                    : "table-icon-button-success",
                                ].join(" ")}
                                type="button"
                                title={
                                  provider.is_active
                                    ? "Desactivar proveedor"
                                    : "Reactivar proveedor"
                                }
                                onClick={() =>
                                  toggleProvider(
                                    provider,
                                  )
                                }
                              >
                                {provider.is_active ? (
                                  <ToggleRight
                                    size={20}
                                  />
                                ) : (
                                  <ToggleLeft
                                    size={20}
                                  />
                                )}
                              </button>
                            </div>
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}
      </section>

      <Modal
        open={modalOpen}
        title={
          editingProvider
            ? "Editar proveedor"
            : "Nuevo proveedor"
        }
        subtitle={
          editingProvider
            ? "Actualice la información administrativa y de contacto."
            : "Registre una empresa para asociarla a las facturas."
        }
        onClose={closeModal}
      >
        <form
          className="modal-form"
          onSubmit={saveProvider}
        >
          <div className="form-grid">
            <label className="form-field form-field-wide">
              <span>
                Nombre o razón social
              </span>

              <input
                className="text-control"
                required
                minLength={2}
                maxLength={180}
                value={form.name}
                placeholder="Ej. Comercial Guatemala, S.A."
                onChange={(event) =>
                  updateForm(
                    "name",
                    event.target.value,
                  )
                }
              />
            </label>

            <label className="form-field">
              <span>NIT</span>

              <input
                className="text-control"
                required
                maxLength={30}
                value={form.nit}
                placeholder="9000001-9"
                onChange={(event) =>
                  updateForm(
                    "nit",
                    event.target.value,
                  )
                }
              />
            </label>

            <label className="form-field">
              <span>Categoría</span>

              <select
                className="select-control"
                value={form.category_id}
                onChange={(event) =>
                  updateForm(
                    "category_id",
                    event.target.value,
                  )
                }
              >
                <option value="">
                  Sin categoría
                </option>

                {categories.map(
                  (category) => (
                    <option
                      key={category.id}
                      value={category.id}
                    >
                      {category.name}
                    </option>
                  ),
                )}
              </select>
            </label>

            <label className="form-field">
              <span>
                Correo electrónico
              </span>

              <input
                className="text-control"
                type="email"
                value={form.email}
                placeholder="facturacion@empresa.com"
                onChange={(event) =>
                  updateForm(
                    "email",
                    event.target.value,
                  )
                }
              />
            </label>

            <label className="form-field">
              <span>Teléfono</span>

              <input
                className="text-control"
                maxLength={30}
                value={form.phone}
                placeholder="2222-0000"
                onChange={(event) =>
                  updateForm(
                    "phone",
                    event.target.value,
                  )
                }
              />
            </label>

            <label className="form-field form-field-wide">
              <span>Dirección</span>

              <textarea
                className="textarea-control"
                rows={3}
                maxLength={500}
                value={form.address}
                placeholder="Dirección comercial del proveedor"
                onChange={(event) =>
                  updateForm(
                    "address",
                    event.target.value,
                  )
                }
              />
            </label>
          </div>

          {formError && (
            <div className="form-alert form-alert-error">
              {formError}
            </div>
          )}

          <footer className="modal-actions">
            <button
              className="secondary-button"
              type="button"
              disabled={saving}
              onClick={closeModal}
            >
              Cancelar
            </button>

            <button
              className="primary-button"
              type="submit"
              disabled={saving}
            >
              {saving && (
                <LoaderCircle
                  className="spin"
                  size={17}
                />
              )}

              {editingProvider
                ? "Guardar cambios"
                : "Crear proveedor"}
            </button>
          </footer>
        </form>
      </Modal>
    </div>
  );
}
