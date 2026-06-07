import { useEffect, useState } from "react";
import StatBar from "./components/StatBar";
import EventLog from "./components/EventLog";
import BrainThought from "./components/BrainThought";
import BodyAvatar from "./components/BodyAvatar";
import ActionButtons from "./components/ActionButtons";
import SafetyStatus from "./components/SafetyStatus";
import VitalChart from "./components/VitalChart";
import DirectivesPanel from "./components/DirectivesPanel";

const WS_URL = "ws://127.0.0.1:8000/ws";
const API_URL = "http://127.0.0.1:8000";

function snapshotToHistory(snapshots) {
  return snapshots
    .slice()
    .reverse()
    .map((s) => ({
      t: new Date(s.recorded_at).toLocaleTimeString(),
      energy: s.energy,
      hunger: s.hunger,
      sleepiness: s.sleepiness,
      hygiene: s.hygiene,
    }));
}

export default function App() {
  const [data, setData] = useState(null);
  const [connected, setConnected] = useState(false);
  const [history, setHistory] = useState([]);
  const [directives, setDirectives] = useState([]);

  const fetchDirectives = async () => {
    try {
      const res = await fetch(`${API_URL}/directives`);
      const data = await res.json();
      setDirectives(data);
    } catch {}
  };

  // Cargar historial persistido al arrancar
  useEffect(() => {
    fetch(`${API_URL}/memory/snapshots?limit=50`)
      .then((r) => r.json())
      .then((snapshots) => {
        if (snapshots.length > 0) {
          setHistory(snapshotToHistory(snapshots));
        }
      })
      .catch(() => {});

    fetchDirectives();
  }, []);

  useEffect(() => {
    let ws;
    let reconnectTimeout;

    const connect = () => {
      ws = new WebSocket(WS_URL);
      ws.onopen = () => setConnected(true);
      ws.onmessage = (event) => {
        const payload = JSON.parse(event.data);
        setData(payload);
        setHistory((prev) =>
          [
            ...prev,
            {
              t: new Date().toLocaleTimeString(),
              energy: payload.state.energy,
              hunger: payload.state.hunger,
              sleepiness: payload.state.sleepiness,
              hygiene: payload.state.hygiene,
            },
          ].slice(-60)
        );
      };
      ws.onclose = () => {
        setConnected(false);
        reconnectTimeout = setTimeout(connect, 3000);
      };
      ws.onerror = () => ws.close();
    };

    connect();
    return () => {
      clearTimeout(reconnectTimeout);
      ws?.close();
    };
  }, []);

  const callAction = async (action) => {
    await fetch(`${API_URL}/action/${action}`, { method: "POST" });
  };

  if (!data) {
    return (
      <div className="loading">
        <p>Conectando con Digiorg...</p>
      </div>
    );
  }

  const { state, body, thought, latest_action, events, safety, scheduler_running } = data;

  return (
    <div className="app">
      <header className="header">
        <div className="header-left">
          <h1>DIGIORG</h1>
          <span className={`status-dot ${connected ? "online" : "offline"}`} />
          <span className="status-label">{connected ? "En línea" : "Desconectado"}</span>
        </div>
        <div className="header-right">
          <span className={`scheduler-badge ${scheduler_running ? "active" : "inactive"}`}>
            {scheduler_running ? "Scheduler activo" : "Scheduler detenido"}
          </span>
          {!safety.safe && (
            <span className="safety-badge">⚠ Alerta de sistema</span>
          )}
        </div>
      </header>

      <main className="grid">
        <section className="card avatar-card">
          <BodyAvatar body={body} mood={state.mood} alive={state.alive} />
        </section>

        <section className="card stats-card">
          <h2>Estado vital</h2>
          <StatBar label="Energía"     value={state.energy}     color="#4ade80" warning={20} danger={10} />
          <StatBar label="Hambre"      value={state.hunger}     color="#f87171" warning={60} danger={80} invert />
          <StatBar label="Somnolencia" value={state.sleepiness} color="#818cf8" warning={60} danger={80} invert />
          <StatBar label="Higiene"     value={state.hygiene}    color="#38bdf8" warning={40} danger={20} />
          <div className="mood-row">
            <span className="mood-label">Humor:</span>
            <span className={`mood-value mood-${state.mood}`}>{state.mood}</span>
          </div>
        </section>

        <section className="card thought-card">
          <BrainThought thought={thought} latest_action={latest_action} />
        </section>

        <section className="card actions-card">
          <h2>Acciones manuales</h2>
          <ActionButtons onAction={callAction} alive={state.alive} />
        </section>

        <section className="card directives-card">
          <DirectivesPanel directives={directives} onRefresh={fetchDirectives} />
        </section>

        <section className="card chart-card">
          <h2>Historial vital</h2>
          <VitalChart history={history} />
        </section>

        <section className="card events-card">
          <h2>Eventos recientes</h2>
          <EventLog events={events} />
        </section>

        <section className="card safety-card">
          <SafetyStatus safety={safety} />
        </section>
      </main>
    </div>
  );
}