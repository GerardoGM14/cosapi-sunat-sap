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
    } catch (error) {
      console.error('Could not load configuration:', error);
      // Fallback in case file is missing
      this.config = { apiUrl: 'http://localhost:8000' };
    }
  }

  get apiUrl(): string {
    return this.config.apiUrl;
  }
}
