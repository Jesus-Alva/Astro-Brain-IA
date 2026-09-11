'use client';

import { useState, useEffect } from 'react';
import { Tema } from '@/types';

export function useTheme() {
  const [tema, setTema] = useState<Tema>('oscuro');
  const [montado, setMontado] = useState(false);

  // Inicializar el tema desde localStorage
  useEffect(() => {
    const temaGuardado = localStorage.getItem('tema') as Tema;
    const temaInicial = temaGuardado || 'oscuro';
    
    setTema(temaInicial);
    aplicarTema(temaInicial);
    setMontado(true);
  }, []);

  const aplicarTema = (nuevoTema: Tema) => {
    const root = document.documentElement;
    if (nuevoTema === 'oscuro') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  };

  const toggleTema = () => {
    const nuevoTema: Tema = tema === 'oscuro' ? 'claro' : 'oscuro';
    setTema(nuevoTema);
    localStorage.setItem('tema', nuevoTema);
    aplicarTema(nuevoTema);
  };

  return { tema, toggleTema, montado };
}