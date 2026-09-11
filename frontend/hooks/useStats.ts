'use client';

import { useState, useEffect } from 'react';
import { obtenerEstadisticasMemoria, obtenerResumenSesion } from '@/lib/api';
import { EstadisticasMemoria, ResumenSesion } from '@/types';

export function useStats(refreshInterval: number = 5000) {
  const [stats, setStats] = useState<EstadisticasMemoria | null>(null);
  const [sesion, setSesion] = useState<ResumenSesion | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const cargarStats = async () => {
    try {
      const [statsData, sesionData] = await Promise.all([
        obtenerEstadisticasMemoria(),
        obtenerResumenSesion(),
      ]);
      setStats(statsData);
      setSesion(sesionData);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarStats();
    const interval = setInterval(cargarStats, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  return { stats, sesion, loading, error, refrescar: cargarStats };
}