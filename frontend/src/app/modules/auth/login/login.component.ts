import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

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

  constructor(private http: HttpClient, private router: Router) {}

  login() {
    this.loading = true;
    this.errorMessage = '';
    this.loginSuccess = false;

    // URL del Backend Python (Asegúrate que el puerto coincida con Uvicorn)
    const apiUrl = 'http://localhost:8000/api/auth/login';

    this.http.post<any>(apiUrl, this.credentials).subscribe({
      next: (response) => {
        console.log('Login exitoso', response);
        localStorage.setItem('token', response.access_token);
        
        // Activar estado de éxito
        this.loading = false;
        this.loginSuccess = true;

        // Esperar 1.5 segundos y redirigir a Configuración
        setTimeout(() => {
          this.router.navigate(['/config']);
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
