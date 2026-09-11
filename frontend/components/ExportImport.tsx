'use client';

import { useState, useRef } from 'react';
import { exportarConocimiento, importarConocimiento } from '@/lib/api';

interface ExportImportProps {
  usuario: string;
}

export function ExportImport({ usuario }: ExportImportProps) {
  const [exportando, setExportando] = useState(false);
  const [importando, setImportando] = useState(false);
  const [resultado, setResultado] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleExportar = async () => {
    setExportando(true);
    setResultado(null);
    try {
      await exportarConocimiento(usuario !== 'anonimo' ? usuario : undefined);
      setResultado('✅ Conocimiento exportado correctamente');
    } catch (error) {
      setResultado('❌ Error al exportar');
      console.error(error);
    } finally {
      setExportando(false);
    }
  };

  const handleImportar = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const archivo = e.target.files?.[0];
    if (!archivo) return;

    setImportando(true);
    setResultado(null);
    try {
      const resultado = await importarConocimiento(archivo);
      setResultado(`✅ Importados: ${resultado.importados} items`);
    } catch (error) {
      setResultado('❌ Error al importar');
      console.error(error);
    } finally {
      setImportando(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700 shadow-sm">
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        💾 Exportar / Importar
      </h3>
      
      <div className="space-y-2">
        <button
          onClick={handleExportar}
          disabled={exportando}
          className="w-full text-left px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {exportando ? '⏳ Exportando...' : '📤 Exportar conocimiento'}
        </button>
        
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={importando}
          className="w-full text-left px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {importando ? '⏳ Importando...' : '📥 Importar conocimiento'}
        </button>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleImportar}
          className="hidden"
        />
        
        {resultado && (
          <div className="text-xs text-gray-600 dark:text-gray-400 mt-2 p-2 bg-gray-50 dark:bg-gray-700/50 rounded">
            {resultado}
          </div>
        )}
      </div>
    </div>
  );
}