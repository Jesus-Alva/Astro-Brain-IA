'use client';

import { useState } from 'react';
import { login, registrar } from '@/lib/api';

interface LoginProps {
  onLoginExitoso: (nombre: string) => void;
}

export function Login({ onLoginExitoso }: LoginProps) {
  const [modo, setModo] = useState<'login' | 'registro'>('login');
  const [nombre, setNombre] = useState('');
  const [password, setPassword] = useState('');
  const [confirmarPassword, setConfirmarPassword] = useState('');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCargando(true);

    try {
      if (modo === 'registro') {
        if (password !== confirmarPassword) {
          throw new Error('Las contraseñas no coinciden');
        }
        if (password.length < 6) {
          throw new Error('La contraseña debe tener al menos 6 caracteres');
        }
        const data = await registrar(nombre, password);
        onLoginExitoso(data.nombre);
      } else {
        const data = await login(nombre, password);
        onLoginExitoso(data.nombre);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 dark:bg-gray-900">
      <div className="w-full max-w-md p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-4xl mx-auto mb-4">
            🧠
          </div>
          <h1 className="text-3xl font-bold text-white">Astro-IA</h1>
          <p className="text-gray-400 mt-2">
            {modo === 'login' ? 'Inicia sesión para continuar' : 'Crea tu cuenta'}
          </p>
        </div>

        {/* Formulario */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Usuario
            </label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Tu nombre de usuario"
              required
              minLength={3}
              className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Tu contraseña"
              required
              minLength={6}
              className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500"
            />
          </div>

          {modo === 'registro' && (
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Confirmar contraseña
              </label>
              <input
                type="password"
                value={confirmarPassword}
                onChange={(e) => setConfirmarPassword(e.target.value)}
                placeholder="Repite la contraseña"
                required
                minLength={6}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500"
              />
            </div>
          )}

          {error && (
            <div className="bg-red-900/30 border border-red-700 rounded-lg p-3">
              <p className="text-red-400 text-sm">❌ {error}</p>
            </div>
          )}

          <button
            type="submit"
            disabled={cargando}
            className="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg py-3 font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {cargando
              ? '⏳ Procesando...'
              : modo === 'login'
              ? '🔐 Iniciar Sesión'
              : '✨ Crear Cuenta'}
          </button>
        </form>

        {/* Cambiar modo */}
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setModo(modo === 'login' ? 'registro' : 'login');
              setError('');
            }}
            className="text-purple-400 hover:text-purple-300 text-sm"
          >
            {modo === 'login'
              ? '¿No tienes cuenta? Regístrate'
              : '¿Ya tienes cuenta? Inicia sesión'}
          </button>
        </div>
      </div>
    </div>
  );
}