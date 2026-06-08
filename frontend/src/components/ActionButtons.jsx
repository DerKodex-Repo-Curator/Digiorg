const ACTIONS = [
  { id: "feed",   label: "🍖 Feed",    color: "#4ade80" },
  { id: "sleep",  label: "💤 Sleep",   color: "#818cf8" },
  { id: "clean",  label: "🚿 Clean",   color: "#38bdf8" },
  { id: "revive", label: "⚡ Revive",  color: "#f59e0b" },
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