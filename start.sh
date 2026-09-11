#!/bin/bash
# ============================================
#  start.sh - Inicio rápido de Astro-IA
# ============================================

echo "🚀 Astro-IA - Inicio rápido"
echo "================================"

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

# Verificar Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

# Opciones
echo ""
echo "Selecciona una opción:"
echo "1) Iniciar todos los servicios"
echo "2) Ver logs"
echo "3) Detener todos los servicios"
echo "4) Limpiar (detener + eliminar volúmenes)"
echo "5) Salir"
echo ""
read -p "Opción (1-5): " option

case $option in
    1)
        echo "📦 Construyendo imágenes..."
        docker compose -f docker/docker-compose.yml build
        
        echo "🚀 Iniciando servicios..."
        docker compose -f docker/docker-compose.yml up -d
        
        echo ""
        echo "✅ Servicios iniciados:"
        echo "  🌐 Frontend: http://localhost:3000"
        echo "  🔌 Backend API: http://localhost:8000"
        echo "  📚 API Docs: http://localhost:8000/docs"
        echo "  🧠 Ollama: http://localhost:11434"
        echo ""
        echo "📝 Para ver logs: docker compose -f docker/docker-compose.yml logs -f"
        ;;
    2)
        docker compose -f docker/docker-compose.yml logs -f
        ;;
    3)
        echo "🛑 Deteniendo servicios..."
        docker compose -f docker/docker-compose.yml down
        echo "✅ Servicios detenidos"
        ;;
    4)
        echo "⚠️  Esto eliminará todos los datos y volúmenes"
        read -p "¿Estás seguro? (s/N): " confirm
        if [[ $confirm == "s" || $confirm == "S" ]]; then
            docker compose -f docker/docker-compose.yml down -v
            echo "✅ Limpiado completamente"
        else
            echo "❌ Operación cancelada"
        fi
        ;;
    5)
        exit 0
        ;;
    *)
        echo "❌ Opción inválida"
        ;;
esac