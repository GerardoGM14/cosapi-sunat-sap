import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AppConfigService {
  private config: any = {};

  constructor(private http: HttpClient) {}

  async loadConfig(): Promise<void> {
    try {
      this.config = await firstValueFrom(this.http.get('assets/config.json'));
      this.adjustConfigForEnvironment();
    } catch (error) {
      console.error('Could not load configuration:', error);
      // Fallback in case file is missing
      this.config = { apiUrl: 'http://localhost:8001/api' };
      this.adjustConfigForEnvironment();
    }
  }

  private adjustConfigForEnvironment(): void {
    const currentHost = window.location.hostname;
    const isLocalhost = currentHost === 'localhost' || currentHost === '127.0.0.1';
    
    if (isLocalhost) {
      // En Windows (Local), aseguramos que apunte al backend local
      if (this.config.apiUrl === '/api') {
          this.config.apiUrl = 'http://localhost:8001/api';
      }
    } else {
      // En Linux/Remoto (192.168.x.x, etc.)
      // Opción 1: Usar Nginx Proxy (Requiere configuración de sockets en Nginx) -> this.config.apiUrl = '/api';
      // Opción 2: Conectar directo al puerto 8001 (Más fácil, evita configurar Nginx)
      
      const protocol = window.location.protocol; // http: o https:
      this.config.apiUrl = `${protocol}//${currentHost}:8001/api`;
      
      console.log(`🔧 Remote environment detected (${currentHost}). Auto-configuring API to: ${this.config.apiUrl}`);
    }
  }

  get apiUrl(): string {
    return this.config.apiUrl;
  }
}
