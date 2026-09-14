'use client';

import { useState } from 'react';
import { useStats } from '@/hooks/useStats';

export function StatsDashboard() {
  const [expandido, setExpandido] = useState(false);
  const { stats, sesion, loading } = useStats(5000);

  if (loading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="animate-pulse text-gray-500 dark:text-gray-400">Cargando estadísticas...</div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 overflow-hidden shadow-sm">
      <button
        onClick={() => setExpandido(!expandido)}
        className="w-full p-4 flex justify-between items-center hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="sidebar-title-icon text-xl" title="Estadísticas">📊</span>
          <span className="sidebar-label font-semibold text-gray-900 dark:text-white">Estadísticas</span>
          <span className="sidebar-detail text-xs bg-purple-500/20 text-purple-600 dark:text-purple-300 px-2 py-1 rounded">
            {stats.largo_plazo.total_items} items
          </span>
        </div>
        <span className="sidebar-detail text-gray-500 dark:text-gray-400">{expandido ? '▼' : '▶'}</span>
      </button>

      {expandido && (
        <div className="sidebar-detail p-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">💭 Corto Plazo</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.corto_plazo.items_actuales}
                <span className="text-sm text-gray-500 dark:text-gray-400 font-normal">
                  /{stats.corto_plazo.capacidad}
                </span>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stats.corto_plazo.mensajes} mensajes • {stats.corto_plazo.hechos} hechos
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-1">📚 Largo Plazo</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats.largo_plazo.total_items}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {stats.largo_plazo.total_etiquetas_unicas} etiquetas únicas
              </div>
            </div>
          </div>

          {Object.keys(stats.largo_plazo.categorias).length > 0 && (
            <div>
              <div className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">📂 Categorías</div>
              <div className="space-y-1">
                {Object.entries(stats.largo_plazo.categorias)
                  .sort(([, a], [, b]) => b - a)
                  .slice(0, 5)
                  .map(([cat, count]) => (
                    <div key={cat} className="flex items-center gap-2">
                      <div className="flex-1 text-xs text-gray-600 dark:text-gray-400 truncate">{cat}</div>
                      <div className="w-24 bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-blue-500 h-full"
                          style={{
                            width: `${(count / stats.largo_plazo.total_items) * 100}%`,
                          }}
                        />
                      </div>
                      <div className="text-xs text-gray-700 dark:text-gray-300 w-8 text-right">{count}</div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {sesion && (
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3">
              <div className="text-xs text-gray-600 dark:text-gray-400 mb-2">⏱️ Sesión Actual</div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">{sesion.duracion_minutos}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">minutos</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">{sesion.total_mensajes}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">mensajes</div>
                </div>
                <div>
                  <div className="text-lg font-bold text-gray-900 dark:text-white">{sesion.total_hechos}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">hechos</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}