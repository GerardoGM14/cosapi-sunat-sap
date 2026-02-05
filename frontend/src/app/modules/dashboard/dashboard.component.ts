import { Component, OnInit } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  isMobileSidebarOpen = false;
  username = '';
  userEmail = '';
  avatarUrl = '';
  pageTitle = 'Ejecuciones';

  constructor(private router: Router) {
    this.username = localStorage.getItem('username') || 'Usuario Invitado';
    // Simular email basado en usuario si no es un email real
    this.userEmail = this.username.includes('@') ? this.username : `${this.username.toLowerCase().replace(/\s+/g, '.')}@cosapi.com`;
    
    // Generar avatar aleatorio pero consistente basado en el nombre de usuario
    // Usamos DiceBear 'notionists-neutral' para un diseño diferente
    this.avatarUrl = `https://api.dicebear.com/9.x/notionists-neutral/svg?seed=${encodeURIComponent(this.username)}`;
  }

  ngOnInit() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.updateTitle(event.url);
    });
    
    // Set initial title
    this.updateTitle(this.router.url);
  }

  updateTitle(url: string) {
    if (url.includes('config')) {
      this.pageTitle = 'Configuración';
    } else if (url.includes('ejecuciones')) {
      this.pageTitle = 'Ejecuciones';
    } else {
      this.pageTitle = '';
    }
  }

  toggleMobileSidebar() {
    this.isMobileSidebarOpen = !this.isMobileSidebarOpen;
  }

  closeMobileSidebar() {
    this.isMobileSidebarOpen = false;
  }

  loggingOut = false;

  logout() {
    this.loggingOut = true;
    setTimeout(() => {
      localStorage.removeItem('token');
      this.router.navigate(['/login']);
    }, 2000);
  }
}
