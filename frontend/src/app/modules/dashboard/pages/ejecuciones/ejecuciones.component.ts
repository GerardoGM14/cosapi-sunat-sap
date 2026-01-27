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
      ruc: '123456789',
      ultimaEjecucion: '21/01/2026 • 18:29',
      totalEjecuciones: 10,
      listaBlanca: 6,
      listaBlancaTotal: 10,
      estado: 'Ejecutando'
    },
    {
      id: 1,
      nombre: 'SERVICIOS LOGISTICOS PERU S.A.',
      ruc: '123456789',
      ultimaEjecucion: '21/01/2026 • 18:29',
      totalEjecuciones: 10,
      listaBlanca: 6,
      listaBlancaTotal: 10,
      estado: 'Procesando'
    },
    {
      id: 1,
      nombre: 'SERVICIOS LOGISTICOS PERU S.A.',
      ruc: '123456789',
      ultimaEjecucion: '21/01/2026 • 18:29',
      totalEjecuciones: 10,
      listaBlanca: 6,
      listaBlancaTotal: 10,
      estado: 'Ejecutando'
    },
    {
      id: 1,
      nombre: 'SERVICIOS LOGISTICOS PERU S.A.',
      ruc: '123456789',
      ultimaEjecucion: '21/01/2026 • 18:29',
      totalEjecuciones: 10,
      listaBlanca: 6,
      listaBlancaTotal: 10,
      estado: 'Ejecutando'
    }
  ];

  constructor() { }

  ngOnInit(): void {
  }

  getStatusClass(estado: string): string {
    switch (estado) {
      case 'Ejecutando': return 'status-running';
      case 'Procesando': return 'status-processing';
      default: return '';
    }
  }

}
