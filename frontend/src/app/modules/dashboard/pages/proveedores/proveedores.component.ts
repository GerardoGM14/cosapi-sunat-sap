import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-proveedores',
  templateUrl: './proveedores.component.html',
  styleUrls: ['./proveedores.component.css']
})
export class ProveedoresComponent implements OnInit {
  
  // Updated model for Proveedores
  proveedores = [
    {
      id: 1,
      ruc: '123456789',
      razonSocial: 'PROVEEDORES LOGISTICOS PERU S.A.',
      listaBlanca: true,
      estado: true
    },
    {
      id: 2,
      ruc: '987654321',
      razonSocial: 'SERVICIOS GENERALES S.A.C.',
      listaBlanca: false,
      estado: true
    },
    {
      id: 3,
      ruc: '456123789',
      razonSocial: 'IMPORTACIONES Y EXPORTACIONES E.I.R.L.',
      listaBlanca: true,
      estado: true
    },
    {
      id: 4,
      ruc: '789123456',
      razonSocial: 'COMERCIALIZADORA DEL SUR S.A.',
      listaBlanca: true,
      estado: true
    },
    {
      id: 5,
      ruc: '321654987',
      razonSocial: 'DISTRIBUIDORA NORTE S.A.C.',
      listaBlanca: true,
      estado: true
    }
  ];

  filteredProveedores = [...this.proveedores];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Modal Logic
  isModalOpen: boolean = false;
  
  newProveedor = {
    ruc: '',
    razonSocial: '',
    listaBlanca: false,
    estado: true
  };

  constructor() { }

  ngOnInit(): void {
  }

  openModal(): void {
    this.isModalOpen = true;
    // Reset or initialize new entry
    this.newProveedor = {
      ruc: '',
      razonSocial: '',
      listaBlanca: false,
      estado: true
    };
  }

  closeModal(): void {
    this.isModalOpen = false;
  }

  toggleStatus(item: any): void {
    item.estado = !item.estado;
  }

  saveProveedor(): void {
    console.log('Guardando proveedor...', this.newProveedor);
    this.closeModal();
  }

  filterData(): void {
    this.filteredProveedores = this.proveedores.filter(item => {
      const matchesSearch = item.razonSocial.toLowerCase().includes(this.searchTerm.toLowerCase()) || 
                            item.ruc.includes(this.searchTerm);
      
      const matchesStatus = this.selectedStatus === 'TODOS' || 
                            (this.selectedStatus === 'ACTIVO' ? item.estado : !item.estado);
      
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
}
