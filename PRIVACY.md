cat > PRIVACY.md << 'ENDOFFILE'
# 🔒 Política de Privacidad y Protección de Datos

**Astro-IA**

**Última actualización:** 14 de septiembre de 2026  
**Versión:** 1.0.0

---

## 📖 Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Responsable del Tratamiento](#2-responsable-del-tratamiento)
3. [Datos que Recopilamos](#3-datos-que-recopilamos)
4. [Finalidad del Tratamiento](#4-finalidad-del-tratamiento)
5. [Base Legal](#5-base-legal)
6. [Uso de Inteligencia Artificial](#6-uso-de-inteligencia-artificial)
7. [Almacenamiento y Seguridad](#7-almacenamiento-y-seguridad)
8. [Compartición con Terceros](#8-compartición-con-terceros)
9. [Transferencias Internacionales](#9-transferencias-internacionales)
10. [Derechos del Usuario](#10-derechos-del-usuario)
11. [Retención de Datos](#11-retención-de-datos)
12. [Cookies y Tecnologías Similares](#12-cookies-y-tecnologías-similares)
13. [Menores de Edad](#13-menores-de-edad)
14. [Cambios en la Política](#14-cambios-en-la-política)
15. [Contacto](#15-contacto)

---

## 1. Introducción

Bienvenido a **Astro-IA** ("la Aplicación", "el Servicio", "nosotros"). 

Esta Política de Privacidad describe cómo recopilamos, usamos, almacenamos y protegemos tu información personal cuando utilizas nuestra aplicación de inteligencia artificial personal.

**Al registrarte y usar Astro-IA, aceptas las prácticas descritas en esta política.**

Nuestro compromiso es:

- ✅ **Transparencia total** sobre qué datos recopilamos
- ✅ **Control absoluto** del usuario sobre su información
- ✅ **Almacenamiento local** — Tus datos permanecen en TU servidor
- ✅ **Sin venta de datos** a terceros bajo ninguna circunstancia
- ✅ **Código abierto** — Puedes auditar cómo manejamos tus datos
- ✅ **Cumplimiento** con GDPR, CCPA y leyes de protección de datos

---

## 2. Responsable del Tratamiento

**Responsable:** El propietario/administrador de la instancia de Astro-IA que estés utilizando.

**Naturaleza del proyecto:** Astro-IA es un proyecto de código abierto. Si estás usando una instancia alojada por un tercero, ese tercero es el responsable del tratamiento de tus datos.

**Contacto:** [Configurar email de contacto del administrador]

---

## 3. Datos que Recopilamos

### 3.1 Datos de Registro

| Dato | Obligatorio | Finalidad |
|------|-------------|-----------|
| **Nombre de usuario** | ✅ Sí | Identificación en la aplicación |
| **Email** | ✅ Sí | Autenticación y comunicación |
| **Contraseña** | ✅ Sí | Seguridad de la cuenta (hasheada con bcrypt) |
| **Fecha de registro** | ✅ Automático | Auditoría y estadísticas |
| **Último login** | ✅ Automático | Seguridad de la cuenta |

### 3.2 Datos de Conversación

| Dato | Almacenamiento | Finalidad |
|------|----------------|-----------|
| **Mensajes enviados** | Local (tu servidor) | Historial de conversaciones |
| **Respuestas de la IA** | Local (tu servidor) | Historial de conversaciones |
| **Títulos de conversaciones** | Local (tu servidor) | Organización |
| **Feedback (👍/👎)** | Local (tu servidor) | Mejora de respuestas |
| **Conocimiento extraído** | Local (tu servidor) | Memoria de la IA |

### 3.3 Datos Técnicos

| Dato | Almacenamiento | Finalidad |
|------|----------------|-----------|
| **Dirección IP** | Solo en logs temporales | Seguridad |
| **User-Agent** | Solo en logs temporales | Compatibilidad |
| **Tokens JWT** | En tu navegador (localStorage) | Autenticación |
| **Preferencias de tema** | En tu navegador (localStorage) | Experiencia de usuario |

### 3.4 Datos que NO Recopilamos

- ❌ Datos biométricos
- ❌ Datos de geolocalización precisa
- ❌ Información financiera
- ❌ Datos de salud
- ❌ Contactos del teléfono
- ❌ Fotos o archivos personales

---

## 4. Finalidad del Tratamiento

Utilizamos tus datos **exclusivamente** para:

### 4.1 Proporcionar el Servicio

- ✅ Autenticarte de forma segura
- ✅ Guardar tus conversaciones
- ✅ Recordar tu conocimiento personal
- ✅ Personalizar las respuestas de la IA
- ✅ Mantener el aislamiento entre usuarios

### 4.2 Mejorar el Servicio

- ✅ Analizar patrones de uso (agregados y anónimos)
- ✅ Identificar errores y bugs
- ✅ Mejorar la calidad de las respuestas

### 4.3 Seguridad

- ✅ Prevenir accesos no autorizados
- ✅ Detectar actividad sospechosa
- ✅ Cumplir con obligaciones legales

### 4.4 Lo que NUNCA hacemos con tus datos

- ❌ Vender tu información a terceros
- ❌ Usar tus conversaciones para entrenar modelos públicos
- ❌ Compartir tus datos con anunciantes
- ❌ Enviarte spam o publicidad no solicitada
- ❌ Perfilar tu comportamiento para fines comerciales

---

## 5. Base Legal

El tratamiento de tus datos se basa en:

| Base Legal | Aplicación |
|------------|------------|
| **Consentimiento** | Al aceptar esta política al registrarte |
| **Ejecución de contrato** | Para proporcionar el servicio solicitado |
| **Interés legítimo** | Seguridad y prevención de fraude |
| **Obligación legal** | Cumplimiento de leyes aplicables |

---

## 6. Uso de Inteligencia Artificial

### 6.1 Modelos Utilizados

Astro-IA utiliza modelos de lenguaje de código abierto:

| Modelo | Proveedor | Licencia | Ejecución |
|--------|-----------|----------|-----------|
| **Mistral** | Mistral AI | Apache 2.0 | Local |
| **Phi-3** | Microsoft | MIT | Local |
| **Llama 3** | Meta | Llama 3 License | Local |

**⚠️ Importante:** Todos los modelos se ejecutan **localmente** en tu servidor mediante **Ollama**. Tus conversaciones **NUNCA** se envían a servidores externos.

### 6.2 Cómo Funciona la IA
```text
Tu mensaje → Tu servidor → Modelo local → Respuesta → Tu servidor → Tú
│
└── NADA sale de tu servidor
```


- ❌ **NO** enviamos tus datos a OpenAI
- ❌ **NO** enviamos tus datos a Google
- ❌ **NO** enviamos tus datos a Anthropic
- ❌ **NO** enviamos tus datos a Mistral AI
- ✅ **TODO** se procesa localmente

### 6.3 Limitaciones de la IA

Debes saber que:

- ⚠️ Las respuestas de la IA **pueden contener errores**
- ⚠️ La IA **no es un sustituto** de asesoramiento profesional (médico, legal, financiero)
- ⚠️ No debes compartir información **altamente sensible** (contraseñas, datos bancarios, etc.)
- ⚠️ La IA aprende de tus conversaciones, pero **solo en tu instancia**

### 6.4 Memoria y Aprendizaje

Astro-IA tiene capacidad de **recordar información** que compartes:

- 📝 Extrae datos de tus conversaciones
- 🏷️ Los clasifica por categorías
- 💾 Los almacena en tu base de datos local
- 🔒 **Solo tú** puedes acceder a tu información

**Puedes eliminar esta información en cualquier momento.**

---

## 7. Almacenamiento y Seguridad

### 7.1 Dónde se Almacenan tus Datos

| Componente | Ubicación | Cifrado |
|------------|-----------|---------|
| **Conversaciones** | Tu servidor (JSON) | ❌ No cifrado* |
| **Base de conocimiento** | Tu servidor (ChromaDB) | ❌ No cifrado* |
| **Contraseñas** | Tu servidor (bcrypt hash) | ✅ Hasheadas |
| **Tokens JWT** | Tu navegador | ✅ Firmados |
| **Preferencias** | Tu navegador | ❌ No cifradas |

*El cifrado depende de la configuración del servidor. Recomendamos cifrar el disco.

### 7.2 Medidas de Seguridad

Implementamos:

- 🔐 **Hash bcrypt** para contraseñas (nunca en texto plano)
- 🎫 **Tokens JWT** firmados con HS256
- 🛡️ **Aislamiento total** entre usuarios
- 🔒 **HTTPS** recomendado en producción
- 🚫 **Sin acceso** a datos de otros usuarios

### 7.3 Responsabilidad del Usuario

Tú eres responsable de:

- ✅ Mantener tu contraseña segura
- ✅ No compartir tu cuenta
- ✅ Cerrar sesión en dispositivos compartidos
- ✅ Reportar actividad sospechosa

---

## 8. Compartición con Terceros

### 8.1 Principio General

**NO compartimos tus datos con terceros**, salvo en los casos descritos a continuación.

### 8.2 Servicios de Terceros (Opcionales)

Si decides usar estas integraciones, algunos datos se comparten:

| Servicio | Datos Compartidos | Cuándo |
|----------|-------------------|--------|
| **Telegram** | Mensajes, ID de Telegram | Solo si activas el bot |
| **Twilio (WhatsApp)** | Mensajes, número de teléfono | Solo si activas WhatsApp |
| **Cloudflare Tunnel** | Tráfico HTTP (cifrado) | Solo si expones el servicio |

**⚠️ Importante:** Estas integraciones son **opcionales**. Si no las usas, no se comparte nada.

### 8.3 Lo que NO Compartimos

- ❌ Tus conversaciones con otros usuarios
- ❌ Tu email con anunciantes
- ❌ Tu información con gobiernos (salvo orden judicial)
- ❌ Tus datos con empresas de análisis

---

## 9. Transferencias Internacionales

Como Astro-IA se ejecuta **localmente en tu servidor**, **no realizamos transferencias internacionales de datos**.

Si usas integraciones opcionales (Telegram, WhatsApp), esas plataformas pueden transferir datos a sus servidores. Consulta sus políticas:

- [Política de Telegram](https://telegram.org/privacy)
- [Política de Twilio](https://www.twilio.com/legal/privacy)

---

## 10. Derechos del Usuario

Tienes **derecho a**:

### 10.1 Acceso
- ✅ Ver todos tus datos almacenados
- ✅ Solicitar una copia completa

### 10.2 Rectificación
- ✅ Corregir información incorrecta
- ✅ Actualizar tu perfil

### 10.3 Supresión ("Derecho al Olvido")
- ✅ Eliminar conversaciones individuales
- ✅ Eliminar TODAS tus conversaciones
- ✅ Eliminar tu cuenta completa

### 10.4 Portabilidad
- ✅ Exportar tus datos en formato JSON
- ✅ Migrar a otra instancia

### 10.5 Oposición
- ✅ Oponerte al tratamiento de tus datos
- ✅ Retirar tu consentimiento

### 10.6 Cómo Ejercer tus Derechos

Todos estos derechos se pueden ejercer desde la propia aplicación:

O contactando al administrador: [jesusalva575@gmail.com]

**Tiempo de respuesta:** Máximo 30 días.

---

## 11. Retención de Datos

| Tipo de Dato | Retención |
|--------------|-----------|
| **Cuenta de usuario** | Hasta que la elimines |
| **Conversaciones** | Hasta que las elimines |
| **Conocimiento de IA** | Hasta que lo elimines |
| **Logs técnicos** | 30 días |
| **Feedback** | Hasta que lo elimines |

**Puedes eliminar cualquier dato en cualquier momento.**

---

## 12. Cookies y Tecnologías Similares

### 12.1 Qué Usamos

Astro-IA usa **localStorage** (no cookies) para:

| Elemento | Propósito | Duración |
|----------|-----------|----------|
| `auth_token` | Sesión de autenticación | 30 días |
| `usuario` | Recordar tu nombre | Persistente |
| `email` | Recordar tu email | Persistente |
| `tema` | Preferencia de tema | Persistente |

### 12.2 Cookies de Terceros

**No usamos cookies de terceros.** No hay Google Analytics, Facebook Pixel, ni rastreadores.

### 12.3 Cómo Eliminar

Puedes borrar `localStorage` desde:
- Configuración del navegador → Privacidad → Datos del sitio
- O usar el botón "Cerrar sesión" (borra el token)

---

## 13. Menores de Edad

Astro-IA **no está dirigida a menores de 16 años**. 

- ❌ No recopilamos datos de menores a sabiendas
- ✅ Si eres padre/madre y detectas datos de tu hijo, contáctanos
- ✅ Eliminaremos la información inmediatamente

---

## 14. Cambios en la Política

### 14.1 Notificación

Cuando actualicemos esta política:

- 📧 Te notificaremos por email
- 🔔 Aparecerá un aviso en la aplicación
- 📅 Indicaremos la fecha de la última actualización

### 14.2 Aceptación

Si los cambios son significativos:

- ✅ Deberás aceptar la nueva versión
- ❌ No podrás usar el servicio sin aceptar
- 🗑️ Puedes eliminar tu cuenta si no estás de acuerdo

### 14.3 Historial de Versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-09-14 | Versión inicial |

---

## 15. Contacto

Para cualquier consulta sobre privacidad:

- 📧 **Email:** [configurar email de contacto]
- 🐛 **Issues de GitHub:** [enlace al repositorio]
- 💬 **Discord/Comunidad:** [enlace si existe]

**Delegado de Protección de Datos (DPO):**  
Si tu jurisdicción lo requiere, puedes contactar a nuestro DPO en: [configurar email]

---

## 📜 Resumen Rápido

| Pregunta | Respuesta |
|----------|-----------|
| ¿Venden mis datos? | ❌ **Nunca** |
| ¿Se envían a OpenAI/Google? | ❌ **Nunca** |
| ¿Se almacenan localmente? | ✅ **Sí, en tu servidor** |
| ¿Otros usuarios pueden ver mis datos? | ❌ **No, aislamiento total** |
| ¿Puedo eliminar mis datos? | ✅ **Sí, en cualquier momento** |
| ¿Puedo exportar mis datos? | ✅ **Sí, en JSON** |
| ¿Usan cookies de terceros? | ❌ **No** |
| ¿Se usan para entrenar modelos? | ❌ **No** |

---

## ⚖️ Cumplimiento Legal

Esta política cumple con:

- 🇪🇺 **GDPR** (Reglamento General de Protección de Datos - UE)
- 🇺🇸 **CCPA** (California Consumer Privacy Act)
- 🇲🇽 **LFPDPPP** (Ley Federal de Protección de Datos Personales - México)
- 🌎 **Estándares internacionales** de protección de datos

---

**Al aceptar esta política, confirmas que:**

1. ✅ Has leído y entendido esta Política de Privacidad
2. ✅ Aceptas el tratamiento de tus datos según lo descrito
3. ✅ Tienes al menos 16 años de edad
4. ✅ Comprendes que Astro-IA es una herramienta de IA y puede cometer errores

---

**Astro-IA** — Tu privacidad es nuestra prioridad. 🔒

*Última actualización: 14 de septiembre de 2026*
ENDOFFILE