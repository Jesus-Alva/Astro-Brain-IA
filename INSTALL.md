# 🚀 Guía de Instalación - Astro-IA

Guía completa para instalar y ejecutar **Astro-IA** en tu máquina local desde cero.

---

## 📋 Tabla de Contenidos

- [Requisitos Previos](#-requisitos-previos)
- [Instalación Rápida con Docker](#-instalación-rápida-con-docker-recomendado)
- [Instalación Manual](#-instalación-manual-sin-docker)
- [Configuración Avanzada](#-configuración-avanzada)
- [Verificación](#-verificación)
- [Solución de Problemas](#-solución-de-problemas)
- [Actualización](#-actualización)
- [Desinstalación](#-desinstalación)

---

## 📦 Requisitos Previos

### Hardware Mínimo

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **RAM** | 8 GB | 16 GB |
| **Disco libre** | 15 GB | 25 GB |
| **CPU** | 2 cores | 4+ cores |
| **GPU** | Opcional | NVIDIA (opcional, acelera la IA) |

> **Nota:** El modelo `mistral` ocupa ~4.4 GB. Si tienes menos de 8 GB de RAM, usa `phi3` (2.3 GB).

### Software Necesario

| Software | Versión | Cómo verificar |
|----------|---------|----------------|
| **Docker** | 20.10+ | `docker --version` |
| **Docker Compose** | 2.0+ | `docker compose version` |
| **Git** | 2.30+ | `git --version` |

### Instalar Docker

**Linux (Fedora):**
```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar para aplicar el grupo
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Cerrar sesión y volver a entrar
```

**macOS / Windows:**
Descarga [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Instalar Git

**Fedora:**
```bash
sudo dnf install -y git
```

**Ubuntu/Debian:**
```bash
sudo apt install -y git
```
**macOS:**
```bash
brew install git
```

# 🚀 Instalación Rápida con Docker (Recomendado)

### Paso 1: Clonar el repositorio
```bash
git clone https://github.com/Jesus-Alva/Astro-Brain-IA.git
cd Astro-Brain-IA
```

### Paso 2: Configurar variables de entorno
```bash
# Copiar la plantilla
cp .env.example .env

# Editar con tu editor preferido
nano .env
# o
vim .env
# o
code .env
```

#### Configuración mínima (valores por defecto funcionan):
```bash
BACKEND_PORT=8000
OLLAMA_MODEL=mistral
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Paso 3: Construir y levantar los servicios
```bash
# Construir las imágenes
docker compose build

# Levantar los servicios en segundo plano
docker compose up -d
```

Verificar el estado:
```bash
docker compose ps
```

Deberias ver algo asi
```bash
NAME                    SERVICE          STATUS
astro-ollama            ollama           running
astro-backend           backend          running
astro-frontend          frontend         running
```

### Paso 4: Descargar el modelo de IA
En otra terminal, descarga el modelo:
```bash
# Modelo Mistral (~4.4 GB) - recomendado
docker compose exec ollama ollama pull mistral
```

Verás una barra de progreso:
```bash
pulling manifest
pulling 8934d96d3f08... 100% ▕████████████████▏ 3.8 GB
pulling 8c17c2ebb0ea... 100% ▕████████████████▏ 7.0 KB
...
success
```

Alternativa más ligera (si tienes poca RAM):
```bash
docker compose exec ollama ollama pull phi3
```

Y actualiza .env:
```bash
OLLAMA_MODEL=phi3
```

Luego reinicia el backend:
```bash
docker compose restart backend
```

### Paso 5: Verificar que todo funciona

```bash
# Verificar backend
curl http://localhost:8000
```
Respuesta esperada:
```bash
{"nombre":"Astro-IA API","version":"3.0","estado":"online"}
```
```bash
# Verificar que Ollama tiene el modelo
docker compose exec ollama ollama list
```

Respuesta esperada:
```bash
NAME              ID              SIZE      MODIFIED
mistral:latest    6577803aa9a0    4.4 GB    X minutes ago
```

### Paso 6: Acceder a la aplicación
Abre tu navegador:

|Servicio|	URL	Descripción|
|-|-|
|Frontend|	http://localhost:3000	Interfaz de chat|
|Backend|	http://localhost:8000	API REST|
|API| Docs	http://localhost:8000/docs	Documentación interactiva|
|Ollama|	http://localhost:11434	Runtime de IA|
|¡Listo! 🎉 Empieza a chatear en http://localhost:3000|

# 🔧 Instalación Manual (sin Docker)
Si prefieres no usar Docker, sigue estos pasos.

### Requisitos adicionales
- Python 3.11+

- Node.js 20+

- Ollama instalado en el sistema

### 1. Instalar Ollama
Linux / macOS:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Windows: Descarga desde [ollama.com](https://ollama.com/download)

```bash
ollama pull mistral
```

### 2. Backend (Python)
```bash
# Ir al directorio del backend
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate          # Linux / macOS
# venv\Scripts\activate           # Windows

# Actualizar pip e instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Configurar variables de entorno
cp ../.env.example .env
# Editar .env si es necesario

# Iniciar el backend
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

El backend estará en [http://localhost:8000](http://localhost:8000)

### 3. Frontend (Next.js)

En otra terminal:
```bash
# Ir al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp ../.env.example .env.local

# Iniciar en modo desarrollo
npm run dev
```

El frontend estará en [http://localhost:3000](http://localhost:3000)

# ⚙️ Configuración Avanzada
### Variables de entorno principales

|Variable|	Descripción	|Valor por defecto|
|-|-|-|
|BACKEND_PORT|	Puerto del backend	| 8000|
|OLLAMA_MODEL|	Modelo de IA a usar	|mistral|
|OLLAMA_KEEP_ALIVE|	Tiempo que el modelo permanece en memoria |24h|
|IA_PERSONALIDAD|	Personalidad por defecto|amigable|
|IA_TEMPERATURA|	Creatividad |(0.0 - 1.0)	0.7|
|NEXT_PUBLIC_API_URL|	URL del backend|http://localhost:8000|
|TELEGRAM_TOKEN|	Token del bot de Telegram (opcional)|(vacío)|

### Personalidades disponibles

|Personalidad|	Descripción	|Emoji|
|-|-|
|amigable|	Cálida y cercana	|😊|
|profesional|	Formal y precisa	|💼|
|creativo|	Original e imaginativa	|🎨|
|sarcastico|	Con humor irónico	|😏|

### Cambiar modelo de IA
```bash
# 1. Descargar el nuevo modelo
docker compose exec ollama ollama pull llama3

# 2. Actualizar .env
nano .env
# Cambiar: OLLAMA_MODEL=llama3

# 3. Reiniciar el backend
docker compose restart backend
```

### Modelos recomendados según tu hardware

|Modelo|	Tamaño|	RAM mínima|	Calidad	Uso|
|-|-|-|-|
|phi3|	2.3 GB|	4 GB|	⭐⭐⭐|	Equipos con poca RAM|
|mistral|	4.4 GB|	8 GB|	⭐⭐⭐⭐|	Recomendado|
|llama3|	4.7 GB|	8 GB|	⭐⭐⭐⭐⭐|	Mejor calidad|
|llama3:70b|	40 GB|	32 GB|	⭐⭐⭐⭐⭐⭐|	Servidores potentes|

### Configurar el bot de Telegram (opcional)
1. Abre Telegram y busca @BotFather

2. Envía /newbot y sigue las instrucciones

3. Copia el token que te da

4. Añádelo a .env:

```bash
TELEGRAM_TOKEN=7123456789:AAHxxxxxxxxxxxxxxxxxxxxx
```

5. Reinicia el servicio:
```bash
docker compose restart telegram-bot
```

# ✅ Verificación

### Script de verificación completo

Copia y ejecuta este script para verificar toda la instalación:

```bash
cat > verificar.sh << 'EOF'
#!/bin/bash

echo "🔍 Verificando instalación de Astro-IA..."
echo ""

# 1. Contenedores
echo "1️⃣ Contenedores Docker:"
docker compose ps

# 2. Backend
echo ""
echo "2️⃣ Backend (puerto 8000):"
curl -s http://localhost:8000 | head -c 100
echo ""

# 3. Modelo Ollama
echo ""
echo "3️⃣ Modelos disponibles:"
docker compose exec ollama ollama list 2>/dev/null

# 4. Frontend
echo ""
echo "4️⃣ Frontend (puerto 3000):"
curl -s http://localhost:3000 -o /dev/null -w "HTTP %{http_code}\n"

# 5. Prueba de chat
echo ""
echo "5️⃣ Prueba de chat:"
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"mensaje": "Hola", "usuario": "test"}' \
  | head -c 200
echo ""

echo ""
echo "✅ Verificación completada"
EOF

chmod +x verificar.sh
./verificar.sh
```

### Verificación manual
|Verificación|	Comando|	Resultado esperado|
|-|-|-|
|Contenedores activos|	docker compose ps|	3+ servicios running|
|Backend responde|	curl http://localhost:8000|	JSON con "estado":"online"|
|Modelo descargado|	docker compose exec ollama ollama list|	mistral:latest visible|
|Frontend accesible	Abrir| http://localhost:3000|	Interfaz de chat|

### 🐛 Solución de Problemas
#### Error: port is already allocated
Causa: Otro servicio usa el puerto 8000, 3000 o 11434.

Solución:
```bash
# Ver qué está usando el puerto
sudo ss -tulpn | grep 8000
sudo ss -tulpn | grep 3000

# Opción 1: Detener el proceso conflictivo
# Opción 2: Cambiar el puerto en .env
BACKEND_PORT=8001
```

#### Error: model "mistral" not found
Causa: El modelo no está descargado.

Solución:
```bash
docker compose exec ollama ollama pull mistral
```

#### Error: no such column: collections.topic
Causa: Base de datos ChromaDB incompatible con la versión actual.

Solución:
```bash
# 1. Detener servicios
docker compose down

# 2. Backup y limpieza
mv conocimiento conocimiento_backup_$(date +%Y%m%d_%H%M%S)
mkdir -p conocimiento
chmod 755 conocimiento

# 3. Reiniciar
docker compose up -d
```

#### Error: Cannot connect to Ollama
Causa: Ollama no está corriendo o no es accesible.

Solución:
```bash
# Verificar estado
docker compose ps ollama

# Reiniciar
docker compose restart ollama

# Ver logs
docker compose logs ollama
```

#### Error: Failed to fetch en el frontend
Causa: El frontend no puede conectar con el backend.

Solución:
```bash
# 1. Verificar que el backend responde
curl http://localhost:8000

# 2. Verificar variables de entorno
cat .env | grep NEXT_PUBLIC

# 3. Verificar que el navegador puede acceder al backend
#    Debe ser http://localhost:8000 (NO http://backend:8000)
```

#### Error: no space left on device
Causa: Docker se quedó sin espacio.

Solución:
```bash
# Limpiar recursos no usados
docker system prune -a

# Ver uso de disco
docker system df
```

#### El backend se reinicia constantemente
Causa: Error en el código Python.

Solución:
```bash
# Ver logs detallados
docker compose logs --tail=100 backend

# Buscar errores específicos
docker compose logs backend | grep -iE "(error|traceback|exception)"
```

#### El contenedor tarda mucho en iniciar
Causa: Ollama está cargando el modelo en memoria (la primera vez tarda).

Solución: Espera 1-2 minutos la primera vez. Las siguientes serán más rápidas.

#### La respuesta de la IA es muy lenta
Causas posibles:

- Poca RAM

- Modelo muy grande

- CPU sin aceleración

Soluciones:
```bash
# Usar un modelo más ligero
docker compose exec ollama ollama pull phi3
# Editar .env: OLLAMA_MODEL=phi3
docker compose restart backend
```

# 🔄 Actualización
Actualizar desde GitHub

```bash
# 1. Detener servicios
docker compose down

# 2. Backup del conocimiento
tar -czf backup_conocimiento_$(date +%Y%m%d).tar.gz conocimiento/

# 3. Actualizar código
git pull origin main

# 4. Reconstruir imágenes
docker compose build --no-cache

# 5. Levantar
docker compose up -d

# 6. Verificar
docker compose ps
```

Actualizar solo un servicio
```bash
# Ejemplo: solo el backend
docker compose build --no-cache backend
docker compose up -d backend
```

# 🗑️ Desinstalación
#### Detener sin borrar datos
```bash
docker compose down
```

#### Detener y borrar contenedores (mantiene datos)
```bash
docker compose down --rmi local
```

#### Eliminar TODO (contenedores + volúmenes + datos)
```bash
# ⚠️ CUIDADO: Esto borra el conocimiento acumulado
docker compose down -v
docker system prune -a
```
