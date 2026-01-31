import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AppConfigService } from './app-config.service';

export interface Sociedad {
  tRuc: string;
  tRazonSocial: string;
  tUsuario: string;
  tClave: string;
  lActivo: boolean;
  // Optional fields for UI logic
  showClave?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class SociedadService {

  constructor(
    private http: HttpClient,
    private config: AppConfigService
  ) { }

  private get baseUrl(): string {
    return `${this.config.apiUrl}/crud`;
  }

  getAll(): Observable<Sociedad[]> {
    // Check backend/app/api/utils.py or wherever societies are exposed
    // If not exposed, I might need to create the endpoint too.
    // Let's assume standard REST for now, but I better check backend routes first.
    return this.http.get<Sociedad[]>(`${this.baseUrl}/sociedades`);
  }

  create(sociedad: any): Observable<Sociedad> {
    return this.http.post<Sociedad>(`${this.baseUrl}/sociedades`, sociedad);
  }

  update(ruc: string, sociedad: any): Observable<Sociedad> {
    return this.http.put<Sociedad>(`${this.baseUrl}/sociedades/${ruc}`, sociedad);
  }
  
  delete(ruc: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/sociedades/${ruc}`);
  }
}
