const ACTIONS = [
  { id: "feed",   label: "🍖 Alimentar", color: "#4ade80" },
  { id: "sleep",  label: "💤 Dormir",    color: "#818cf8" },
  { id: "clean",  label: "🚿 Limpiar",   color: "#38bdf8" },
  { id: "revive", label: "⚡ Revivir",   color: "#f59e0b" },
];

export default function ActionButtons({ onAction, alive }) {
  return (
    <div className="action-buttons">
      {ACTIONS.map(({ id, label, color }) => {
        const disabled = id !== "revive" ? !alive : alive;
        return (
          <button
            key={id}
            className="action-btn"
            style={{ "--btn-color": color }}
            onClick={() => onAction(id)}
            disabled={disabled}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}