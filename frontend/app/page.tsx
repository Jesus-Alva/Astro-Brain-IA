'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import {
  enviarMensaje,
  enviarFeedback,
  verificarBackend,
  verificarSesion,
  logout,
  obtenerToken,
} from '@/lib/api';
import { Message } from '@/types';
import { Header } from '@/components/Header';
import { StatsDashboard } from '@/components/StatsDashboard';
import { MessageBubble } from '@/components/MessageBubble';
import { ExportImport } from '@/components/ExportImport';
import { FeedbackStats } from '@/components/FeedbackStats';
import { Login } from '@/components/Login';

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
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Verificar sesión al cargar
  useEffect(() => {
    const verificar = async () => {
      const valido = await verificarSesion();
      const usuarioGuardado = localStorage.getItem('usuario');

      if (valido && usuarioGuardado) {
        setUsuario(usuarioGuardado);
        setAutenticado(true);
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

  const handleLoginExitoso = (nombre: string) => {
    setUsuario(nombre);
    setAutenticado(true);
  };

  const handleLogout = () => {
    logout();
    setAutenticado(false);
    setUsuario('');
    setMessages([]);
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
      const response = await enviarMensaje(mensajeActual, usuario, personalidad);

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

  const limpiarConversacion = () => {
    if (confirm('¿Estás seguro de que quieres limpiar la conversación?')) {
      setMessages([]);
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
          <aside
            className={`${sidebarAbierto ? 'w-80' : 'w-0'
              } transition-all duration-300 overflow-hidden`}
          >
            <div className="space-y-4">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
                <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  🛠️ Acciones
                </h3>
                <div className="space-y-2">
                  <button
                    onClick={limpiarConversacion}
                    className="w-full text-left px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm transition-colors"
                  >
                    🗑️ Limpiar conversación
                  </button>
                  <button
                    onClick={exportarConversacion}
                    disabled={messages.length === 0}
                    className="w-full text-left px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm transition-colors disabled:opacity-50"
                  >
                    📥 Exportar conversación
                  </button>
                </div>
              </div>

              <StatsDashboard />

              <ExportImport usuario={usuario} />

              <FeedbackStats key={feedbackRefresh} />
            </div>
          </aside>

          <button
            onClick={() => setSidebarAbierto(!sidebarAbierto)}
            className="self-start p-2 bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors border border-gray-200 dark:border-gray-700"
          >
            {sidebarAbierto ? '◀' : '▶'}
          </button>

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
    </div>
  );
}