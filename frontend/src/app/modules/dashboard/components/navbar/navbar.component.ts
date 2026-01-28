import { Component, OnInit, Output, EventEmitter, OnDestroy } from '@angular/core';
import { trigger, transition, style, animate } from '@angular/animations';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { Subscription } from 'rxjs';
import { NetworkStatusService } from '../../../../services/network-status.service';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css'],
  animations: [
    trigger('fadeInOut', [
      transition(':enter', [
        style({ opacity: 0 }),
        animate('200ms ease-out', style({ opacity: 1 }))
      ]),
      transition(':leave', [
        animate('200ms ease-in', style({ opacity: 0 }))
      ])
    ]),
    trigger('scaleUp', [
      transition(':enter', [
        style({ transform: 'scale(0.95)', opacity: 0 }),
        animate('300ms cubic-bezier(0.16, 1, 0.3, 1)', style({ transform: 'scale(1)', opacity: 1 }))
      ]),
      transition(':leave', [
        animate('200ms cubic-bezier(0.16, 1, 0.3, 1)', style({ transform: 'scale(0.95)', opacity: 0 }))
      ])
    ])
  ]
})
export class NavbarComponent implements OnInit, OnDestroy {
  @Output() toggleSidebar = new EventEmitter<void>();
  breadcrumbItems: { label: string; active: boolean }[] = [];
  showHomeIcon = true;
  
  // Network Status
  isOnline: boolean = true;
  private networkSubscription!: Subscription;
  isNetworkModalOpen: boolean = false;

  constructor(
    private router: Router,
    private networkService: NetworkStatusService
  ) {}

  ngOnInit() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: any) => {
      this.updateBreadcrumbs(event.url);
    });
    
    // Set initial title
    this.updateBreadcrumbs(this.router.url);

    // Subscribe to network status
    this.networkSubscription = this.networkService.isOnline$.subscribe((status: boolean) => {
      this.isOnline = status;
      // Auto-close modal if connection is restored? 
      // Optional: if (status) this.isNetworkModalOpen = false;
    });
  }

  ngOnDestroy(): void {
    if (this.networkSubscription) {
      this.networkSubscription.unsubscribe();
    }
  }

  toggleNetworkModal(): void {
    this.isNetworkModalOpen = !this.isNetworkModalOpen;
  }
  
  closeNetworkModal(): void {
    this.isNetworkModalOpen = false;
  }

  retryConnection(): void {
    this.networkService.verifyInternetConnection();
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
    } else if (url.includes('maestros/proveedores') || url.includes('proveedores')) {
      this.breadcrumbItems = [
        { label: 'Maestros', active: false },
        { label: 'Proveedores', active: true }
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
