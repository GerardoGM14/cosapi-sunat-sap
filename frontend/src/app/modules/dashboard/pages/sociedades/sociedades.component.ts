import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-sociedades',
  templateUrl: './sociedades.component.html',
  styleUrls: ['./sociedades.component.css']
})
export class SociedadesComponent implements OnInit {
  
  // Dummy data adapted for Sociedades
  programaciones = [
    {
      id: 1,
      ruc: '20100017491',
      razonSocial: 'SERVICIOS LOGISTICOS PERU S.A.',
      usuarioSunat: 'MODDATOS',
      claveSol: 'moddatos',
      showClave: false,
      estado: true
    },
    {
      id: 2,
      ruc: '20100017492',
      razonSocial: 'COSAPI MINERIA S.A.C.',
      usuarioSunat: 'MODDATOS',
      claveSol: 'moddatos',
      showClave: false,
      estado: true
    },
    {
      id: 3,
      ruc: '20100017493',
      razonSocial: 'COSAPI INMOBILIARIA Y GRUPO',
      usuarioSunat: 'MODDATOS',
      claveSol: 'moddatos',
      showClave: false,
      estado: false
    },
    {
      id: 4,
      ruc: '20100017494',
      razonSocial: 'COSAPI DATA S.A.',
      usuarioSunat: 'MODDATOS',
      claveSol: 'moddatos',
      showClave: false,
      estado: true
    }
  ];

  filteredProgramaciones = [...this.programaciones];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Modal Logic
  isModalOpen: boolean = false;
  showModalClave: boolean = false;
  
  // Mock Providers for selection
  proveedorSearchTerm: string = '';
  availableProveedores = [
    { id: 1, ruc: '123456789', razonSocial: 'PROVEEDORES LOGISTICOS PERU S.A.' },
    { id: 2, ruc: '987654321', razonSocial: 'SERVICIOS GENERALES S.A.C.' },
    { id: 3, ruc: '456123789', razonSocial: 'IMPORTACIONES Y EXPORTACIONES E.I.R.L.' },
    { id: 4, ruc: '789123456', razonSocial: 'COMERCIALIZADORA DEL SUR S.A.' },
    { id: 5, ruc: '321654987', razonSocial: 'DISTRIBUIDORA NORTE S.A.C.' }
  ];

  get filteredProveedores() {
    if (!this.proveedorSearchTerm) {
      return this.availableProveedores;
    }
    const term = this.proveedorSearchTerm.toLowerCase();
    return this.availableProveedores.filter(p => 
      p.razonSocial.toLowerCase().includes(term) || 
      p.ruc.includes(term)
    );
  }

  newProgramacion = {
    ruc: '',
    razonSocial: '',
    usuarioSunat: '',
    claveSol: '',
    estado: true,
    proveedores: [] as number[] // Store IDs of selected providers
  };

  constructor() { }

  ngOnInit(): void {
  }

  openModal(): void {
    this.isModalOpen = true;
    // Reset or initialize new entry
    this.proveedorSearchTerm = '';
    this.newProgramacion = {
      ruc: '',
      razonSocial: '',
      usuarioSunat: '',
      claveSol: '',
      estado: true,
      proveedores: []
    };
    this.showModalClave = false;
  }

  closeModal(): void {
    this.isModalOpen = false;
  }

  toggleClaveVisibility(item: any): void {
    item.showClave = !item.showClave;
  }
  
  toggleModalClave(): void {
    this.showModalClave = !this.showModalClave;
  }

  toggleProveedorSelection(id: number): void {
    const index = this.newProgramacion.proveedores.indexOf(id);
    if (index === -1) {
      this.newProgramacion.proveedores.push(id);
    } else {
      this.newProgramacion.proveedores.splice(index, 1);
    }
  }

  saveProgramacion(): void {
    console.log('Guardando sociedad...', this.newProgramacion);
    this.closeModal();
  }

  filterData(): void {
    this.filteredProgramaciones = this.programaciones.filter(item => {
      const matchesSearch = item.razonSocial.toLowerCase().includes(this.searchTerm.toLowerCase()) || 
                            item.ruc.includes(this.searchTerm);
      
      let matchesStatus = true;
      if (this.selectedStatus === 'ACTIVO') {
        matchesStatus = item.estado === true;
      } else if (this.selectedStatus === 'INACTIVO') {
        matchesStatus = item.estado === false;
      }

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

  toggleStatus(item: any): void {
    item.estado = !item.estado;
    console.log(`Status toggled for ${item.razonSocial}: ${item.estado}`);
  }
}
