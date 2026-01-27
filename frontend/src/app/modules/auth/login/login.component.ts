import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AppConfigService } from '../../../services/app-config.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  credentials = {
    username: '',
    password: ''
  };
  errorMessage = '';
  loading = false;
  loginSuccess = false;

  constructor(private http: HttpClient, private router: Router, private configService: AppConfigService) {}

  login() {
    this.loading = true;
    this.errorMessage = '';
    this.loginSuccess = false;

    // URL del Backend Python (Cargada desde config.json)
    const apiUrl = `${this.configService.apiUrl}/auth/login`;

    this.http.post<any>(apiUrl, this.credentials).subscribe({
      next: (response) => {
        console.log('Login exitoso', response);
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('username', this.credentials.username);
        
        // Activar estado de éxito
        this.loading = false;
        this.loginSuccess = true;

        // Esperar 1.5 segundos y redirigir a Dashboard
        setTimeout(() => {
          this.router.navigate(['/ejecuciones']);
        }, 1500);
      },
      error: (error) => {
        console.error('Error login', error);
        this.errorMessage = 'Credenciales inválidas o error de servidor';
        this.loading = false;
        this.loginSuccess = false;

        // Auto-ocultar el Toast después de 4 segundos
        setTimeout(() => {
          this.errorMessage = '';
        }, 4000);
      }
    });
  }
}
