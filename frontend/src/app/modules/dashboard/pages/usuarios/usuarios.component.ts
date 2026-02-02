import { Component, OnInit } from '@angular/core';
import { UsuarioService } from '../../../../services/usuario.service';

@Component({
  selector: 'app-usuarios',
  templateUrl: './usuarios.component.html',
  styleUrls: ['./usuarios.component.css']
})
export class UsuariosComponent implements OnInit {
  
  // Updated model based on user image
  usuarios: any[] = [];

  filteredUsuarios: any[] = [];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Modal Logic
  isModalOpen: boolean = false;
  isEditMode: boolean = false;
  currentUserId: number | null = null;
  showModalClave: boolean = false;
  
  // Delete Modal Logic
  isDeleteModalOpen: boolean = false;
  itemToDelete: any = null;

  // Toast Logic
  errorMessage: string = '';
  successMessage: string = '';

  newUsuario = {
    nombres: '',
    apellidos: '',
    correo: '',
    clave: '',
    rol: '', // Default empty for 'Seleccionar' placeholder
    notificaciones: true,
    estado: true
  };

  constructor(private usuarioService: UsuarioService) { }

  ngOnInit(): void {
    this.loadUsuarios();
  }

  loadUsuarios(): void {
    this.usuarioService.getAll().subscribe({
      next: (data) => {
        this.usuarios = data.map(u => ({
          id: u.iMusuario,
          nombres: u.tNombre,
          apellidos: u.tApellidos,
          nombreCompleto: `${u.tNombre} ${u.tApellidos}`,
          correo: u.tCorreo,
          clave: u.tClave,
          rol: u.iMRol === 1 ? 'Administrador' : 'Usuario', // TODO: Fetch roles dynamically if needed
          notificaciones: u.lNotificacion,
          estado: u.lActivo,
          showClave: false
        }));
        this.filterData();
      },
      error: (err) => {
        console.error('Error loading usuarios:', err);
      }
    });
  }

  openModal(user?: any): void {
    this.isModalOpen = true;
    if (user) {
      this.isEditMode = true;
      this.currentUserId = user.id;
      this.newUsuario = {
        nombres: user.nombres,
        apellidos: user.apellidos,
        correo: user.correo,
        clave: '', // Leave empty to not change
        rol: user.rol,
        notificaciones: user.notificaciones,
        estado: user.estado
      };
    } else {
      this.isEditMode = false;
      this.currentUserId = null;
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
    }
    this.showModalClave = false;
  }

  closeModal(): void {
    this.isModalOpen = false;
    this.isEditMode = false;
    this.currentUserId = null;
  }

  toggleClaveVisibility(item: any): void {
    item.showClave = !item.showClave;
  }
  
  toggleModalClave(): void {
    this.showModalClave = !this.showModalClave;
  }

  saveUsuario(): void {
    // 1. Validar campos obligatorios
    // Password is only required for new users
    if (!this.newUsuario.nombres || !this.newUsuario.apellidos || !this.newUsuario.correo || !this.newUsuario.rol) {
        this.showError('Por favor complete los campos obligatorios (Nombres, Apellidos, Correo, Rol).');
        return;
    }

    if (!this.isEditMode && !this.newUsuario.clave) {
        this.showError('La contraseña es obligatoria para nuevos usuarios.');
        return;
    }

    // 2. Validar formato de correo (debe tener @)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    // Simple check as requested: "debe de tener (@)" - but standard regex is safer.
    // However, sticking to strict request: must have '@'.
    // If I use standard regex, it covers '@'.
    if (!this.newUsuario.correo.includes('@')) {
         this.showError('El correo electrónico debe contener el símbolo "@".');
         return;
    }
    // Optional: More strict email validation
    if (!emailRegex.test(this.newUsuario.correo)) {
         this.showError('Por favor ingrese un correo electrónico válido.');
         return;
    }

    // 3. Validar complejidad de contraseña (solo si se proporciona)
    if (this.newUsuario.clave) {
        // Min 8 chars, 1 uppercase, 1 symbol
        const minLength = 8;
        const hasUpperCase = /[A-Z]/.test(this.newUsuario.clave);
        const hasSymbol = /[!@#$%^&*(),.?":{}|<>]/.test(this.newUsuario.clave); // Common symbols

        if (this.newUsuario.clave.length < minLength) {
            this.showError('La contraseña debe tener al menos 8 caracteres.');
            return;
        }
        if (!hasUpperCase) {
            this.showError('La contraseña debe tener al menos una letra mayúscula.');
            return;
        }
        if (!hasSymbol) {
            this.showError('La contraseña debe tener al menos un símbolo (ej. !@#$%).');
            return;
        }
    }

    const payload = {
        tNombre: this.newUsuario.nombres,
        tApellidos: this.newUsuario.apellidos,
        tCorreo: this.newUsuario.correo,
        tClave: this.newUsuario.clave,
        iMRol: this.newUsuario.rol === 'Administrador' ? 1 : 2,
        lNotificacion: this.newUsuario.notificaciones,
        lActivo: this.newUsuario.estado
    };

    if (this.isEditMode && this.currentUserId) {
        this.usuarioService.update(this.currentUserId, payload).subscribe({
            next: (res) => {
                console.log('Usuario actualizado', res);
                this.showSuccess('Usuario actualizado correctamente.');
                this.loadUsuarios();
                this.closeModal();
            },
            error: (err) => {
                console.error('Error actualizando usuario', err);
                this.showError('Error al actualizar usuario: ' + (err.error?.detail || err.message));
            }
        });
    } else {
        this.usuarioService.create(payload).subscribe({
            next: (res) => {
                console.log('Usuario creado', res);
                this.showSuccess('Usuario creado correctamente.');
                this.loadUsuarios();
                this.closeModal();
            },
            error: (err) => {
                console.error('Error creando usuario', err);
                this.showError('Error al crear usuario: ' + (err.error?.detail || err.message));
            }
        });
    }
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

  openDeleteModal(item: any): void {
    this.itemToDelete = item;
    this.isDeleteModalOpen = true;
  }

  closeDeleteModal(): void {
    this.isDeleteModalOpen = false;
    this.itemToDelete = null;
  }

  confirmDelete(): void {
    if (!this.itemToDelete) return;
    
    this.usuarioService.delete(this.itemToDelete.id).subscribe({
      next: () => {
        console.log(`User ${this.itemToDelete.nombreCompleto} deleted`);
        this.showSuccess('Usuario eliminado correctamente.');
        this.loadUsuarios(); // Reload data from server
        this.closeDeleteModal();
      },
      error: (err) => {
        console.error('Error deleting user:', err);
        this.showError('Error al eliminar usuario.');
        this.closeDeleteModal();
      }
    });
  }

  showError(message: string) {
    this.successMessage = '';
    this.errorMessage = message;
    this.triggerToastTimeout();
  }

  showSuccess(message: string) {
    this.errorMessage = '';
    this.successMessage = message;
    this.triggerToastTimeout();
  }

  triggerToastTimeout() {
    setTimeout(() => {
      this.errorMessage = '';
      this.successMessage = '';
    }, 4000);
  }
}
