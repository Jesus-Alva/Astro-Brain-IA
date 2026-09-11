'use client';

import { useState, useEffect } from 'react';
import { obtenerEstadisticasFeedback, EstadisticasFeedback } from '@/lib/api';

export function FeedbackStats() {
    const [stats, setStats] = useState<EstadisticasFeedback | null>(null);
    const [loading, setLoading] = useState(true);

    const cargar = async () => {
        try {
            const data = await obtenerEstadisticasFeedback();
            setStats(data);
            console.log('📊 Feedback stats:', data);
        } catch (error) {
            console.error('Error cargando feedback:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        cargar();

        // ✅ Escuchar evento de actualización
        const handleUpdate = () => {
            console.log('🔄 Refrescando feedback...');
            cargar();
        };
        window.addEventListener('feedback-updated', handleUpdate);

        // Refresco automático cada 5 segundos
        const interval = setInterval(cargar, 5000);

        return () => {
            window.removeEventListener('feedback-updated', handleUpdate);
            clearInterval(interval);
        };
    }, []);

    if (loading) {
        return (
            <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
                <div className="animate-pulse text-gray-500 dark:text-gray-400 text-sm">
                    Cargando feedback...
                </div>
            </div>
        );
    }

    if (!stats) return null;

    return (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                ⭐ Feedback
            </h3>

            <div className="space-y-3">
                <div>
                    <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-600 dark:text-gray-400">
                            Tasa de aceptación
                        </span>
                        <span className="text-gray-900 dark:text-white font-semibold">
                            {stats.tasa_aceptacion}%
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-green-500 to-emerald-500 h-full transition-all duration-500"
                            style={{ width: `${stats.tasa_aceptacion}%` }}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                    <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-2 text-center">
                        <div className="text-lg font-bold text-green-600 dark:text-green-400">
                            {stats.positivos}
                        </div>
                        <div className="text-xs text-green-700 dark:text-green-500">
                            👍 Positivos
                        </div>
                    </div>
                    <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-2 text-center">
                        <div className="text-lg font-bold text-red-600 dark:text-red-400">
                            {stats.negativos}
                        </div>
                        <div className="text-xs text-red-700 dark:text-red-500">
                            👎 Negativos
                        </div>
                    </div>
                </div>

                <div className="text-xs text-gray-500 dark:text-gray-400 text-center">
                    Total: {stats.total_feedback} feedbacks
                </div>
            </div>
        </div>
    );
}