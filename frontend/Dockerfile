FROM node:20-alpine

WORKDIR /app

# Copiar package.json y package-lock.json
COPY package.json package-lock.json* ./

# Instalar dependencias (usando legacy-peer-deps para beta)
RUN npm install --legacy-peer-deps

# Copiar el resto del código
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]