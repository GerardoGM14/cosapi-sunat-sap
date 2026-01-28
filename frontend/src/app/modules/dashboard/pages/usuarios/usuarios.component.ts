import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-usuarios',
  templateUrl: './usuarios.component.html',
  styleUrls: ['./usuarios.component.css']
})
export class UsuariosComponent implements OnInit {
  
  // Updated model based on user image
  usuarios = [
    {
      id: 1,
      nombreCompleto: 'Martín Alejandro García Pérez',
      correo: 'MARTIN.GARCÍA@GMAIL.COM',
      clave: '123456',
      rol: 'Administrador',
      notificaciones: true,
      estado: true,
      showClave: false
    },
    {
      id: 2,
      nombreCompleto: 'Martín Alejandro García Pérez',
      correo: 'MARTIN.GARCÍA@GMAIL.COM',
      clave: '123456',
      rol: 'Usuario',
      notificaciones: true,
      estado: true,
      showClave: false
    },
    {
      id: 3,
      nombreCompleto: 'Martín Alejandro García Pérez',
      correo: 'MARTIN.GARCÍA@GMAIL.COM',
      clave: '123456',
      rol: 'Usuario',
      notificaciones: false,
      estado: true,
      showClave: false
    }
  ];

  filteredUsuarios = [...this.usuarios];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Modal Logic
  isModalOpen: boolean = false;
  showModalClave: boolean = false;
  
  newUsuario = {
    nombres: '',
    apellidos: '',
    correo: '',
    clave: '',
    rol: '', // Default empty for 'Seleccionar' placeholder
    notificaciones: true,
    estado: true
  };

  constructor() { }

  ngOnInit(): void {
  }

  openModal(): void {
    this.isModalOpen = true;
    // Reset or initialize new entry
    this.newUsuario = {
      nombres: '',
      apellidos: '',
      correo: '',
      clave: '',
      rol: '',
      notificaciones: true,
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

  saveUsuario(): void {
    console.log('Guardando usuario...', this.newUsuario);
    this.closeModal();
  }

  filterData(): void {
    this.filteredUsuarios = this.usuarios.filter(item => {
      const matchesSearch = item.nombreCompleto.toLowerCase().includes(this.searchTerm.toLowerCase()) || 
                            item.correo.toLowerCase().includes(this.searchTerm.toLowerCase());
      
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
    console.log(`Status toggled for ${item.nombreCompleto}: ${item.estado}`);
  }
}
