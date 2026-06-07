export default function BrainThought({ thought, latest_action }) {
  return (
    <div className="brain-container">
      <h2>Pensamiento</h2>
      {thought ? (
        <p className="thought-text">
          💭 {thought.replace("Digiorg piensa: ", "")}
        </p>
      ) : (
        <p className="thought-empty">Sin pensamiento registrado aún.</p>
      )}
      {latest_action && (
        <div className="latest-action">
          <span className="action-label">ÚLTIMA ACCIÓN AUTÓNOMA</span>
          <p className="action-description">{latest_action.description}</p>
          <span className="action-time">
            {new Date(latest_action.created_at).toLocaleTimeString()}
          </span>
        </div>
      )}
    </div>
  );
}