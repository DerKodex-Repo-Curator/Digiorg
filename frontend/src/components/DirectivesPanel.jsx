import { useState } from "react";

const API_URL = "http://127.0.0.1:8000";

export default function DirectivesPanel({ directives, onRefresh }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const handleCreate = async () => {
    if (!name.trim() || !description.trim()) {
      setError("Nombre y descripción son obligatorios.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/directives`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: name.trim(), description: description.trim() }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Error al crear la directriz.");
      } else {
        setName("");
        setDescription("");
        onRefresh?.();
      }
    } catch {
      setError("No se pudo conectar con la API.");
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (directiveName, currentStatus) => {
    try {
      await fetch(`${API_URL}/directives/${directiveName}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !currentStatus }),
      });
      onRefresh?.();
    } catch {
      setError("No se pudo actualizar la directriz.");
    }
  };

  const handleDelete = async (directiveName) => {
    if (confirmDelete !== directiveName) {
      setConfirmDelete(directiveName);
      return;
    }
    try {
      await fetch(`${API_URL}/directives/${directiveName}`, {
        method: "DELETE",
      });
      setConfirmDelete(null);
      onRefresh?.();
    } catch {
      setError("No se pudo eliminar la directriz.");
    }
  };

  return (
    <div className="directives-panel">
      <h2>Directivas</h2>

      <div className="directives-list-full">
        {directives.length === 0 && (
          <p className="no-directives-msg">No hay directivas creadas.</p>
        )}
        {directives.map((d) => (
          <div key={d.id} className={`directive-row ${d.is_active ? "active" : "inactive"}`}>
            <div className="directive-info">
              <span className="directive-name">{d.name}</span>
              <span className="directive-desc">{d.description}</span>
            </div>
            <div className="directive-actions">
              <button
                className={`toggle-btn ${d.is_active ? "on" : "off"}`}
                onClick={() => handleToggle(d.name, d.is_active)}
              >
                {d.is_active ? "Activa" : "Inactiva"}
              </button>
              <button
                className={`delete-btn ${confirmDelete === d.name ? "confirm" : ""}`}
                onClick={() => handleDelete(d.name)}
                title={confirmDelete === d.name ? "Pulsa de nuevo para confirmar" : "Eliminar"}
              >
                {confirmDelete === d.name ? "¿Seguro?" : "✕"}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="directive-form">
        <h3>Nueva directriz</h3>
        <input
          className="directive-input"
          placeholder="Nombre (ej: evitar_hambre_critica)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="directive-input"
          placeholder="Descripción"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        {error && <p className="directive-error">{error}</p>}
        <button
          className="directive-create-btn"
          onClick={handleCreate}
          disabled={loading}
        >
          {loading ? "Creando..." : "Crear directriz"}
        </button>
      </div>
    </div>
  );
}