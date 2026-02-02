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
      // Si config.json ya tiene localhost:8001/api, está bien.
      if (this.config.apiUrl === '/api') {
          this.config.apiUrl = 'http://localhost:8001/api';
      }
    } else {
      // En Linux (Servidor/Producción), usar ruta relativa para que Nginx maneje el proxy
      this.config.apiUrl = '/api';
      console.log(`🔧 Production detected (${currentHost}). Using relative API path: ${this.config.apiUrl}`);
    }
  }

  get apiUrl(): string {
    return this.config.apiUrl;
  }
}
