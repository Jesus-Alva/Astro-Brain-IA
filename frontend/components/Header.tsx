'use client';

import { useTheme } from '@/hooks/useTheme';

interface HeaderProps {
    isConnected: boolean;
    usuario: string;
    personalidad: string;
    onPersonalidadChange: (personalidad: string) => void;
    onLogout: () => void;
}

export function Header({ isConnected, usuario, personalidad, onPersonalidadChange, onLogout }: HeaderProps) {
    const { tema, toggleTema, montado } = useTheme();

    // Evitar hidratación incorrecta
    if (!montado) {
        return (
            <header className="flex justify-between items-center mb-6 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700">
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-linear-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-2xl">
                        🧠
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Astro-IA</h1>
                    </div>
                </div>
            </header>
        );
    }

    return (
        <header className="flex justify-between items-center mb-6 p-4 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-linear-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-2xl">
                    🧠
                </div>
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Astro-IA</h1>
                    <div className="flex items-center gap-2 text-sm">
                        <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                        <span className="text-gray-600 dark:text-gray-400">
                            {isConnected ? 'Backend Online' : 'Backend Offline'}
                        </span>
                        <span className="text-gray-400 dark:text-gray-500">•</span>
                        <span className="text-gray-600 dark:text-gray-400">👤 {usuario}</span>
                    </div>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <select
                    value={personalidad}
                    onChange={(e) => onPersonalidadChange(e.target.value)}
                    className="bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg px-4 py-2 border border-gray-300 dark:border-gray-600 focus:outline-none focus:border-purple-500"
                >
                    <option value="amigable">😊 Amigable</option>
                    <option value="profesional">💼 Profesional</option>
                    <option value="creativo">🎨 Creativo</option>
                    <option value="sarcastico">😏 Sarcástico</option>
                </select>

                <button
                    onClick={toggleTema}
                    className="p-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                    title={tema === 'oscuro' ? 'Cambiar a claro' : 'Cambiar a oscuro'}
                >
                    {tema === 'oscuro' ? '☀️' : '🌙'}
                </button>
                <button
                    onClick={onLogout}
                    className="p-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors text-white"
                    title="Cerrar sesión"
                    >
                    🚪
                </button>
            </div>
        </header>
    );
}