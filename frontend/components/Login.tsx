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
      <div
        className="relative flex min-h-screen items-center justify-center overflow-hidden bg-linear-to-br from-slate-950 via-violet-950/40 to-slate-950 px-4 py-8"
        style={{
          backgroundImage: "url('/images/Astro Code Difuminado.jpeg')",
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundAttachment: 'fixed',
        }}
      >
        <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(168,85,247,0.22),transparent_30%),radial-gradient(circle_at_bottom,_rgba(59,130,246,0.18),transparent_35%)]" />
        <div className="relative w-full max-w-md">
          <div className="rounded-3xl border border-violet-400/40 bg-white/5 p-6 shadow-[0_0_0_1px_rgba(167,139,250,0.18),0_0_25px_rgba(168,85,247,0.3),0_20px_80px_rgba(15,23,42,0.75)] backdrop-blur-xl sm:p-8">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="mx-auto mb-4 flex h-32 w-32 items-center justify-center overflow-hidden rounded-full border border-white/20 bg-linear-to-br from-violet-500/80 to-cyan-500/80 shadow-[0_0_30px_rgba(168,85,247,0.45)] backdrop-blur-md">
                <img
                  src="/images/Astro_Code_Icon.png"
                  alt="Astro Code Icon"
                  className="h-28 w-28 object-contain"
                />
              </div>
              <h1 className="text-3xl font-bold text-white drop-shadow-sm">Astro-IA</h1>
              <p className="mt-2 text-sm text-slate-300">
                {modo === 'login' ? 'Inicia sesión para continuar' : 'Crea tu cuenta gratis'}
              </p>
            </div>

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="space-y-4 ">
              {modo === 'login' ? (
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200">
                    Usuario o Email
                  </label>
                  <input
                    type="text"
                    value={identificador}
                    onChange={(e) => setIdentificador(e.target.value)}
                    placeholder="jesus o jesus@example.com"
                    required
                    autoComplete="username"
                    className="w-full rounded-xl border border-white/10 bg-slate-900/40 px-4 py-3 text-white placeholder:text-slate-400 shadow-inner shadow-slate-950/40 transition-all focus:border-violet-400/80 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
                  />
                  <p className="mt-1 text-xs text-slate-400">
                    Puedes usar tu nombre de usuario o tu email
                  </p>
                </div>
              ) : (
                <>
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-200">
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
                      className="w-full rounded-xl border border-white/10 bg-slate-900/40 px-4 py-3 text-white placeholder:text-slate-400 shadow-inner shadow-slate-950/40 transition-all focus:border-violet-400/80 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
                    />
                  </div>

                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-200">
                      Email
                    </label>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="jesus@example.com"
                      required
                      autoComplete="email"
                      className="w-full rounded-xl border border-white/10 bg-slate-900/40 px-4 py-3 text-white placeholder:text-slate-400 shadow-inner shadow-slate-950/40 transition-all focus:border-violet-400/80 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
                    />
                  </div>
                </>
              )}

              <div>
                <label className="mb-2 block text-sm font-medium text-slate-200">
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
                  className="w-full rounded-xl border border-white/10 bg-slate-900/40 px-4 py-3 text-white placeholder:text-slate-400 shadow-inner shadow-slate-950/40 transition-all focus:border-violet-400/80 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
                />
              </div>

              {modo === 'registro' && (
                <div>
                  <label className="mb-2 block text-sm font-medium text-slate-200">
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
                    className="w-full rounded-xl border border-white/10 bg-slate-900/40 px-4 py-3 text-white placeholder:text-slate-400 shadow-inner shadow-slate-950/40 transition-all focus:border-violet-400/80 focus:outline-none focus:ring-2 focus:ring-violet-500/30"
                  />
                </div>
              )}

              {/* ✅ CHECKBOX DE ACEPTACIÓN DE POLÍTICAS */}
              {modo === 'registro' && (
                <div className="rounded-2xl border border-white/10 bg-slate-900/30 p-4 shadow-inner shadow-slate-950/20">
                  <label className="flex cursor-pointer items-start gap-3">
                    <input
                      type="checkbox"
                      checked={aceptaPoliticas}
                      onChange={(e) => setAceptaPoliticas(e.target.checked)}
                      className="mt-1 h-4 w-4 rounded border-slate-600 bg-slate-900 text-violet-500 focus:ring-violet-500 focus:ring-offset-slate-900"
                    />
                    <span className="text-sm leading-relaxed text-slate-200">
                      He leído y acepto la{' '}
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setMostrarPoliticas(true);
                        }}
                        className="font-medium text-violet-300 underline decoration-violet-400/60 underline-offset-2 hover:text-violet-200"
                      >
                        Política de Privacidad
                      </button>
                      {' '}y el tratamiento de mis datos personales.
                    </span>
                  </label>

                  <div className="mt-3 space-y-1 border-t border-white/10 pt-3 text-xs text-slate-400">
                    <p>✅ Tus datos se almacenan localmente</p>
                    <p>✅ NO vendemos tu información a terceros</p>
                    <p>✅ Puedes eliminar tus datos cuando quieras</p>
                  </div>
                </div>
              )}

              {error && (
                <div className="rounded-xl border border-red-500/40 bg-red-500/10 p-3 shadow-inner shadow-red-950/30">
                  <p className="text-sm text-red-300">❌ {error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={cargando || (modo === 'registro' && !aceptaPoliticas)}
                className="w-full rounded-xl bg-gradient-to-r from-violet-500 to-cyan-500 py-3 font-medium text-white shadow-[0_12px_30px_rgba(168,85,247,0.35)] transition-all hover:opacity-90 hover:shadow-[0_16px_32px_rgba(45,212,191,0.35)] disabled:cursor-not-allowed disabled:opacity-50"
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
                className="text-sm text-violet-300 transition-colors hover:text-violet-200"
              >
                {modo === 'login'
                  ? '¿No tienes cuenta? Regístrate gratis'
                  : '¿Ya tienes cuenta? Inicia sesión'}
              </button>
            </div>

            {/* Footer con enlaces */}
            <div className="mt-8 space-y-2 text-center">
              <button
                onClick={() => setMostrarPoliticas(true)}
                className="text-xs text-slate-400 transition-colors hover:text-slate-300"
              >
                🔒 Ver Política de Privacidad
              </button>
              <p className="text-xs text-slate-500">
                Tus datos están seguros y encriptados
              </p>
            </div>
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