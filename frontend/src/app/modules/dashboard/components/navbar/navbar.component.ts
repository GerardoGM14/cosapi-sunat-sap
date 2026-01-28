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
  pageTitle = 'Ejecuciones';

  constructor(private router: Router) {}

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
    } else if (url.includes('programacion')) {
      this.pageTitle = 'Programación';
    } else {
      this.pageTitle = '';
    }
  }

  onToggleSidebar() {
    this.toggleSidebar.emit();
  }
}
