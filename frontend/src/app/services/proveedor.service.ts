import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AppConfigService } from './app-config.service';

@Injectable({
  providedIn: 'root'
})
export class ProveedorService {

  constructor(
    private http: HttpClient,
    private config: AppConfigService
  ) { }

  private get baseUrl(): string {
    return `${this.config.apiUrl}/crud`;
  }

  getProveedores(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/proveedores`);
  }

  uploadExcel(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(`${this.baseUrl}/proveedores/upload`, formData);
  }

  previewExcel(file: File): Observable<any[]> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<any[]>(`${this.baseUrl}/proveedores/preview`, formData);
  }

  importBatch(proveedores: any[]): Observable<any> {
    return this.http.post(`${this.baseUrl}/proveedores/batch`, proveedores);
  }

  deleteProveedor(ruc: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/proveedores/${ruc}`);
  }

  updateSociedades(ruc: string, sociedades: string[]): Observable<any> {
    return this.http.put(`${this.baseUrl}/proveedores/${ruc}/sociedades`, { sociedades });
  }
}
