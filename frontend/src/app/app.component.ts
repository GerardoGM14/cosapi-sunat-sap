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
    const targetUrl = environment.apiUrl.replace(/\/api\/?$/, '/'); // Remove trailing /api and add /

    // El endpoint root '/' puede devolver HTML si es interceptado por un servidor web (nginx) que sirve el frontend
    // O puede devolver JSON si le pega directo al backend.
    // El error "Http failure during parsing" indica que recibió HTML (texto) cuando esperaba JSON.
    // Solución: Especificar responseType: 'text' para evitar error de parsing si devuelve HTML (frontend),
    // o mejor aun, consultar un endpoint de API que sabemos devuelve JSON.
    
    // CAMBIO: Consultar un endpoint seguro de la API (/api/utils/check-service) que ya usamos luego,
    // o el root de la API '/api/' si el backend lo soporta, o '/api/utils/health' si existiera.
    // Como checkServiceStatus ya verifica el backend indirectamente, podemos unificarlo o usar el root del backend '/'
    // sabiendo que puede fallar si devuelve HTML.
    
    // Mejor enfoque: Consultar directamente el endpoint de servicio. Si responde, el backend está vivo.
    // Así evitamos el problema de que '/' sea interceptado por el servidor web y devuelva el index.html del frontend.
    
    this.checkServiceStatus(); // Check directo al backend
  }

  checkServiceStatus() {
      // Llamamos a un nuevo endpoint que crearemos en utils para verificar integridad del servicio
      // Este endpoint sirve doble propósito: Verifica Backend vivo y Servicio scripts presentes.
      this.http.get(`${environment.apiUrl}/utils/check-service`).subscribe({
          next: (res: any) => {
              console.log('%c ✅ Backend: Active (Connected)', 'color: green; font-weight: bold;');
              
              if (res.status === 'ok') {
                  console.log('%c ✅ Service Core: Active (Ready)', 'color: green; font-weight: bold;');
              } else {
                  console.log('%c ⚠️ Service Core: Warning', 'color: orange; font-weight: bold;', res.message);
              }
              console.groupEnd();
          },
          error: (err) => {
              console.log('%c ❌ Backend: Inactive or Unreachable', 'color: red; font-weight: bold;');
              console.error('   Error:', err);
              console.groupEnd();
          }
      });
  }
}
