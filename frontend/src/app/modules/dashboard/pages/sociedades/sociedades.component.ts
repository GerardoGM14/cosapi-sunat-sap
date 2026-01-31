import { Component, OnInit } from '@angular/core';
import { SociedadService } from '../../../../services/sociedad.service';

@Component({
  selector: 'app-sociedades',
  templateUrl: './sociedades.component.html',
  styleUrls: ['./sociedades.component.css']
})
export class SociedadesComponent implements OnInit {
  
  programaciones: any[] = [];
  filteredProgramaciones: any[] = [];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Modal Logic
  isModalOpen: boolean = false;
  showModalClave: boolean = false;
  isEditMode: boolean = false; // Track if we are editing
  currentRucToEdit: string = ''; // Store the original RUC for updates

  // Delete Modal Logic
  isDeleteModalOpen: boolean = false;
  itemToDelete: any = null;

  // Toast Logic
  errorMessage: string = '';
  successMessage: string = '';

  newProgramacion = {
    ruc: '',
    razonSocial: '',
    usuarioSunat: '',
    claveSol: '',
    estado: true
  };

  constructor(private sociedadService: SociedadService) { }

  ngOnInit(): void {
    this.loadSociedades();
  }

  loadSociedades(): void {
    this.sociedadService.getAll().subscribe({
      next: (data) => {
        this.programaciones = data.map(item => ({
          id: item.tRuc, // Use RUC as ID
          ruc: item.tRuc,
          razonSocial: item.tRazonSocial,
          usuarioSunat: item.tUsuario,
          claveSol: item.tClave,
          estado: item.lActivo,
          showClave: false
        }));
        this.filterData();
      },
      error: (err) => console.error('Error loading sociedades:', err)
    });
  }

  openModal(): void {
    this.isEditMode = false;
    this.isModalOpen = true;
    this.newProgramacion = {
      ruc: '',
      razonSocial: '',
      usuarioSunat: '',
      claveSol: '',
      estado: true
    };
    this.showModalClave = false;
  }

  openEditModal(item: any): void {
    this.isEditMode = true;
    this.isModalOpen = true;
    this.currentRucToEdit = item.ruc;
    
    // Clone data to avoid direct mutation of table row before saving
    this.newProgramacion = {
      ruc: item.ruc,
      razonSocial: item.razonSocial,
      usuarioSunat: item.usuarioSunat,
      claveSol: item.claveSol,
      estado: item.estado
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

  validateRucInput(event: any): void {
    const input = event.target;
    const value = input.value;
    
    // Remove non-numeric characters
    const numericValue = value.replace(/[^0-9]/g, '');
    
    if (value !== numericValue) {
      this.newProgramacion.ruc = numericValue;
      input.value = numericValue;
    }
    
    // Truncate to 11 characters if somehow exceeded (though maxlength handles this)
    if (this.newProgramacion.ruc.length > 11) {
      this.newProgramacion.ruc = this.newProgramacion.ruc.slice(0, 11);
    }
  }

  isValidForm(): boolean {
    // Check for empty fields
    if (!this.newProgramacion.ruc || 
        !this.newProgramacion.razonSocial || 
        !this.newProgramacion.usuarioSunat || 
        !this.newProgramacion.claveSol) {
      this.showError('Todos los campos son obligatorios.');
      return false;
    }

    // Check RUC length
    if (this.newProgramacion.ruc.length !== 11) {
      this.showError('El RUC debe tener exactamente 11 dígitos.');
      return false;
    }

    return true;
  }

  saveProgramacion(): void {
    if (!this.isValidForm()) {
      return;
    }

    console.log('Guardando sociedad...', this.newProgramacion);
    
    // Map to backend format
    const payload = {
      tRuc: this.newProgramacion.ruc,
      tRazonSocial: this.newProgramacion.razonSocial,
      tUsuario: this.newProgramacion.usuarioSunat,
      tClave: this.newProgramacion.claveSol,
      lActivo: this.newProgramacion.estado
    };

    if (this.isEditMode) {
      // Update existing record
      this.sociedadService.update(this.currentRucToEdit, payload).subscribe({
        next: (res) => {
          console.log('Sociedad actualizada:', res);
          this.showSuccess('Sociedad actualizada correctamente.');
          this.loadSociedades(); // Refresh list
          this.closeModal();
        },
        error: (err) => {
          console.error('Error updating sociedad:', err);
          this.showError('Error al actualizar: ' + (err.error?.detail || err.message));
        }
      });
    } else {
      // Create new record
      this.sociedadService.create(payload).subscribe({
        next: (res) => {
          console.log('Sociedad creada:', res);
          this.showSuccess('Sociedad creada correctamente.');
          this.loadSociedades(); // Refresh list
          this.closeModal();
        },
        error: (err) => {
          console.error('Error creating sociedad:', err);
          this.showError('Error al guardar: ' + (err.error?.detail || err.message));
        }
      });
    }
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
    // Toggle locally first for UI responsiveness (optional, but better to wait for server)
    // Here we'll call server
    const newState = !item.estado;
    const payload = { lActivo: newState };

    this.sociedadService.update(item.ruc, payload).subscribe({
      next: (res) => {
        item.estado = newState;
        console.log(`Status updated for ${item.razonSocial}: ${item.estado}`);
      },
      error: (err) => {
        console.error('Error updating status:', err);
        // Revert if failed
        // item.estado = !newState; 
      }
    });
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

    this.sociedadService.delete(this.itemToDelete.ruc).subscribe({
      next: (res) => {
        console.log('Sociedad eliminada:', res);
        this.showSuccess('Sociedad eliminada correctamente.');
        this.loadSociedades(); // Refresh list
        this.closeDeleteModal();
      },
      error: (err) => {
        console.error('Error deleting sociedad:', err);
        this.showError('Error al eliminar: ' + (err.error?.detail || err.message));
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
