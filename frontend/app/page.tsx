"use client";

import { useEffect, useState } from "react";
import fondo from "./fondo.png";

const API = process.env.NEXT_PUBLIC_API_URL!;

type Estacion = {
  id: string | number;
  nombre: string;
  provincia: string;
};

type HealthInfo = Record<string, unknown>;

type EstacionInfo = Record<string, unknown>;

type PrediccionItem = {
  fecha: string;
  temperatura_max: number | string;
  temperatura_min: number | string;
  precipitacion: number | string;
  humedad: number | string;
};

type PrediccionInfo = {
  estacion_nombre: string;
  provincia: string;
  dias_predichos: number | string;
  fecha_generacion: string;
  predicciones: PrediccionItem[];
  promedios: {
    temperatura_max_promedio: number | string;
    temperatura_min_promedio: number | string;
    precipitacion_acumulada: number | string;
    humedad_promedio: number | string;
  };
};

const formatNumber = (value: number) => {
  const decimals = Number.isInteger(value * 100) ? 2 : 3;
  return value.toFixed(decimals);
};

const formatDisplayValue = (value: unknown) => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return formatNumber(value);
  }

  if (typeof value === "string") {
    const trimmed = value.trim();

    if (trimmed !== "" && !Number.isNaN(Number(trimmed))) {
      return formatNumber(Number(trimmed));
    }
  }

  return String(value);
};

export default function Home() {

  const [estaciones, setEstaciones] = useState<Estacion[]>([]);
  const [selectedStation, setSelectedStation] = useState("");

  const [dias, setDias] = useState(7);

  const [healthInfo, setHealthInfo] = useState<HealthInfo | null>(null);

  const [estacionInfo, setEstacionInfo] = useState<EstacionInfo | null>(null);

  const [prediccion, setPrediccion] = useState<PrediccionInfo | null>(null);

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    listarEstaciones();
  }, []);

  const listarEstaciones = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API}/estaciones`);
      const data = await response.json();

      if (response.ok) {
        setEstaciones(data.estaciones || []);
        setMensaje("Estaciones cargadas correctamente.");
      } else {
        setError(data.detail || "No se pudieron cargar las estaciones.");
      }
    } catch {
      setError("No se pudo conectar con la API.");
    } finally {
      setLoading(false);
    }
  };

  const consultarEstacion = async () => {

    if (!selectedStation) {
      alert("Seleccione una estación.");
      return;
    }

    try {

      setLoading(true);
      setError("");

      const response = await fetch(
        `${API}/estacion/${selectedStation}`
      );

      const data = await response.json();

      if (response.ok) {
        setEstacionInfo(data);
        setMensaje("Información obtenida.");
      } else {
        setError(data.detail || "No se encontró la estación.");
      }

    } catch {
      setError("Error conectando con la API.");
    } finally {

      setLoading(false);

    }

  };

  const predecirClima = async () => {

    if (!selectedStation) {
      alert("Seleccione una estación.");
      return;
    }

    try {

      setLoading(true);
      setError("");

      const response = await fetch(`${API}/predecir`, {

        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          estacion_id: selectedStation,
          dias: dias,
        }),

      });

      const data = await response.json();

      if (response.ok) {

        setPrediccion(data);

        setMensaje("Predicción generada.");

      } else {

        setError(data.detail || "No fue posible generar la predicción.");

      }

    } catch {

      setError("No se pudo conectar con la API.");

    } finally {

      setLoading(false);

    }

  };

  const health = async () => {

    try {

      setLoading(true);
      setError("");

      const response = await fetch(`${API}/health`);

      const data = await response.json();

      if (response.ok) {

        setHealthInfo(data);

        setMensaje("API funcionando correctamente.");

      } else {

        setError("No fue posible obtener el estado.");

      }

    } catch {
      setError("No se pudo conectar con la API.");
    } finally {
      setLoading(false);
    }

  };

  return (
    <div
      className="momo-trust-display-regular min-h-screen bg-slate-950 bg-cover bg-center bg-no-repeat px-4 py-8 text-white md:px-8"
      style={{ backgroundImage: `url(${fondo.src})` }}
    >

      <div className="mx-auto w-full max-w-6xl rounded-[2rem] border border-white/15 bg-slate-950/70 p-6 shadow-2xl shadow-cyan-950/30 backdrop-blur md:p-10">

        <div className="flex flex-col gap-8 lg:flex-row lg:items-start lg:justify-between">

          <div className="max-w-3xl">
            <span className="inline-flex rounded-full border border-cyan-300/40 bg-cyan-300/10 px-4 py-1 text-sm uppercase tracking-[0.28em] text-cyan-100">
              Proyecto de Big Data - Grupo C
            </span>

            <h1 className="mt-5 text-4xl leading-tight text-white md:text-6xl">
              Sistema Inteligente de Prediccion Climática
            </h1>

            <p className="mt-4 max-w-2xl text-base text-slate-200 md:text-lg">
              Explora estaciones, consulta el estado de la API y genera pronósticos con una interfaz inspirada en paneles meteorológicos modernos.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 self-stretch sm:max-w-sm">
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <div className="text-xs uppercase tracking-[0.22em] text-cyan-100/80">Fuente</div>
              <div className="mt-2 text-lg text-white">SENAMHI</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <div className="text-xs uppercase tracking-[0.22em] text-cyan-100/80">Modelo</div>
              <div className="mt-2 text-lg text-white">LSTM</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <div className="text-xs uppercase tracking-[0.22em] text-cyan-100/80">Estaciones</div>
              <div className="mt-2 text-lg text-white">{estaciones.length}</div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/10 p-4 backdrop-blur">
              <div className="text-xs uppercase tracking-[0.22em] text-cyan-100/80">Horizonte</div>
              <div className="mt-2 text-lg text-white">{dias} dias</div>
            </div>
          </div>

        </div>

        <div className="mt-7 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">

          <button
            onClick={listarEstaciones}
            className="rounded-2xl border border-cyan-300/30 bg-cyan-400/10 p-6 text-left transition hover:-translate-y-1 hover:bg-cyan-300/20"
          >
            <div className="text-sm uppercase tracking-[0.22em] text-cyan-100/80">
              01
            </div>

            <h3 className="mt-3 text-xl text-white">
              Estaciones
            </h3>

            <p className="mt-2 text-sm text-slate-200">
              Obtener estaciones disponibles
            </p>

          </button>

          <button
            onClick={consultarEstacion}
            className="rounded-2xl border border-sky-300/30 bg-sky-400/10 p-6 text-left transition hover:-translate-y-1 hover:bg-sky-300/20"
          >
            <div className="text-sm uppercase tracking-[0.22em] text-sky-100/80">
              02
            </div>

            <h3 className="mt-3 text-xl text-white">
              Información
            </h3>

            <p className="mt-2 text-sm text-slate-200">
              Consultar datos del modelo
            </p>

          </button>

          <button
            onClick={predecirClima}
            className="rounded-2xl border border-emerald-300/30 bg-emerald-400/10 p-6 text-left transition hover:-translate-y-1 hover:bg-emerald-300/20"
          >
            <div className="text-sm uppercase tracking-[0.22em] text-emerald-100/80">
              03
            </div>

            <h3 className="mt-3 text-xl text-white">
              Predicción
            </h3>

            <p className="mt-2 text-sm text-slate-200">
              Generar pronóstico climático
            </p>

          </button>

          <button
            onClick={health}
            className="rounded-2xl border border-amber-300/30 bg-amber-400/10 p-6 text-left transition hover:-translate-y-1 hover:bg-amber-300/20"
          >
            <div className="text-sm uppercase tracking-[0.22em] text-amber-100/80">
              04
            </div>

            <h3 className="mt-3 text-xl text-white">
              Estado API
            </h3>

            <p className="mt-2 text-sm text-slate-200">
              Verificar disponibilidad
            </p>

          </button>

        </div>

        <div className="mt-7 grid gap-6 lg:grid-cols-[1.4fr_0.8fr]">

          <div className="rounded-[1.75rem] border border-white/10 bg-white/10 p-6 backdrop-blur">

            <label className="mb-2 block text-sm uppercase tracking-[0.18em] text-cyan-100/80">
              Estación
            </label>

            <select
              className="w-full rounded-xl border border-white/15 bg-slate-950/60 p-3 text-white outline-none transition placeholder:text-slate-400 focus:border-cyan-300"
              value={selectedStation}
              onChange={(e) => setSelectedStation(e.target.value)}
            >

              <option value="">Seleccione una estación</option>

              {estaciones.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.nombre} - {e.provincia}
                </option>
              ))}

            </select>

          </div>

          <div className="rounded-[1.75rem] border border-white/10 bg-white/10 p-6 backdrop-blur">

            <label className="mb-2 block text-sm uppercase tracking-[0.18em] text-cyan-100/80">
              Días a predecir
            </label>

            <input
              type="number"
              className="w-full rounded-xl border border-white/15 bg-slate-950/60 p-3 text-white outline-none transition focus:border-cyan-300"
              min={1}
              max={30}
              value={dias}
              onChange={(e) => setDias(Number(e.target.value))}
            />

          </div>

        </div>

        <button
          onClick={predecirClima}
          className="mt-8 w-full rounded-2xl bg-gradient-to-r from-cyan-400 via-sky-500 to-indigo-500 p-4 text-lg text-slate-950 transition hover:brightness-110"
        >
          Generar Predicción
        </button>

        {loading && (

          <div className="mt-8 rounded-2xl border border-cyan-300/20 bg-cyan-400/10 p-4 text-center text-cyan-100">
            Cargando...
          </div>

        )}

        {error && (

          <div className="mt-8 rounded-2xl border border-rose-300/30 bg-rose-400/10 p-4 text-rose-100">
            {error}
          </div>

        )}

        {mensaje && (

          <div className="mt-8 rounded-2xl border border-emerald-300/30 bg-emerald-400/10 p-4 text-emerald-100">
            {mensaje}
          </div>

        )}

        {healthInfo && (
          <div className="mt-10 rounded-[1.75rem] border border-white/10 bg-white/10 p-6 backdrop-blur">
            <h2 className="mb-4 text-2xl text-amber-200">
              Estado de la API
            </h2>

            <pre className="overflow-auto rounded-2xl bg-slate-950/70 p-4 text-sm text-slate-100">
              {JSON.stringify(healthInfo, null, 2)}
            </pre>
          </div>
        )}

        {estacionInfo && (
          <div className="mt-10 rounded-[1.75rem] border border-white/10 bg-white/10 p-6 backdrop-blur">

            <h2 className="mb-5 text-2xl text-sky-200">
              Información de la estación
            </h2>

            <div className="grid gap-4 md:grid-cols-2">

              {Object.entries(estacionInfo).map(([key, value]) => (

                <div
                  key={key}
                  className="rounded-2xl border border-white/10 bg-slate-950/60 p-4"
                >
                  <div className="uppercase tracking-[0.16em] text-slate-400">
                    {key}
                  </div>

                  <div className="mt-2 text-lg text-white">
                    {formatDisplayValue(value)}
                  </div>

                </div>

              ))}

            </div>

          </div>
        )}

        {prediccion && (

          <div className="mt-10 rounded-[1.75rem] border border-white/10 bg-white/10 p-6 backdrop-blur">

            <h2 className="mb-4 text-2xl text-emerald-200">
              Predicción Climática
            </h2>

            <div className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                <b>Estación</b><br />
                {prediccion.estacion_nombre}
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                <b>Provincia</b><br />
                {prediccion.provincia}
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                <b>Días predichos</b><br />
                {prediccion.dias_predichos}
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                <b>Fecha generación</b><br />
                {prediccion.fecha_generacion}
              </div>

            </div>

            <h3 className="mb-3 text-xl text-white">
              Predicciones
            </h3>

            <div className="overflow-auto rounded-2xl border border-white/10">

              <table className="min-w-full bg-slate-950/50 text-slate-100">

                <thead className="bg-gradient-to-r from-cyan-500 to-sky-600 text-slate-950">

                  <tr>

                    <th className="px-4 py-3">Fecha</th>
                    <th className="px-4 py-3">T. Máx</th>
                    <th className="px-4 py-3">T. Mín</th>
                    <th className="px-4 py-3">Precipitación</th>
                    <th className="px-4 py-3">Humedad</th>

                  </tr>

                </thead>

                <tbody>

                  {prediccion.predicciones.map((p, index: number) => (

                    <tr
                      key={index}
                      className="border-b border-white/5 hover:bg-white/5"
                    >

                      <td className="px-4 py-2">{p.fecha}</td>

                        <td className="px-4 py-2">{formatDisplayValue(p.temperatura_max)} °C</td>

                        <td className="px-4 py-2">{formatDisplayValue(p.temperatura_min)} °C</td>

                        <td className="px-4 py-2">{formatDisplayValue(p.precipitacion)} mm</td>

                        <td className="px-4 py-2">{formatDisplayValue(p.humedad)} %</td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

            <h3 className="mt-8 mb-3 text-xl text-white">
              Promedios
            </h3>

            <div className="grid gap-4 md:grid-cols-2">

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                Temperatura Máxima Promedio
                <div className="text-2xl text-white">
                  {formatDisplayValue(prediccion.promedios.temperatura_max_promedio)} °C
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                Temperatura Mínima Promedio
                <div className="text-2xl text-white">
                  {formatDisplayValue(prediccion.promedios.temperatura_min_promedio)} °C
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                Precipitación Acumulada
                <div className="text-2xl text-white">
                  {formatDisplayValue(prediccion.promedios.precipitacion_acumulada)} mm
                </div>
              </div>

              <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-slate-100">
                Humedad Promedio
                <div className="text-2xl text-white">
                  {formatDisplayValue(prediccion.promedios.humedad_promedio)} %
                </div>
              </div>

            </div>

          </div>

        )}

      </div>

    </div>

  );
}
