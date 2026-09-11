import axios from 'axios';

class AstroBrain {
  constructor(config = {}) {
    this.config = {
      apiUrl: config.apiUrl || 'http://localhost:8000',
      wsUrl: config.wsUrl || 'ws://localhost:8000/ws',
      usuario: config.usuario || 'anonimo',
      onMessage: config.onMessage || (() => {}),
      onError: config.onError || (() => {}),
      onConnect: config.onConnect || (() => {}),
      onDisconnect: config.onDisconnect || (() => {}),
    };

    this.ws = null;
    this.connected = false;
  }

  async conectar() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.config.wsUrl);
        
        this.ws.onopen = () => {
          this.connected = true;
          this.config.onConnect();
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const mensaje = JSON.parse(event.data);
            this.config.onMessage(mensaje);
          } catch (error) {
            this.config.onError(error);
          }
        };

        this.ws.onerror = (error) => {
          this.config.onError(error);
          reject(error);
        };

        this.ws.onclose = () => {
          this.connected = false;
          this.config.onDisconnect();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  async enviarMensaje(mensaje) {
    try {
      const response = await axios.post(
        `${this.config.apiUrl}/chat`,
        {
          mensaje,
          usuario: this.config.usuario,
        }
      );
      return response.data;
    } catch (error) {
      this.config.onError(error);
      throw error;
    }
  }

  desconectar() {
    if (this.ws) {
      this.ws.close();
      this.connected = false;
    }
  }
}

export default AstroBrain;