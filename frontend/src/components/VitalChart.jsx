import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";

export default function VitalChart({ history }) {
  if (history.length < 2) {
    return <p className="chart-empty">Acumulando datos...</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={history}>
        <XAxis dataKey="t" tick={{ fontSize: 10 }} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 10 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="energy"     stroke="#4ade80" dot={false} strokeWidth={2} />
        <Line type="monotone" dataKey="hunger"     stroke="#f87171" dot={false} strokeWidth={2} />
        <Line type="monotone" dataKey="sleepiness" stroke="#818cf8" dot={false} strokeWidth={2} />
        <Line type="monotone" dataKey="hygiene"    stroke="#38bdf8" dot={false} strokeWidth={2} />
      </LineChart>
    </ResponsiveContainer>
  );
}