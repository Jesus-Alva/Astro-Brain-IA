'use client';

import { useEffect, useState } from 'react';
import {
  crearConversacion,
  eliminarConversacion,
  listarConversaciones,
  ConversationSummary,
} from '@/lib/api';

interface ListaConversacionesProps {
  conversacionActual: string | null;
  onSeleccionar: (id: string) => void;
  onNueva: (id: string) => void;
  onEliminada: (id: string) => void;
  recargarTrigger: number;
}

export function ListaConversaciones({
  conversacionActual,
  onSeleccionar,
  onNueva,
  onEliminada,
  recargarTrigger,
}: ListaConversacionesProps) {
  const [conversaciones, setConversaciones] = useState<ConversationSummary[]>([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const cargar = async () => {
      setCargando(true);
      try {
        setConversaciones(await listarConversaciones());
      } finally {
        setCargando(false);
      }
    };
    cargar();
  }, [recargarTrigger]);

  const nueva = async () => {
    const conversacion = await crearConversacion();
    setConversaciones((prev) => [conversacion, ...prev]);
    onNueva(conversacion.id);
  };

  const eliminar = async (id: string) => {
    await eliminarConversacion(id);
    setConversaciones((prev) => prev.filter((conversacion) => conversacion.id !== id));
    onEliminada(id);
  };

  return (
    <section className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">💬 Conversaciones</h3>
        <button
          type="button"
          onClick={nueva}
          className="rounded-lg px-2 py-1 text-lg hover:bg-gray-100 dark:hover:bg-gray-700"
          title="Nueva conversación"
        >
          ➕
        </button>
      </div>
      {cargando ? (
        <p className="text-xs text-gray-500">Cargando...</p>
      ) : (
        <div className="max-h-64 space-y-2 overflow-y-auto">
          {conversaciones.map((conversacion) => (
            <div key={conversacion.id} className="flex items-center gap-2">
              <button
                type="button"
                onClick={() => onSeleccionar(conversacion.id)}
                className={`min-w-0 flex-1 truncate rounded-lg px-3 py-2 text-left text-sm ${conversacionActual === conversacion.id ? 'bg-purple-100 dark:bg-purple-900/40' : 'bg-gray-100 dark:bg-gray-700'}`}
              >
                {conversacion.titulo}
              </button>
              <button
                type="button"
                onClick={() => eliminar(conversacion.id)}
                className="px-2 py-2 text-red-500 hover:text-red-700"
                title="Eliminar conversación"
              >
                🗑️
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
