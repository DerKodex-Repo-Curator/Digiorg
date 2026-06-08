import { useState } from "react";

const IS_DEV = window.location.hostname === "localhost" && window.location.port === "5173";
const API_URL = IS_DEV ? "http://127.0.0.1:8000" : "";

const TYPE_LABELS = {
  sleep:   { label: "Sleep",   color: "#818cf8", help: "Triggers sleep when sleepiness exceeds threshold" },
  hunger:  { label: "Hunger",  color: "#f87171", help: "Triggers feeding when hunger exceeds threshold" },
  hygiene: { label: "Hygiene", color: "#38bdf8", help: "Triggers cleaning when hygiene falls below threshold" },
  custom:  { label: "Custom",  color: "#a78bfa", help: "LLM-only directive, interpreted from description" },
};

export default function DirectivesPanel({ directives, onRefresh }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [type, setType] = useState("custom");
  const [threshold, setThreshold] = useState(70);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(null);

  const handleCreate = async () => {
    if (!name.trim() || !description.trim()) {
      setError("Name and description are required.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/directives`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim(),
          type,
          threshold: parseInt(threshold),
        }),
      });
      if (!res.ok) {
        const data = await res.json();
        setError(data.detail || "Error creating directive.");
      } else {
        setName("");
        setDescription("");
        setType("custom");
        setThreshold(70);
        onRefresh?.();
      }
    } catch {
      setError("Could not connect to the API.");
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
      setError("Could not update directive.");
    }
  };

  const handleDelete = async (directiveName) => {
    if (confirmDelete !== directiveName) {
      setConfirmDelete(directiveName);
      return;
    }
    try {
      await fetch(`${API_URL}/directives/${directiveName}`, { method: "DELETE" });
      setConfirmDelete(null);
      onRefresh?.();
    } catch {
      setError("Could not delete directive.");
    }
  };

  return (
    <div className="directives-panel">
      <h2>Directives</h2>

      <div className="directives-list-full">
        {directives.length === 0 && (
          <p className="no-directives-msg">No directives created yet.</p>
        )}
        {directives.map((d) => {
          const typeInfo = TYPE_LABELS[d.type] || TYPE_LABELS.custom;
          return (
            <div key={d.id} className={`directive-row ${d.is_active ? "active" : "inactive"}`}>
              <div className="directive-info">
                <div className="directive-header">
                  <span className="directive-name">{d.name}</span>
                  <span className="directive-type-badge" style={{ color: typeInfo.color, borderColor: typeInfo.color }}>
                    {typeInfo.label}
                    {d.type !== "custom" && ` ≥ ${d.threshold}`}
                  </span>
                </div>
                <span className="directive-desc">{d.description}</span>
              </div>
              <div className="directive-actions">
                <button
                  className={`toggle-btn ${d.is_active ? "on" : "off"}`}
                  onClick={() => handleToggle(d.name, d.is_active)}
                >
                  {d.is_active ? "Active" : "Inactive"}
                </button>
                <button
                  className={`delete-btn ${confirmDelete === d.name ? "confirm" : ""}`}
                  onClick={() => handleDelete(d.name)}
                  title={confirmDelete === d.name ? "Click again to confirm" : "Delete"}
                >
                  {confirmDelete === d.name ? "Sure?" : "✕"}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      <div className="directive-form">
        <h3>New directive</h3>
        <input
          className="directive-input"
          placeholder="Name (e.g. avoid_critical_hunger)"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <input
          className="directive-input"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <div className="directive-type-row">
          <select
            className="directive-select"
            value={type}
            onChange={(e) => setType(e.target.value)}
          >
            {Object.entries(TYPE_LABELS).map(([key, val]) => (
              <option key={key} value={key}>{val.label}</option>
            ))}
          </select>
          {type !== "custom" && (
            <div className="directive-threshold">
              <label className="threshold-label">Threshold</label>
              <input
                type="number"
                className="directive-input threshold-input"
                min={1}
                max={100}
                value={threshold}
                onChange={(e) => setThreshold(e.target.value)}
              />
            </div>
          )}
        </div>
        <p className="directive-type-help">{TYPE_LABELS[type]?.help}</p>
        {error && <p className="directive-error">{error}</p>}
        <button
          className="directive-create-btn"
          onClick={handleCreate}
          disabled={loading}
        >
          {loading ? "Creating..." : "Create directive"}
        </button>
      </div>
    </div>
  );
}