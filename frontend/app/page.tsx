'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import toast from 'react-hot-toast';
import {
  enviarMensaje,
  enviarFeedback,
  verificarBackend,
  verificarSesion,
  logout,
  obtenerToken,
  listarConversaciones,
  crearConversacion,
  obtenerConversacion,
  renombrarConversacion,
  eliminarConversacion,
  ConversationSummary,
} from '@/lib/api';
import { Message } from '@/types';
import { Header } from '@/components/Header';
import { StatsDashboard } from '@/components/StatsDashboard';
import { MessageBubble } from '@/components/MessageBubble';
import { ExportImport } from '@/components/ExportImport';
import { FeedbackStats } from '@/components/FeedbackStats';
import { Login } from '@/components/Login';
import { ConfirmationAlert } from '@/components/ConfirmationAlert';

export default function Home() {
  const [autenticado, setAutenticado] = useState(false);
  const [verificando, setVerificando] = useState(true);
  const [usuario, setUsuario] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [personalidad, setPersonalidad] = useState('amigable');
  const [sidebarAbierto, setSidebarAbierto] = useState(true);
  const [feedbackRefresh, setFeedbackRefresh] = useState(0);
  const [conversaciones, setConversaciones] = useState<ConversationSummary[]>([]);
  const [conversationId, setConversationId] = useState<string>();
  const [conversacionEditando, setConversacionEditando] = useState<string>();
  const [tituloEditado, setTituloEditado] = useState('');
  const [conversacionPendienteEliminar, setConversacionPendienteEliminar] = useState<string>();
  const [eliminandoConversacion, setEliminandoConversacion] = useState(false);
  const [menuConversacionAbierto, setMenuConversacionAbierto] = useState<string>();
  const [menuConversacionPosicion, setMenuConversacionPosicion] = useState({
    top: 0,
    left: 0,
  });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const cargarConversaciones = async () => {
    try {
      const disponibles = await listarConversaciones();
      setConversaciones(disponibles);

      if (disponibles[0]) {
        const conversacion = await obtenerConversacion(disponibles[0].id);
        setConversationId(conversacion.id);
        setMessages(conversacion.mensajes);
      } else {
        const nueva = await crearConversacion();
        setConversationId(nueva.id);
        setConversaciones([nueva]);
        setMessages([]);
      }
    } catch (error) {
      console.error('Error al cargar conversaciones:', error);
      toast.error('No se pudieron cargar tus conversaciones');
    }
  };

  // Verificar sesión al cargar
  useEffect(() => {
    const verificar = async () => {
      const valido = await verificarSesion();
      const usuarioGuardado = localStorage.getItem('usuario');

      if (valido && usuarioGuardado) {
        setUsuario(usuarioGuardado);
        setAutenticado(true);
        await cargarConversaciones();
      } else {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('usuario');
      }

      setVerificando(false);
    };

    verificar();
  }, []);

  // Verificar backend
  useEffect(() => {
    if (!autenticado) return;

    const checkBackend = async () => {
      const connected = await verificarBackend();
      setIsConnected(connected);
    };
    checkBackend();
    const interval = setInterval(checkBackend, 10000);
    return () => clearInterval(interval);
  }, [autenticado]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleLoginExitoso = async (nombre: string) => {
    setUsuario(nombre);
    setVerificando(true);
    await cargarConversaciones();
    setAutenticado(true);
    setVerificando(false);
  };

  const handleLogout = () => {
    toast.success('Sesión cerrada correctamente');
    logout();
    setAutenticado(false);
    setUsuario('');
    setMessages([]);
    setConversaciones([]);
    setConversationId(undefined);
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const mensajeActual = input;
    setInput('');
    setIsLoading(true);

    try {
      const response = await enviarMensaje(mensajeActual, usuario, personalidad, conversationId);
      setConversationId(response.conversacion_id);
      setConversaciones((prev) => prev.map((conversacion) =>
        conversacion.id === response.conversacion_id
          ? { ...conversacion, total_mensajes: conversacion.total_mensajes + 2 }
          : conversacion
      ));

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.respuesta,
        timestamp: response.timestamp || new Date().toISOString(),
        feedback: null,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: '❌ Error al conectar con el backend.',
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFeedback = useCallback(
    async (messageId: string, esPositivo: boolean) => {
      const messageIndex = messages.findIndex((m) => m.id === messageId);
      if (messageIndex === -1 || messageIndex === 0) return;

      const mensajeUsuario = messages[messageIndex - 1]?.content || '';
      const respuestaIA = messages[messageIndex].content;

      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId ? { ...m, feedback: esPositivo } : m
        )
      );
      setFeedbackRefresh((prev) => prev + 1);

      try {
        await enviarFeedback(mensajeUsuario, respuestaIA, esPositivo, usuario);
      } catch (error) {
        console.error('Error al enviar feedback:', error);
        setMessages((prev) =>
          prev.map((m) =>
            m.id === messageId ? { ...m, feedback: null } : m
          )
        );
      }
    },
    [messages, usuario]
  );

  const nuevaConversacion = async () => {
    const nueva = await crearConversacion();
    setConversationId(nueva.id);
    setConversaciones((prev) => [nueva, ...prev]);
    setMessages([]);
  };

  const seleccionarConversacion = async (id: string) => {
    const conversacion = await obtenerConversacion(id);
    setConversationId(id);
    setMessages(conversacion.mensajes);
  };

  const iniciarEdicionConversacion = (conversacion: ConversationSummary) => {
    setMenuConversacionAbierto(undefined);
    setConversacionEditando(conversacion.id);
    setTituloEditado(conversacion.titulo);
  };

  const guardarNombreConversacion = async () => {
    if (!conversacionEditando || !tituloEditado.trim()) return;
    const actualizada = await renombrarConversacion(
      conversacionEditando,
      tituloEditado
    );
    setConversaciones((prev) => prev.map((conversacion) =>
      conversacion.id === actualizada.id ? actualizada : conversacion
    ));
    setConversacionEditando(undefined);
    setTituloEditado('');
  };

  const solicitarEliminarConversacion = (id: string) => {
    setMenuConversacionAbierto(undefined);
    setConversacionPendienteEliminar(id);
  };

  const borrarConversacion = async () => {
    if (!conversacionPendienteEliminar) return;
    const id = conversacionPendienteEliminar;
    setEliminandoConversacion(true);
    try {
      await eliminarConversacion(id);
      toast.success('Conversación eliminada');
      const restantes = conversaciones.filter((conversacion) => conversacion.id !== id);
      setConversaciones(restantes);
      if (id === conversationId) {
        if (restantes[0]) {
          await seleccionarConversacion(restantes[0].id);
        } else {
          await nuevaConversacion();
        }
      }
      setConversacionPendienteEliminar(undefined);
    } catch (error) {
      console.error('Error al eliminar conversación:', error);
      toast.error('No se pudo eliminar la conversación');
    } finally {
      setEliminandoConversacion(false);
    }
  };

  const exportarConversacion = () => {
    const contenido = messages
      .map((m) => `[${m.role === 'user' ? 'Tú' : 'IA'}] ${m.content}`)
      .join('\n\n');

    const blob = new Blob([contenido], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `conversacion_${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Loading inicial
  if (verificando) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900">
        <div className="text-white text-center">
          <div className="text-6xl mb-4 animate-pulse">🧠</div>
          <p className="text-gray-400">Verificando sesión...</p>
        </div>
      </div>
    );
  }

  // Sin autenticar → mostrar login
  if (!autenticado) {
    return <Login onLoginExitoso={handleLoginExitoso} />;
  }

  // Autenticado → mostrar chat
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-300">
      <div className="container mx-auto max-w-7xl px-4 py-6">
        <Header
          isConnected={isConnected}
          usuario={usuario}
          personalidad={personalidad}
          onPersonalidadChange={setPersonalidad}
          onLogout={handleLogout}
        />

        <div className="flex gap-6">
          <div className="flex shrink-0 flex-col gap-3">
            <motion.button
              onClick={() => setSidebarAbierto(!sidebarAbierto)}
              aria-label={sidebarAbierto ? 'Ocultar menú lateral' : 'Mostrar menú lateral'}
              title={sidebarAbierto ? 'Ocultar menú lateral' : 'Mostrar menú lateral'}
              className={`${sidebarAbierto ? 'w-full' : 'w-auto'} self-center rounded-full border border-purple-400/40 bg-linear-to-r from-purple-600 to-blue-600 px-5 py-2 text-sm font-semibold text-white shadow-lg shadow-purple-500/20 transition-all hover:scale-105 hover:from-purple-500 hover:to-blue-500`}
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.96 }}
              transition={{ type: 'spring', stiffness: 420, damping: 24 }}
            >
              <AnimatePresence mode="wait" initial={false}>
                <motion.span
                  key={sidebarAbierto ? 'cerrar' : 'abrir'}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -6 }}
                  transition={{ duration: 0.16 }}
                >
                  {sidebarAbierto ? '◀  Menú' : 'Menú  ▶'}
                </motion.span>
              </AnimatePresence>
            </motion.button>

            <motion.aside
              initial={false}
              animate={{
                width: sidebarAbierto ? 320 : 64,
                height: 'auto',
              }}
              transition={{ duration: 0.45, ease: 'easeInOut' }}
              className={`${sidebarAbierto ? '' : 'sidebar-compact'} overflow-hidden`}
            >
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  <span className="sidebar-title-icon" title="Acciones">🛠️</span> <span className="sidebar-label">Acciones</span>
                </h3>
                <div className="sidebar-detail space-y-2">
                  <button
                    onClick={nuevaConversacion}
                    className="w-full text-left px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm transition-colors"
                  >
                    ➕ <span className="sidebar-label">Nueva conversación</span>
                  </button>
                  <button
                    onClick={exportarConversacion}
                    disabled={messages.length === 0}
                    className="w-full text-left px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm transition-colors disabled:opacity-50"
                  >
                    📥 <span className="sidebar-label">Exportar conversación</span>
                  </button>
                </div>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  <span className="sidebar-title-icon" title="Conversaciones">💬</span> <span className="sidebar-label">Conversaciones</span>
                </h3>
                <div className="sidebar-detail space-y-2 max-h-64 overflow-y-auto">
                  {conversaciones.map((conversacion) => (
                    <div key={conversacion.id} className="relative flex items-center gap-2">
                      {conversacionEditando === conversacion.id ? (
                        <input
                          autoFocus
                          value={tituloEditado}
                          onChange={(e) => setTituloEditado(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') guardarNombreConversacion();
                            if (e.key === 'Escape') setConversacionEditando(undefined);
                          }}
                          onBlur={guardarNombreConversacion}
                          className="flex-1 min-w-0 px-3 py-2 rounded-lg text-sm bg-gray-100 dark:bg-gray-700 border border-purple-500 outline-none"
                        />
                      ) : (
                        <button
                          onClick={() => seleccionarConversacion(conversacion.id)}
                          className={`flex-1 text-left px-3 py-2 rounded-lg text-sm truncate ${conversationId === conversacion.id ? 'bg-purple-100 dark:bg-purple-900/40' : 'bg-gray-100 dark:bg-gray-700'}`}
                        >
                          {conversacion.titulo}
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={(event) => {
                          const rect = event.currentTarget.getBoundingClientRect();
                          setMenuConversacionPosicion({
                            top: rect.bottom + 4,
                            left: Math.max(8, rect.right - 160),
                          });
                          setMenuConversacionAbierto((actual) =>
                            actual === conversacion.id ? undefined : conversacion.id
                          );
                        }}
                        className="rounded-lg px-2 py-2 text-lg leading-none text-gray-500 transition-colors hover:bg-gray-200 hover:text-gray-900 dark:hover:bg-gray-600 dark:hover:text-white"
                        title="Opciones de conversación"
                        aria-label={`Opciones de ${conversacion.titulo}`}
                        aria-expanded={menuConversacionAbierto === conversacion.id}
                      >
                        ⋮
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <StatsDashboard />

              <ExportImport usuario={usuario} />

              <FeedbackStats key={feedbackRefresh} />
            </div>
            </motion.aside>

            {menuConversacionAbierto && (
              <div
                className="fixed z-50 min-w-40 overflow-hidden rounded-lg border border-gray-200 bg-white py-1 shadow-2xl dark:border-gray-700 dark:bg-gray-800"
                style={{
                  top: menuConversacionPosicion.top,
                  left: menuConversacionPosicion.left,
                }}
              >
                <button
                  type="button"
                  onClick={() => {
                    const conversacion = conversaciones.find(
                      (item) => item.id === menuConversacionAbierto
                    );
                    if (conversacion) iniciarEdicionConversacion(conversacion);
                  }}
                  className="block w-full px-3 py-2 text-left text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-200 dark:hover:bg-gray-700"
                >
                  ✏️ Cambiar nombre
                </button>
                <button
                  type="button"
                  onClick={() => solicitarEliminarConversacion(menuConversacionAbierto)}
                  className="block w-full px-3 py-2 text-left text-sm text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                >
                  🗑️ Eliminar chat
                </button>
              </div>
            )}

          </div>

          <main className="flex-1">
            <div className="bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 shadow-sm">
              <div className="h-[calc(100vh-250px)] overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-full text-gray-400 dark:text-gray-500">
                    <div className="text-6xl mb-4">🧠</div>
                    <p className="text-lg font-semibold text-gray-700 dark:text-gray-300">
                      ¡Hola {usuario}!
                    </p>
                    <p className="text-sm mt-2">
                      {isConnected
                        ? 'Envía un mensaje para comenzar'
                        : 'Conectando al backend...'}
                    </p>
                  </div>
                )}

                {messages.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    message={msg}
                    onFeedback={
                      msg.role === 'assistant'
                        ? (esPositivo) => handleFeedback(msg.id, esPositivo)
                        : undefined
                    }
                  />
                ))}

                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-700 rounded-2xl rounded-bl-sm px-4 py-3">
                      <span className="inline-flex gap-1 text-gray-600 dark:text-gray-400">
                        <span className="animate-bounce">●</span>
                        <span className="animate-bounce delay-100">●</span>
                        <span className="animate-bounce delay-200">●</span>
                      </span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              <form
                onSubmit={handleSubmit}
                className="p-4 border-t border-gray-200 dark:border-gray-700"
              >
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={
                      isConnected
                        ? 'Escribe tu mensaje...'
                        : 'Backend desconectado...'
                    }
                    disabled={isLoading || !isConnected}
                    className="flex-1 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg px-4 py-3 border border-gray-300 dark:border-gray-600 focus:outline-none focus:border-purple-500 disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !input.trim() || !isConnected}
                    className="px-6 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                  >
                    {isLoading ? '⏳' : '📤 Enviar'}
                  </button>
                </div>
              </form>
            </div>
          </main>
        </div>
      </div>
      <ConfirmationAlert
        open={Boolean(conversacionPendienteEliminar)}
        title="Eliminar conversación"
        message="Esta conversación se eliminará permanentemente. Esta acción no se puede deshacer."
        confirmLabel="Eliminar"
        onConfirm={borrarConversacion}
        onCancel={() => setConversacionPendienteEliminar(undefined)}
        loading={eliminandoConversacion}
      />
    </div>
  );
}