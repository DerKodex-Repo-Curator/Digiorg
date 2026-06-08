export default function BrainThought({ thought, latest_action }) {
  return (
    <div className="brain-container">
      <h2>Thought</h2>
      {thought ? (
        <p className="thought-text">💭 {thought}</p>
      ) : (
        <p className="thought-empty">No thought recorded yet.</p>
      )}
      {latest_action && (
        <div className="latest-action">
          <span className="action-label">LAST AUTONOMOUS ACTION</span>
          <p className="action-description">{latest_action.description}</p>
          <span className="action-time">
            {new Date(latest_action.created_at).toLocaleTimeString()}
          </span>
        </div>
      )}
    </div>
  );
}