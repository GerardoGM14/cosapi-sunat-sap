import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-root',
  template: '<router-outlet></router-outlet>',
  styles: []
})
export class AppComponent implements OnInit {
  title = 'autosun-frontend';

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.checkSystemStatus();
  }

  checkSystemStatus() {
    console.group('%c 🔍 System Status Check ', 'background: #222; color: #bada55; font-size: 14px; padding: 4px; border-radius: 4px;');
    
    // 1. Check Frontend (Implicitly true if this code runs)
    console.log('%c ✅ Frontend: Active (Running)', 'color: green; font-weight: bold;');

    // 2. Check Backend
    const backendUrl = environment.apiUrl.replace('/api', ''); // Base URL
    
    // Usamos endpoint root '/' que retorna mensaje de bienvenida
    // Si environment.apiUrl es '/api' (proxy) o full url, ajustamos.
    // Asumimos que environment.apiUrl apunta a algo como 'http://x.x.x.x:8000/api' o '/api'
    
    // Si apiUrl es relativo (/api), la raiz del backend suele ser el mismo host sin /api o puerto 8000 si es dev
    // Para ser robustos, intentamos contactar al endpoint de salud del backend.
    // Usaremos el endpoint '/' definido en main.py que retorna {message: ...}
    
    // Construimos url raiz del backend
    let healthUrl = '';
    if (environment.apiUrl.startsWith('http')) {
        healthUrl = environment.apiUrl.replace('/api', '/');
    } else {
        // Relative path, likely proxy or same origin
        healthUrl = '/'; // Si hay proxy, '/' deberia ir al backend o frontend? 
        // Si estamos en desarrollo Angular -> proxy.conf.json mapea /api -> localhost:8000
        // Pero '/' suele ser el frontend.
        // Mejor usamos un endpoint explicito del backend: /api/utils/health (si existiera) o el root de la api
        healthUrl = `${environment.apiUrl.replace('/api', '')}/`; 
        // Si apiUrl es '/api', esto queda '/'. Si hay proxy inverso nginx en '/' -> frontend.
        // Mejor atacamos al endpoint que sabemos que es backend: environment.apiUrl + '/...'
        // Pero main.py define root en '/' (app.get("/")).
        // Si usamos '/api/', fastAPI lo maneja? No, el prefix es en routers.
        
        // Vamos a intentar hacer un ping a un endpoint seguro del backend.
        // main.py tiene @app.get("/")
    }

    // Simplificación: Usaremos el endpoint '/' del backend.
    // Si estamos usando la URL completa en environment (prod/dev):
    const targetUrl = environment.apiUrl.replace(/\/api\/?$/, ''); // Remove trailing /api

    this.http.get(targetUrl).subscribe({
        next: (res) => {
            console.log('%c ✅ Backend: Active (Connected)', 'color: green; font-weight: bold;');
            console.log('   Response:', res);
            
            // 3. Check Sunat/Sap Service
            // El servicio no es un servidor HTTP per se, es un script que el backend ejecuta.
            // Verificamos si el backend puede "ver" el servicio.
            // Podríamos añadir un endpoint ligero en backend para chequear existencia de carpetas/archivos del servicio.
            this.checkServiceStatus();
        },
        error: (err) => {
            console.log('%c ❌ Backend: Inactive or Unreachable', 'color: red; font-weight: bold;');
            console.error('   Error:', err);
        }
    });
  }

  checkServiceStatus() {
      // Llamamos a un nuevo endpoint que crearemos en utils para verificar integridad del servicio
      this.http.get(`${environment.apiUrl}/utils/check-service`).subscribe({
          next: (res: any) => {
              if (res.status === 'ok') {
                  console.log('%c ✅ Service Core: Active (Ready)', 'color: green; font-weight: bold;');
              } else {
                  console.log('%c ⚠️ Service Core: Warning', 'color: orange; font-weight: bold;', res.message);
              }
              console.groupEnd();
          },
          error: (err) => {
              console.log('%c ❌ Service Core: Not Detected', 'color: red; font-weight: bold;');
              console.groupEnd();
          }
      });
  }
}
