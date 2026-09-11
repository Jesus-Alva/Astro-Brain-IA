const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://10.110.164.138:8000';

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  mensaje: string;
  respuesta: string;
  usuario: string;
  personalidad: string;
  timestamp: string;
}

export interface FeedbackResponse {
  feedback_registrado: boolean;
  es_positivo: boolean;
  timestamp: string;
}

export async function enviarMensaje(
  mensaje: string,
  usuario: string = 'anonimo',
  personalidad: string = 'amigable'
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mensaje, usuario, personalidad }),
  });

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

export async function enviarFeedback(
  mensaje: string,
  respuesta: string,
  esPositivo: boolean,
  usuario: string = 'anonimo'
): Promise<FeedbackResponse> {
  const response = await fetch(`${API_URL}/feedback`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mensaje, respuesta, es_positivo: esPositivo, usuario }),
  });

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

export async function verificarBackend(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/`, { method: 'GET' });
    console.log('Verificación del backend:', API_URL, response.ok);
    return response.ok;
  } catch (error) {
    console.error('Error al verificar el backend:', error);
    return false;
  }
}

// --- Fase 2: Búsqueda y Etiquetas ---

export interface ItemConocimiento {
  documento: string;
  metadata: Record<string, any>;
  etiquetas: string[];
  importancia: number;
  similitud?: number;
}

export interface EstadisticasDetalladas {
  total_items: number;
  categorias: Record<string, number>;
  etiquetas: Record<string, number>;
  total_etiquetas_unicas: number;
  importancia_promedio: number;
  confianza_promedio: number;
}

export async function obtenerEstadisticasDetalladas(): Promise<EstadisticasDetalladas> {
  const response = await fetch(`${API_URL}/estadisticas`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function obtenerCategorias() {
  const response = await fetch(`${API_URL}/categorias`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function obtenerEtiquetas() {
  const response = await fetch(`${API_URL}/etiquetas`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function buscarPorCategoria(categoria: string) {
  const response = await fetch(`${API_URL}/buscar/categoria/${categoria}`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function buscarPorEtiqueta(etiqueta: string) {
  const response = await fetch(`${API_URL}/buscar/etiqueta/${etiqueta}`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

// --- Fase 3: Memoria Dual ---

export interface EstadisticasMemoria {
  corto_plazo: {
    sesion_id: string;
    items_actuales: number;
    capacidad: number;
    hechos: number;
    mensajes: number;
  };
  largo_plazo: {
    total_items: number;
    categorias: Record<string, number>;
    etiquetas: Record<string, number>;
    total_etiquetas_unicas: number;
    importancia_promedio: number;
    confianza_promedio: number;
  };
  consolidaciones_realizadas: number;
  ultima_consolidacion: string;
}

export interface ResumenSesion {
  sesion_id: string;
  iniciada: string;
  duracion_minutos: number;
  total_mensajes: number;
  total_hechos: number;
  categorias_detectadas: string[];
  primer_mensaje: string;
  ultimo_mensaje: string;
}

export async function obtenerEstadisticasMemoria(): Promise<EstadisticasMemoria> {
  const response = await fetch(`${API_URL}/memoria/estadisticas`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function consolidarMemoria(forzar: boolean = true) {
  const response = await fetch(`${API_URL}/memoria/consolidar?forzar=${forzar}`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function obtenerResumenSesion(): Promise<ResumenSesion> {
  const response = await fetch(`${API_URL}/memoria/resumen-sesion`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function olvidarMemoria(
  criterio: string,
  valor: string | number,
  dryRun: boolean = true
) {
  const response = await fetch(
    `${API_URL}/memoria/olvidar?criterio=${criterio}&valor=${valor}&dry_run=${dryRun}`,
    { method: 'POST' }
  );
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function obtenerMemoriaCortoPlazo() {
  const response = await fetch(`${API_URL}/memoria/corto-plazo`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

// --- Usuarios ---

export async function listarUsuarios() {
  const response = await fetch(`${API_URL}/usuarios`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function crearUsuario(nombre: string) {
  const response = await fetch(`${API_URL}/usuario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ nombre }),
  });
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}


export interface EstadisticasFeedback {
  total_feedback: number;
  positivos: number;
  negativos: number;
  tasa_aceptacion: number;
  patrones_positivos: number;
  patrones_negativos: number;
}

export async function obtenerEstadisticasFeedback(): Promise<EstadisticasFeedback> {
  const response = await fetch(`${API_URL}/feedback/estadisticas`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function obtenerHistorialFeedback(usuario?: string, limite: number = 20) {
  const params = new URLSearchParams();
  if (usuario) params.append('usuario', usuario);
  params.append('limite', limite.toString());

  const response = await fetch(`${API_URL}/feedback/historial?${params}`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function exportarConocimiento(usuario?: string) {
  const params = usuario ? `?usuario=${usuario}` : '';
  const response = await fetch(`${API_URL}/exportar/conocimiento${params}`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `astro_ia_conocimiento_${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(url);

  return true;
}

export async function importarConocimiento(archivo: File) {
  const formData = new FormData();
  formData.append('archivo', archivo);

  const response = await fetch(`${API_URL}/importar/conocimiento`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function obtenerPreferencias(usuario: string) {
  const response = await fetch(`${API_URL}/preferencias/${usuario}`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function actualizarPreferencias(
  usuario: string,
  personalidad?: string,
  temperatura?: number
) {
  const response = await fetch(`${API_URL}/preferencias`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, personalidad, temperatura }),
  });
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

// Añadir al final del archivo

// --- Fase 6: Multiusuario ---

export async function cambiarUsuario(usuario: string) {
  const response = await fetch(`${API_URL}/usuario/cambiar`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario }),
  });
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function obtenerUsuarioActual() {
  const response = await fetch(`${API_URL}/usuario/actual`);
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}

export async function verificarAislamiento(usuario1: string, usuario2: string) {
  const response = await fetch(
    `${API_URL}/usuario/aislamiento/verificar?usuario1=${usuario1}&usuario2=${usuario2}`
  );
  if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
  return await response.json();
}