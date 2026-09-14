'use client';

import { useState } from 'react';
import { login, registrar } from '@/lib/api';
import { PoliticasPrivacidad } from './PoliticasPrivacidad';

interface LoginProps {
  onLoginExitoso: (nombre: string) => void;
}

export function Login({ onLoginExitoso }: LoginProps) {
  const [modo, setModo] = useState<'login' | 'registro'>('login');
  const [identificador, setIdentificador] = useState('');
  const [nombre, setNombre] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmarPassword, setConfirmarPassword] = useState('');
  const [aceptaPoliticas, setAceptaPoliticas] = useState(false);
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);
  const [mostrarPoliticas, setMostrarPoliticas] = useState(false);

  const validarEmail = (email: string): boolean => {
    const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return regex.test(email);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setCargando(true);

    try {
      if (modo === 'registro') {
        if (nombre.length < 3) {
          throw new Error('El nombre debe tener al menos 3 caracteres');
        }
        if (!validarEmail(email)) {
          throw new Error('El email no es válido');
        }
        if (password.length < 6) {
          throw new Error('La contraseña debe tener al menos 6 caracteres');
        }
        if (password !== confirmarPassword) {
          throw new Error('Las contraseñas no coinciden');
        }
        // ✅ VALIDAR ACEPTACIÓN DE POLÍTICAS
        if (!aceptaPoliticas) {
          throw new Error('Debes aceptar las políticas de privacidad para continuar');
        }
        
        const data = await registrar(nombre, email, password, aceptaPoliticas);
        onLoginExitoso(data.nombre);
      } else {
        if (!identificador) {
          throw new Error('Ingresa tu usuario o email');
        }
        if (!password) {
          throw new Error('Ingresa tu contraseña');
        }
        
        const data = await login(identificador, password);
        onLoginExitoso(data.nombre);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setCargando(false);
    }
  };

  const cambiarModo = () => {
    setModo(modo === 'login' ? 'registro' : 'login');
    setError('');
    setIdentificador('');
    setNombre('');
    setEmail('');
    setPassword('');
    setConfirmarPassword('');
    setAceptaPoliticas(false);
  };

  return (
    <>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900/20 to-gray-900 py-8">
        <div className="w-full max-w-md px-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-4xl mx-auto mb-4 shadow-lg">
              🧠
            </div>
            <h1 className="text-3xl font-bold text-white">Astro-IA</h1>
            <p className="text-gray-400 mt-2">
              {modo === 'login' ? 'Inicia sesión para continuar' : 'Crea tu cuenta gratis'}
            </p>
          </div>

          {/* Formulario */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {modo === 'login' ? (
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Usuario o Email
                </label>
                <input
                  type="text"
                  value={identificador}
                  onChange={(e) => setIdentificador(e.target.value)}
                  placeholder="jesus o jesus@example.com"
                  required
                  autoComplete="username"
                  className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Puedes usar tu nombre de usuario o tu email
                </p>
              </div>
            ) : (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Nombre de usuario
                  </label>
                  <input
                    type="text"
                    value={nombre}
                    onChange={(e) => setNombre(e.target.value)}
                    placeholder="jesus"
                    required
                    minLength={3}
                    autoComplete="username"
                    className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="jesus@example.com"
                    required
                    autoComplete="email"
                    className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors"
                  />
                </div>
              </>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Contraseña
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mínimo 6 caracteres"
                required
                minLength={6}
                autoComplete={modo === 'login' ? 'current-password' : 'new-password'}
                className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors"
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
                  autoComplete="new-password"
                  className="w-full bg-gray-800 text-white rounded-lg px-4 py-3 border border-gray-700 focus:outline-none focus:border-purple-500 transition-colors"
                />
              </div>
            )}

            {/* ✅ CHECKBOX DE ACEPTACIÓN DE POLÍTICAS */}
            {modo === 'registro' && (
              <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4">
                <label className="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={aceptaPoliticas}
                    onChange={(e) => setAceptaPoliticas(e.target.checked)}
                    className="mt-1 w-4 h-4 rounded border-gray-600 text-purple-500 focus:ring-purple-500 focus:ring-offset-gray-800"
                  />
                  <span className="text-sm text-gray-300 leading-relaxed">
                    He leído y acepto la{' '}
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setMostrarPoliticas(true);
                      }}
                      className="text-purple-400 hover:text-purple-300 underline font-medium"
                    >
                      Política de Privacidad
                    </button>
                    {' '}y el tratamiento de mis datos personales.
                  </span>
                </label>

                <div className="mt-3 pt-3 border-t border-gray-700 text-xs text-gray-500 space-y-1">
                  <p>✅ Tus datos se almacenan localmente</p>
                  <p>✅ NO vendemos tu información a terceros</p>
                  <p>✅ Puedes eliminar tus datos cuando quieras</p>
                </div>
              </div>
            )}

            {error && (
              <div className="bg-red-900/30 border border-red-700 rounded-lg p-3 animate-fade-in">
                <p className="text-red-400 text-sm">❌ {error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={cargando || (modo === 'registro' && !aceptaPoliticas)}
              className="w-full bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg py-3 font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
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
              onClick={cambiarModo}
              className="text-purple-400 hover:text-purple-300 text-sm transition-colors"
            >
              {modo === 'login'
                ? '¿No tienes cuenta? Regístrate gratis'
                : '¿Ya tienes cuenta? Inicia sesión'}
            </button>
          </div>

          {/* Footer con enlaces */}
          <div className="mt-8 text-center space-y-2">
            <button
              onClick={() => setMostrarPoliticas(true)}
              className="text-xs text-gray-500 hover:text-gray-400 transition-colors"
            >
              🔒 Ver Política de Privacidad
            </button>
            <p className="text-xs text-gray-600">
              Tus datos están seguros y encriptados
            </p>
          </div>
        </div>
      </div>

      {/* Modal de Políticas */}
      <PoliticasPrivacidad
        abierto={mostrarPoliticas}
        onCerrar={() => setMostrarPoliticas(false)}
        onAceptar={() => {
          setAceptaPoliticas(true);
          setMostrarPoliticas(false);
        }}
      />
    </>
  );
}