'use client';

import { useState } from 'react';

interface PoliticasPrivacidadProps {
  abierto: boolean;
  onCerrar: () => void;
  onAceptar?: () => void;
  modoLectura?: boolean; // Si es solo lectura (desde menú de config)
}

export function PoliticasPrivacidad({
  abierto,
  onCerrar,
  onAceptar,
  modoLectura = false,
}: PoliticasPrivacidadProps) {
  const [seccionActiva, setSeccionActiva] = useState<string>('intro');

  if (!abierto) return null;

  const secciones = [
    { id: 'intro', titulo: '1. Introducción', icono: '📖' },
    { id: 'responsable', titulo: '2. Responsable', icono: '👤' },
    { id: 'datos', titulo: '3. Datos Recopilados', icono: '📊' },
    { id: 'finalidad', titulo: '4. Finalidad', icono: '🎯' },
    { id: 'ia', titulo: '6. Uso de IA', icono: '🤖' },
    { id: 'seguridad', titulo: '7. Seguridad', icono: '🔒' },
    { id: 'terceros', titulo: '8. Terceros', icono: '🤝' },
    { id: 'derechos', titulo: '10. Tus Derechos', icono: '⚖️' },
    { id: 'resumen', titulo: 'Resumen Rápido', icono: '📋' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className="text-3xl">🔒</div>
            <div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                Política de Privacidad
              </h2>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Versión 1.0.0 · Última actualización: 14 de septiembre de 2026
              </p>
            </div>
          </div>
          <button
            onClick={onCerrar}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
            aria-label="Cerrar"
          >
            <span className="text-gray-500 dark:text-gray-400 text-2xl">×</span>
          </button>
        </div>

        {/* Contenido */}
        <div className="flex-1 flex overflow-hidden">
          {/* Sidebar de secciones */}
          <aside className="w-64 border-r border-gray-200 dark:border-gray-700 overflow-y-auto p-4 hidden md:block">
            <nav className="space-y-1">
              {secciones.map((sec) => (
                <button
                  key={sec.id}
                  onClick={() => setSeccionActiva(sec.id)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                    seccionActiva === sec.id
                      ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 font-medium'
                      : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}
                >
                  <span>{sec.icono}</span>
                  <span className="truncate">{sec.titulo}</span>
                </button>
              ))}
            </nav>
          </aside>

          {/* Contenido de la sección */}
          <div className="flex-1 overflow-y-auto p-6">
            <ContenidoSeccion seccion={seccionActiva} />
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
          {modoLectura ? (
            <div className="flex justify-end">
              <button
                onClick={onCerrar}
                className="px-6 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
              >
                Cerrar
              </button>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Al hacer clic en "Aceptar", confirmas que has leído y aceptas esta política.
              </div>
              <div className="flex gap-3">
                <button
                  onClick={onCerrar}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg font-medium hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  onClick={() => {
                    if (onAceptar) onAceptar();
                    onCerrar();
                  }}
                  className="px-6 py-2 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg font-medium hover:opacity-90 transition-opacity"
                >
                  ✅ Aceptar y Continuar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================
//  CONTENIDO DE CADA SECCIÓN
// ============================================

function ContenidoSeccion({ seccion }: { seccion: string }) {
  const clases = {
    h3: 'text-lg font-bold text-gray-900 dark:text-white mt-6 mb-3 first:mt-0',
    h4: 'text-md font-semibold text-gray-800 dark:text-gray-200 mt-4 mb-2',
    p: 'text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-3',
    ul: 'text-sm text-gray-700 dark:text-gray-300 space-y-1 mb-3 ml-4',
    tabla: 'w-full text-sm border-collapse mb-4',
    th: 'bg-gray-100 dark:bg-gray-800 px-3 py-2 text-left text-xs font-semibold text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700',
    td: 'px-3 py-2 text-xs text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700',
    caja: 'bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-4',
    cajaRoja: 'bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-900/20 dark:to-orange-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4',
    cajaAzul: 'bg-gradient-to-r from-blue-50 to-cyan-50 dark:from-blue-900/20 dark:to-cyan-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-4',
  };

  switch (seccion) {
    case 'intro':
      return (
        <div>
          <h3 className={clases.h3}>1. Introducción</h3>
          <p className={clases.p}>
            Bienvenido a <strong>Astro-IA</strong>. Esta Política de Privacidad describe cómo
            recopilamos, usamos, almacenamos y protegemos tu información personal.
          </p>

          <div className={clases.caja}>
            <h4 className="text-md font-semibold text-green-900 dark:text-green-300 mb-2">
              ✅ Nuestro Compromiso
            </h4>
            <ul className="text-sm text-green-800 dark:text-green-400 space-y-1 ml-4">
              <li>• <strong>Transparencia total</strong> sobre qué datos recopilamos</li>
              <li>• <strong>Control absoluto</strong> del usuario sobre su información</li>
              <li>• <strong>Almacenamiento local</strong> — Tus datos permanecen en TU servidor</li>
              <li>• <strong>Sin venta de datos</strong> a terceros bajo ninguna circunstancia</li>
              <li>• <strong>Código abierto</strong> — Puedes auditar cómo manejamos tus datos</li>
            </ul>
          </div>

          <p className={clases.p}>
            Al registrarte y usar Astro-IA, aceptas las prácticas descritas en esta política.
          </p>
        </div>
      );

    case 'responsable':
      return (
        <div>
          <h3 className={clases.h3}>2. Responsable del Tratamiento</h3>
          <p className={clases.p}>
            El responsable del tratamiento de tus datos es el propietario/administrador
            de la instancia de Astro-IA que estés utilizando.
          </p>
          <div className={clases.cajaAzul}>
            <p className="text-sm text-blue-900 dark:text-blue-300">
              <strong>ℹ️ Nota:</strong> Astro-IA es un proyecto de código abierto. Si estás
              usando una instancia alojada por un tercero, ese tercero es responsable de tus datos.
            </p>
          </div>
        </div>
      );

    case 'datos':
      return (
        <div>
          <h3 className={clases.h3}>3. Datos que Recopilamos</h3>
          
          <h4 className={clases.h4}>3.1 Datos de Registro</h4>
          <table className={clases.tabla}>
            <thead>
              <tr>
                <th className={clases.th}>Dato</th>
                <th className={clases.th}>Obligatorio</th>
                <th className={clases.th}>Finalidad</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className={clases.td}>Nombre de usuario</td>
                <td className={clases.td}>✅ Sí</td>
                <td className={clases.td}>Identificación</td>
              </tr>
              <tr>
                <td className={clases.td}>Email</td>
                <td className={clases.td}>✅ Sí</td>
                <td className={clases.td}>Autenticación</td>
              </tr>
              <tr>
                <td className={clases.td}>Contraseña</td>
                <td className={clases.td}>✅ Sí</td>
                <td className={clases.td}>Seguridad (bcrypt)</td>
              </tr>
            </tbody>
          </table>

          <h4 className={clases.h4}>3.2 Datos que NO Recopilamos</h4>
          <div className={clases.cajaRoja}>
            <ul className="text-sm text-red-800 dark:text-red-400 space-y-1 ml-4">
              <li>❌ Datos biométricos</li>
              <li>❌ Datos de geolocalización precisa</li>
              <li>❌ Información financiera</li>
              <li>❌ Datos de salud</li>
              <li>❌ Contactos del teléfono</li>
              <li>❌ Fotos o archivos personales</li>
            </ul>
          </div>
        </div>
      );

    case 'finalidad':
      return (
        <div>
          <h3 className={clases.h3}>4. Finalidad del Tratamiento</h3>
          <p className={clases.p}>Utilizamos tus datos <strong>exclusivamente</strong> para:</p>

          <div className={clases.caja}>
            <h4 className="text-md font-semibold text-green-900 dark:text-green-300 mb-2">
              ✅ Lo que SÍ hacemos
            </h4>
            <ul className="text-sm text-green-800 dark:text-green-400 space-y-1 ml-4">
              <li>• Autenticarte de forma segura</li>
              <li>• Guardar tus conversaciones</li>
              <li>• Recordar tu conocimiento personal</li>
              <li>• Personalizar las respuestas de la IA</li>
              <li>• Mantener el aislamiento entre usuarios</li>
            </ul>
          </div>

          <div className={clases.cajaRoja}>
            <h4 className="text-md font-semibold text-red-900 dark:text-red-300 mb-2">
              ❌ Lo que NUNCA hacemos
            </h4>
            <ul className="text-sm text-red-800 dark:text-red-400 space-y-1 ml-4">
              <li>• Vender tu información a terceros</li>
              <li>• Usar tus conversaciones para entrenar modelos públicos</li>
              <li>• Compartir tus datos con anunciantes</li>
              <li>• Enviarte spam o publicidad</li>
              <li>• Perfilar tu comportamiento comercialmente</li>
            </ul>
          </div>
        </div>
      );

    case 'ia':
      return (
        <div>
          <h3 className={clases.h3}>6. Uso de Inteligencia Artificial</h3>
          
          <h4 className={clases.h4}>6.1 Modelos Utilizados</h4>
          <p className={clases.p}>
            Astro-IA utiliza modelos de lenguaje de código abierto que se ejecutan
            <strong> localmente</strong> en tu servidor mediante <strong>Ollama</strong>.
          </p>

          <div className={clases.cajaAzul}>
            <h4 className="text-md font-semibold text-blue-900 dark:text-blue-300 mb-2">
              🔒 Tu privacidad está protegida
            </h4>
            <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1 ml-4">
              <li>❌ <strong>NO</strong> enviamos tus datos a OpenAI</li>
              <li>❌ <strong>NO</strong> enviamos tus datos a Google</li>
              <li>❌ <strong>NO</strong> enviamos tus datos a Anthropic</li>
              <li>✅ <strong>TODO</strong> se procesa localmente en tu servidor</li>
            </ul>
          </div>

          <h4 className={clases.h4}>6.2 Limitaciones de la IA</h4>
          <div className={clases.cajaRoja}>
            <ul className="text-sm text-red-800 dark:text-red-400 space-y-1 ml-4">
              <li>⚠️ Las respuestas pueden contener errores</li>
              <li>⚠️ No es sustituto de asesoramiento profesional</li>
              <li>⚠️ No compartas información altamente sensible</li>
              <li>⚠️ La IA puede alucinar (inventar información)</li>
            </ul>
          </div>
        </div>
      );

    case 'seguridad':
      return (
        <div>
          <h3 className={clases.h3}>7. Almacenamiento y Seguridad</h3>

          <h4 className={clases.h4}>7.1 Dónde se Almacenan tus Datos</h4>
          <table className={clases.tabla}>
            <thead>
              <tr>
                <th className={clases.th}>Componente</th>
                <th className={clases.th}>Ubicación</th>
                <th className={clases.th}>Cifrado</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className={clases.td}>Conversaciones</td>
                <td className={clases.td}>Tu servidor</td>
                <td className={clases.td}>Según configuración</td>
              </tr>
              <tr>
                <td className={clases.td}>Contraseñas</td>
                <td className={clases.td}>Tu servidor</td>
                <td className={clases.td}>✅ bcrypt</td>
              </tr>
              <tr>
                <td className={clases.td}>Tokens JWT</td>
                <td className={clases.td}>Tu navegador</td>
                <td className={clases.td}>✅ Firmados</td>
              </tr>
            </tbody>
          </table>

          <h4 className={clases.h4}>7.2 Medidas de Seguridad</h4>
          <ul className={clases.ul}>
            <li>• 🔐 <strong>Hash bcrypt</strong> para contraseñas</li>
            <li>• 🎫 <strong>Tokens JWT</strong> firmados con HS256</li>
            <li>• 🛡️ <strong>Aislamiento total</strong> entre usuarios</li>
            <li>• 🔒 <strong>HTTPS</strong> recomendado en producción</li>
            <li>• 🚫 <strong>Sin acceso</strong> a datos de otros usuarios</li>
          </ul>
        </div>
      );

    case 'terceros':
      return (
        <div>
          <h3 className={clases.h3}>8. Compartición con Terceros</h3>
          
          <div className={clases.caja}>
            <h4 className="text-md font-semibold text-green-900 dark:text-green-300 mb-2">
              ✅ Principio General
            </h4>
            <p className="text-sm text-green-800 dark:text-green-400">
              <strong>NO compartimos tus datos con terceros</strong>, salvo en las
              integraciones opcionales que tú decidas activar.
            </p>
          </div>

          <h4 className={clases.h4}>8.1 Integraciones Opcionales</h4>
          <table className={clases.tabla}>
            <thead>
              <tr>
                <th className={clases.th}>Servicio</th>
                <th className={clases.th}>Datos Compartidos</th>
                <th className={clases.th}>Cuándo</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td className={clases.td}>Telegram</td>
                <td className={clases.td}>Mensajes</td>
                <td className={clases.td}>Solo si lo activas</td>
              </tr>
              <tr>
                <td className={clases.td}>WhatsApp (Twilio)</td>
                <td className={clases.td}>Mensajes, teléfono</td>
                <td className={clases.td}>Solo si lo activas</td>
              </tr>
            </tbody>
          </table>

          <div className={clases.cajaAzul}>
            <p className="text-sm text-blue-900 dark:text-blue-300">
              <strong>ℹ️ Importante:</strong> Estas integraciones son completamente opcionales.
              Si no las usas, no se comparte nada.
            </p>
          </div>
        </div>
      );

    case 'derechos':
      return (
        <div>
          <h3 className={clases.h3}>10. Tus Derechos</h3>
          <p className={clases.p}>Tienes derecho a:</p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
            <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg p-3">
              <h4 className="font-semibold text-purple-900 dark:text-purple-300 text-sm mb-1">
                🔍 Acceso
              </h4>
              <p className="text-xs text-purple-800 dark:text-purple-400">
                Ver todos tus datos almacenados
              </p>
            </div>
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
              <h4 className="font-semibold text-blue-900 dark:text-blue-300 text-sm mb-1">
                ✏️ Rectificación
              </h4>
              <p className="text-xs text-blue-800 dark:text-blue-400">
                Corregir información incorrecta
              </p>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <h4 className="font-semibold text-red-900 dark:text-red-300 text-sm mb-1">
                🗑️ Supresión
              </h4>
              <p className="text-xs text-red-800 dark:text-red-400">
                Eliminar tus conversaciones o cuenta
              </p>
            </div>
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
              <h4 className="font-semibold text-green-900 dark:text-green-300 text-sm mb-1">
                📦 Portabilidad
              </h4>
              <p className="text-xs text-green-800 dark:text-green-400">
                Exportar tus datos en JSON
              </p>
            </div>
          </div>

          <h4 className={clases.h4}>Cómo Ejercer tus Derechos</h4>
          <p className={clases.p}>
            Todos estos derechos se pueden ejercer desde la propia aplicación:
          </p>
          <ul className={clases.ul}>
            <li>• Configuración → Eliminar conversaciones</li>
            <li>• Configuración → Exportar datos</li>
            <li>• Configuración → Eliminar cuenta</li>
          </ul>
        </div>
      );

    case 'resumen':
      return (
        <div>
          <h3 className={clases.h3}>📋 Resumen Rápido</h3>
          <p className={clases.p}>
            Si solo tienes 30 segundos, aquí está lo más importante:
          </p>

          <div className="space-y-2">
            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">❌</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Venden mis datos?
                </div>
                <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                  NUNCA
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">❌</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Se envían a OpenAI/Google?
                </div>
                <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                  NUNCA
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">✅</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Se almacenan localmente?
                </div>
                <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                  SÍ, en tu servidor
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">❌</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Otros usuarios pueden ver mis datos?
                </div>
                <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                  NO, aislamiento total
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">✅</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Puedo eliminar mis datos?
                </div>
                <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                  SÍ, en cualquier momento
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">✅</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Puedo exportar mis datos?
                </div>
                <div className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                  SÍ, en formato JSON
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">❌</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Usan cookies de terceros?
                </div>
                <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                  NO
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl">❌</span>
              <div>
                <div className="font-semibold text-gray-900 dark:text-white text-sm">
                  ¿Se usan para entrenar modelos?
                </div>
                <div className="text-xs text-green-600 dark:text-green-400 font-medium">
                  NO
                </div>
              </div>
            </div>
          </div>
        </div>
      );

    default:
      return null;
  }
}