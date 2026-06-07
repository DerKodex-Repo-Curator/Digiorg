export default function BodyAvatar({ body, alive }) {
  return (
    <div className="avatar-container">
      <div className={`avatar-face ${alive ? "alive" : "dead"}`}>
        {body.avatar}
      </div>
      <div className="vitality-score">
        <span className="vitality-label">Vitalidad</span>
        <span className="vitality-value">{body.vitality_score}</span>
        <span className="vitality-max">/100</span>
      </div>
      <p className="mood-description">{body.mood_description}</p>
      <p className="physical-description">{body.physical.description}</p>
    </div>
  );
}