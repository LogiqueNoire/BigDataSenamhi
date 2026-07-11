"use client";

import { useEffect, useState } from "react";
import "./progressBar.css";

const API = process.env.NEXT_PUBLIC_API_URL!;

export default function Home() {

  const [estaciones, setEstaciones] = useState<any[]>([]);
  const [selectedStation, setSelectedStation] = useState("");

  const [dias, setDias] = useState(7);

  const [healthInfo, setHealthInfo] = useState<any>(null);

  const [estacionInfo, setEstacionInfo] = useState<any>(null);

  const [prediccion, setPrediccion] = useState<any>(null);

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
    <div className="min-h-screen bg-slate-100 flex justify-center items-center p-10">

      <div className="bg-white rounded-2xl shadow-xl w-full max-w-5xl p-10">

        <h1 className="text-5xl font-bold text-center text-teal-700">
          Sistema Inteligente de Predicción Climática
        </h1>

        <p className="text-center text-gray-500 mt-3 text-lg">
          Modelos LSTM entrenados con datos del SENAMHI
        </p>

        <div className="grid grid-cols-4 gap-4 mt-10">

          <button
            onClick={listarEstaciones}
            className="rounded-xl border-2 border-teal-600 p-6 hover:bg-teal-50 transition"
          >
            <h3 className="font-bold mt-3">
              Estaciones
            </h3>

            <p className="text-sm text-gray-500 mt-2">
              Obtener estaciones disponibles
            </p>

          </button>

          <button
            onClick={consultarEstacion}
            className="rounded-xl border-2 border-blue-600 p-6 hover:bg-blue-50 transition"
          >
            <h3 className="font-bold mt-3">
              Información
            </h3>

            <p className="text-sm text-gray-500 mt-2">
              Consultar datos del modelo
            </p>

          </button>

          <button
            onClick={predecirClima}
            className="rounded-xl border-2 border-green-600 p-6 hover:bg-green-50 transition"
          >
            <h3 className="font-bold mt-3">
              Predicción
            </h3>

            <p className="text-sm text-gray-500 mt-2">
              Generar pronóstico climático
            </p>

          </button>

          <button
            onClick={health}
            className="rounded-xl border-2 border-orange-600 p-6 hover:bg-orange-50 transition"
          >
            <h3 className="font-bold mt-3">
              Estado API
            </h3>

            <p className="text-sm text-gray-500 mt-2">
              Verificar disponibilidad
            </p>

          </button>

        </div>

        <div className="mt-10">

          <label className="block font-semibold mb-2">
            Estación
          </label>

          <select
            className="w-full border rounded-lg p-3"
            value={selectedStation}
            onChange={(e) => setSelectedStation(e.target.value)}
          >

            <option value="">
              Seleccione una estación
            </option>

            {estaciones.map((e: any) => (
              <option key={e.id} value={e.id}>
                {e.nombre} - {e.provincia}
              </option>
            ))}

          </select>

        </div>

        <div className="mt-6">

          <label className="block font-semibold mb-2">
            Días a predecir
          </label>

          <input
            type="number"
            className="w-full border rounded-lg p-3"
            min={1}
            max={30}
            value={dias}
            onChange={(e) => setDias(Number(e.target.value))}
          />

        </div>

        <button
          onClick={predecirClima}
          className="mt-8 w-full bg-teal-700 hover:bg-teal-800 text-white rounded-xl p-4 text-lg"
        >
          Generar Predicción
        </button>

        {loading && (

          <div className="mt-8 text-center text-blue-600 font-semibold">
            Cargando...
          </div>

        )}

        {error && (

          <div className="mt-8 bg-red-100 border border-red-400 rounded-lg p-4 text-red-700">
            {error}
          </div>

        )}

        {mensaje && (

          <div className="mt-8 bg-green-100 border border-green-400 rounded-lg p-4 text-green-700">
            {mensaje}
          </div>

        )}

        {healthInfo && (
          <div className="mt-10 rounded-xl border p-6 bg-slate-50">
            <h2 className="text-2xl font-bold text-orange-600 mb-4">
              Estado de la API
            </h2>

            <pre className="bg-white rounded-lg p-4 overflow-auto text-sm">
              {JSON.stringify(healthInfo, null, 2)}
            </pre>
          </div>
        )}

        {estacionInfo && (
          <div className="mt-10 rounded-xl border p-6 bg-slate-50">

            <h2 className="text-2xl font-bold text-blue-600 mb-5">
              Información de la estación
            </h2>

            <div className="grid grid-cols-2 gap-4">

              {Object.entries(estacionInfo).map(([key, value]) => (

                <div
                  key={key}
                  className="border rounded-lg p-4 bg-white"
                >
                  <div className="font-semibold text-slate-500">
                    {key}
                  </div>

                  <div className="mt-2 text-lg">
                    {String(value)}
                  </div>

                </div>

              ))}

            </div>

          </div>
        )}

        {prediccion && (

          <div className="mt-10">

            <h2 className="text-2xl font-bold text-green-700 mb-4">
              Predicción Climática
            </h2>

            <div className="grid grid-cols-2 gap-4 mb-8">

              <div className="border rounded-lg p-4 bg-white">
                <b>Estación</b><br />
                {prediccion.estacion_nombre}
              </div>

              <div className="border rounded-lg p-4 bg-white">
                <b>Provincia</b><br />
                {prediccion.provincia}
              </div>

              <div className="border rounded-lg p-4 bg-white">
                <b>Días predichos</b><br />
                {prediccion.dias_predichos}
              </div>

              <div className="border rounded-lg p-4 bg-white">
                <b>Fecha generación</b><br />
                {prediccion.fecha_generacion}
              </div>

            </div>

            <h3 className="text-xl font-semibold mb-3">
              Predicciones
            </h3>

            <div className="overflow-auto border rounded-lg">

              <table className="min-w-full">

                <thead className="bg-teal-700 text-white">

                  <tr>

                    <th className="px-4 py-3">Fecha</th>
                    <th className="px-4 py-3">T. Máx</th>
                    <th className="px-4 py-3">T. Mín</th>
                    <th className="px-4 py-3">Precipitación</th>
                    <th className="px-4 py-3">Humedad</th>

                  </tr>

                </thead>

                <tbody>

                  {prediccion.predicciones.map((p: any, index: number) => (

                    <tr
                      key={index}
                      className="border-b hover:bg-slate-50"
                    >

                      <td className="px-4 py-2">{p.fecha}</td>

                      <td className="px-4 py-2">{p.temperatura_max} °C</td>

                      <td className="px-4 py-2">{p.temperatura_min} °C</td>

                      <td className="px-4 py-2">{p.precipitacion} mm</td>

                      <td className="px-4 py-2">{p.humedad} %</td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

            <h3 className="text-xl font-semibold mt-8 mb-3">
              Promedios
            </h3>

            <div className="grid grid-cols-2 gap-4">

              <div className="border rounded-lg p-4">
                Temperatura Máxima Promedio
                <div className="text-2xl font-bold">
                  {prediccion.promedios.temperatura_max_promedio} °C
                </div>
              </div>

              <div className="border rounded-lg p-4">
                Temperatura Mínima Promedio
                <div className="text-2xl font-bold">
                  {prediccion.promedios.temperatura_min_promedio} °C
                </div>
              </div>

              <div className="border rounded-lg p-4">
                Precipitación Acumulada
                <div className="text-2xl font-bold">
                  {prediccion.promedios.precipitacion_acumulada} mm
                </div>
              </div>

              <div className="border rounded-lg p-4">
                Humedad Promedio
                <div className="text-2xl font-bold">
                  {prediccion.promedios.humedad_promedio} %
                </div>
              </div>

            </div>

          </div>

        )}

      </div>

    </div>

  );
}