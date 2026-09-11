'use client';

import { useState, useEffect } from 'react';
import { listarUsuarios, crearUsuario } from '@/lib/api';
import { Usuario } from '@/types';

interface UserSelectorProps {
  usuarioActual: string;
  onUsuarioChange: (usuario: string) => void;
}

export function UserSelector({ usuarioActual, onUsuarioChange }: UserSelectorProps) {
  const [usuarios, setUsuarios] = useState<Usuario[]>([]);
  const [mostrarCrear, setMostrarCrear] = useState(false);
  const [nuevoNombre, setNuevoNombre] = useState('');

  const cargarUsuarios = async () => {
    try {
      const data = await listarUsuarios();
      setUsuarios(data.usuarios || []);
    } catch (error) {
      console.error('Error cargando usuarios:', error);
    }
  };

  useEffect(() => {
    cargarUsuarios();
  }, []);

  const handleCrear = async () => {
    if (!nuevoNombre.trim()) return;
    try {
      await crearUsuario(nuevoNombre.trim());
      const nombre = nuevoNombre.trim();
      setNuevoNombre('');
      setMostrarCrear(false);
      await cargarUsuarios();
      onUsuarioChange(nombre);
    } catch (error) {
      console.error('Error creando usuario:', error);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <select
          value={usuarioActual}
          onChange={(e) => onUsuarioChange(e.target.value)}
          className="flex-1 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg px-3 py-2 border border-gray-300 dark:border-gray-600 focus:outline-none focus:border-purple-500 text-sm"
        >
          <option value="anonimo">👤 Anónimo</option>
          {usuarios.map((u) => (
            <option key={u.id} value={u.nombre}>
              👤 {u.nombre}
            </option>
          ))}
        </select>
        <button
          onClick={() => setMostrarCrear(!mostrarCrear)}
          className="p-2 bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors text-white text-sm"
          title="Crear nuevo usuario"
        >
          ➕
        </button>
      </div>

      {mostrarCrear && (
        <div className="flex gap-2">
          <input
            type="text"
            value={nuevoNombre}
            onChange={(e) => setNuevoNombre(e.target.value)}
            placeholder="Nombre del usuario"
            onKeyPress={(e) => e.key === 'Enter' && handleCrear()}
            className="flex-1 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg px-3 py-2 border border-gray-300 dark:border-gray-600 text-sm"
            autoFocus
          />
          <button
            onClick={handleCrear}
            className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-white text-sm"
          >
            ✓
          </button>
        </div>
      )}
    </div>
  );
}