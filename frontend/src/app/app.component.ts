import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfigService } from './services/app-config.service';

@Component({
  selector: 'app-root',
  template: '<router-outlet></router-outlet>',
  styles: []
})
export class AppComponent implements OnInit {
  title = 'autosun-frontend';

  constructor(private http: HttpClient, private configService: AppConfigService) {}

  ngOnInit() {
    this.checkSystemStatus();
  }

  checkSystemStatus() {
    console.group('%c 🔍 System Status Check ', 'background: #222; color: #bada55; font-size: 14px; padding: 4px; border-radius: 4px;');
    
    // 1. Check Frontend (Implicitly true if this code runs)
    console.log('%c ✅ Frontend: Active (Running)', 'color: green; font-weight: bold;');
    
    // 2. Check Backend using ConfigService
    this.checkServiceStatus();
  }

  checkServiceStatus() {
      // Llamamos a un nuevo endpoint que crearemos en utils para verificar integridad del servicio
      const apiUrl = this.configService.apiUrl;
      this.http.get(`${apiUrl}/utils/check-service`).subscribe({
          next: (res: any) => {
              console.log('%c ✅ Backend: Active (Connected)', 'color: green; font-weight: bold;');
              
              if (res.status === 'ok') {
                  console.log('%c ✅ Service Core: Active (Ready)', 'color: green; font-weight: bold;');
                  
                  // Mostrar estado Headless
                  if (res.headless_mode) {
                      const isHeadless = String(res.headless_mode).toLowerCase().includes('true');
                      const headlessColor = isHeadless ? 'color: #00ffff;' : 'color: #ffd700;'; // Cyan or Gold
                      const icon = isHeadless ? '👻' : '🖥️';
                      console.log(`%c ${icon} Headless Mode: ${res.headless_mode}`, `${headlessColor} font-weight: bold;`);
                  }

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
