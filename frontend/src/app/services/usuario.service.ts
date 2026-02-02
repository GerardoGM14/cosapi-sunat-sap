import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AppConfigService } from './app-config.service';

export interface Usuario {
  iMusuario: number;
  tNombre: string;
  tApellidos: string;
  tCorreo: string;
  tClave: string;
  iMRol?: number;
  lNotificacion: boolean;
  lActivo: boolean;
  fRegistro?: string;
  // Optional for UI
  showClave?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class UsuarioService {

  constructor(
    private http: HttpClient,
    private config: AppConfigService
  ) { }

  private get baseUrl(): string {
    return `${this.config.apiUrl}/crud`;
  }

  getAll(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(`${this.baseUrl}/usuarios`);
  }

  create(usuario: any): Observable<Usuario> {
    return this.http.post<Usuario>(`${this.baseUrl}/usuarios`, usuario);
  }

  update(id: number, usuario: any): Observable<Usuario> {
    return this.http.put<Usuario>(`${this.baseUrl}/usuarios/${id}`, usuario);
  }

  delete(id: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/usuarios/${id}`);
  }
}
