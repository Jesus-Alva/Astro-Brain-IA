// ============================================
//  TIPOS DEL PROYECTO ASTRO-IA
// ============================================

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  feedback?: boolean | null;
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

export interface Usuario {
  nombre: string;
  id: string;
  creado: string;
}

export type Personalidad = 'amigable' | 'profesional' | 'creativo' | 'sarcastico';

export type Tema = 'claro' | 'oscuro';
