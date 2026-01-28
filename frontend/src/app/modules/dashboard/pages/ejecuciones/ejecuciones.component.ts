import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-ejecuciones',
  templateUrl: './ejecuciones.component.html',
  styleUrls: ['./ejecuciones.component.css']
})
export class EjecucionesComponent implements OnInit {
  
  // Dummy data for the table based on image
  ejecuciones = [
    {
      id: 1,
      nombre: 'SERVICIOS LOGISTICOS PERU S.A.',
      ruc: '20100123456',
      ultimaEjecucion: '21/01/2026 • 18:29',
      totalEjecuciones: 10,
      listaBlanca: 6,
      listaBlancaTotal: 10,
      estado: 'Ejecutar',
      activas: [
        { 
          nombre: 'Sincronización Nocturna SAP', 
          tipo: 'Programación', 
          detalle: 'Prog.: 10:58 - Lunes', 
          progreso: 45,
          logs: [
            { fecha: '21/01/2026 - 13:47', configuracion: 'Validación de Credenciales SOL', estado: 'Completado' },
            { fecha: '21/01/2026 - 13:47', configuracion: 'Extracción de movimientos del día', estado: 'Proceso ...' },
            { fecha: '21/01/2026 - 13:48', configuracion: 'Generación de reporte XML', estado: 'Pendiente' }
          ]
        },
        { 
          nombre: 'Procesamiento Manual', 
          tipo: 'Manual', 
          detalle: 'Disp: 2026-01-22', 
          progreso: 45,
          logs: []
        }
      ],
      historial: [
        { 
          fecha: '22/01/2026 • 14:27', 
          nombre: 'Sincronización Nocturna SAP', 
          tipo: 'Programación', 
          detalle: 'Prog.: 10:58 - Lunes',
          logs: [
            { fecha: '21/01/2026 - 13:47', configuracion: 'Validación de Credenciales SOL', estado: 'Completado' },
            { fecha: '21/01/2026 - 13:47', configuracion: 'Extracción de movimientos del día', estado: 'Fallido' }
          ]
        },
        { fecha: '21/01/2026 • 09:30', nombre: 'Reporte Mensual', tipo: 'Manual', detalle: 'Usuario: Admin' }
      ]
    },
    {
      id: 2,
      nombre: 'COSAPI S.A.',
      ruc: '20100017491',
      ultimaEjecucion: '22/01/2026 • 10:15',
      totalEjecuciones: 45,
      listaBlanca: 45,
      listaBlancaTotal: 45,
      estado: 'Procesando',
      activas: [
        { nombre: 'Validación de Facturas', tipo: 'Automático', detalle: 'Lote #4592', progreso: 78 }
      ],
      historial: [
        { fecha: '21/01/2026 • 18:00', nombre: 'Cierre Diario', tipo: 'Programación', detalle: 'Automático' },
        { fecha: '20/01/2026 • 18:00', nombre: 'Cierre Diario', tipo: 'Programación', detalle: 'Automático' }
      ]
    },
    {
      id: 3,
      nombre: 'SERVICIOS COMPLETOS PERU S.A',
      ruc: '20555888999',
      ultimaEjecucion: '20/01/2026 • 08:00',
      totalEjecuciones: 12,
      listaBlanca: 10,
      listaBlancaTotal: 12,
      estado: 'Ejecutar',
      activas: [],
      historial: [
        { fecha: '19/01/2026 • 15:30', nombre: 'Auditoría Interna', tipo: 'Manual', detalle: 'Solicitado por Gerencia' }
      ]
    },
    {
      id: 4,
      nombre: 'INVERSIONES GENERALES S.A.C.',
      ruc: '20601234567',
      ultimaEjecucion: '23/01/2026 • 11:20',
      totalEjecuciones: 5,
      listaBlanca: 5,
      listaBlancaTotal: 5,
      estado: 'Ejecutar',
      activas: [
        { nombre: 'Actualización de Inventario', tipo: 'Programación', detalle: 'Semanal', progreso: 12 }
      ],
      historial: []
    }
  ];

  filteredEjecuciones = [...this.ejecuciones];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  constructor() { }

  ngOnInit(): void {
  }

  filterData(): void {
    this.filteredEjecuciones = this.ejecuciones.filter(item => {
      const matchesSearch = item.nombre.toLowerCase().includes(this.searchTerm.toLowerCase());
      const matchesStatus = this.selectedStatus === 'TODOS' || item.estado === this.selectedStatus;
      return matchesSearch && matchesStatus;
    });
  }

  onSearch(event: any): void {
    this.searchTerm = event.target.value;
    this.filterData();
  }

  onStatusChange(event: any): void {
    this.selectedStatus = event.target.value;
    this.filterData();
  }

  getStatusClass(estado: string): string {
    switch (estado) {
      case 'Ejecutar': return 'status-running';
      case 'Procesando': return 'status-processing';
      default: return '';
    }
  }

  // Drawer Logic
  isDrawerOpen = false;
  selectedExecution: any = null;

  openDrawer(item: any): void {
    this.selectedExecution = item;
    this.isDrawerOpen = true;
    // Prevent body scroll when drawer is open
    document.body.style.overflow = 'hidden';
  }

  closeDrawer(): void {
    this.isDrawerOpen = false;
    this.selectedExecution = null;
    // Restore body scroll
    document.body.style.overflow = 'auto';
  }

  // Logs Modal Logic
  isLogModalOpen = false;
  selectedLogTask: any = null;

  openLogModal(task: any, event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.selectedLogTask = task;
    this.isLogModalOpen = true;
  }

  closeLogModal(): void {
    this.isLogModalOpen = false;
    this.selectedLogTask = null;
  }
}

