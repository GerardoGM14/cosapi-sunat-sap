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
  
  newProgramacion = {
    ruc: '',
    razonSocial: '',
    usuarioSunat: '',
    claveSol: '',
    estado: true
  };

  constructor() { }

  ngOnInit(): void {
  }

  openModal(): void {
    this.isModalOpen = true;
    // Reset or initialize new entry
    this.newProgramacion = {
      ruc: '',
      razonSocial: '',
      usuarioSunat: '',
      claveSol: '',
      estado: true
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
