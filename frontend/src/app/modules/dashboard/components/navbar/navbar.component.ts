import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  @Output() toggleSidebar = new EventEmitter<void>();
  breadcrumbItems: { label: string; active: boolean }[] = [];
  showHomeIcon = true;

  constructor(private router: Router) {}

  ngOnInit() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.updateBreadcrumbs(event.url);
    });
    
    // Set initial title
    this.updateBreadcrumbs(this.router.url);
  }

  updateBreadcrumbs(url: string) {
    if (url.includes('config')) {
      this.breadcrumbItems = [
        { label: 'Home', active: false },
        { label: 'Configuración', active: true }
      ];
      this.showHomeIcon = true;
    } else if (url.includes('ejecuciones')) {
      this.breadcrumbItems = [
        { label: 'Home', active: false },
        { label: 'Ejecuciones', active: true }
      ];
      this.showHomeIcon = true;
    } else if (url.includes('programacion')) {
      this.breadcrumbItems = [
        { label: 'Home', active: false },
        { label: 'Programación', active: true }
      ];
      this.showHomeIcon = true;
    } else if (url.includes('maestros/sociedades') || url.includes('sociedades')) {
      this.breadcrumbItems = [
        { label: 'Maestros', active: false },
        { label: 'Sociedades', active: true }
      ];
      this.showHomeIcon = true;
    } else if (url.includes('maestros/usuarios') || url.includes('usuarios')) {
      this.breadcrumbItems = [
        { label: 'Maestros', active: false },
        { label: 'Usuarios', active: true }
      ];
      this.showHomeIcon = true;
    } else {
      this.breadcrumbItems = [];
      this.showHomeIcon = true;
    }
  }

  onToggleSidebar() {
    this.toggleSidebar.emit();
  }
}
