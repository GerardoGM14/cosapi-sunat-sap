import { Component, OnInit } from '@angular/core';
import { ProveedorService } from '../../../../services/proveedor.service';
import { SociedadService } from '../../../../services/sociedad.service';

@Component({
  selector: 'app-proveedores',
  templateUrl: './proveedores.component.html',
  styleUrls: ['./proveedores.component.css']
})
export class ProveedoresComponent implements OnInit {
  
  // Updated model for Proveedores
  proveedores: any[] = [];
  sociedades: any[] = []; // List of all societies

  filteredProveedores: any[] = [];
  paginatedProveedores: any[] = []; // Displayed data
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Pagination
  currentPage: number = 1;
  itemsPerPage: number = 10;
  totalPages: number = 0;
  totalItems: number = 0;

  // Modal Logic
  isModalOpen: boolean = false;
  isEditMode: boolean = false;
  
  // Delete Modal Logic
  isDeleteModalOpen: boolean = false;
  itemToDelete: any = null;

  // Sociedades Modal Logic
  isSociedadesModalOpen: boolean = false;
  currentProveedor: any = null;
  selectedSociedades: Set<string> = new Set();
  
  // Sociedades Filter
  sociedadSearchTerm: string = '';
  filteredSociedadesList: any[] = [];
  
  newProveedor = {
    ruc: '',
    razonSocial: '',
    estado: true
  };

  constructor(
    private proveedorService: ProveedorService,
    private sociedadService: SociedadService
  ) { }

  isPreviewModalOpen = false;
  previewData: any[] = [];
  
  // Loader and Toast State
  isLoading = false;
  loadingTimeout: any;
  successMessage = '';
  errorMessage = '';

  triggerToastTimeout() {
    setTimeout(() => {
      this.errorMessage = '';
      this.successMessage = '';
    }, 4000);
  }

  ngOnInit(): void {
    this.loadSociedades();
  }

  loadSociedades(): void {
    this.sociedadService.getAll().subscribe({
      next: (data) => {
        this.sociedades = data.filter(s => s.lActivo); // Only active societies
        this.filteredSociedadesList = [...this.sociedades];
        this.loadProveedores();
      },
      error: (err) => {
        console.error('Error cargando sociedades', err);
        this.loadProveedores();
      }
    });
  }

  loadProveedores(): void {
    this.proveedorService.getProveedores().subscribe({
      next: (data) => {
        this.proveedores = data.map(item => ({
          id: item.tRucListaBlanca, // Use RUC as ID
          ruc: item.tRucListaBlanca,
          razonSocial: item.tRazonSocial,
          estado: item.lActivo,
          sociedadesRucs: item.sociedades_rucs || [],
          sociedadesCount: (item.sociedades_rucs || []).length,
          totalSociedades: this.sociedades.length
        }));
        this.filterData();
      },
      error: (err) => {
        console.error('Error cargando proveedores', err);
        this.errorMessage = 'Error cargando proveedores: ' + (err.error?.detail || err.message);
        this.triggerToastTimeout();
      }
    });
  }

  onFileSelected(event: any): void {
    const file: File = event.target.files[0];
    if (file) {
      this.proveedorService.previewExcel(file).subscribe({
        next: (data: any[]) => {
          this.previewData = data;
          this.isPreviewModalOpen = true;
          // Reset file input
          event.target.value = '';
        },
        error: (err: any) => {
          console.error('Preview error', err);
          this.errorMessage = 'Error al leer el archivo: ' + (err.error?.detail || err.message);
          this.triggerToastTimeout();
          event.target.value = '';
        }
      });
    }
  }

  confirmUpload(): void {
    // Map preview data to backend expected format
    const payload = this.previewData.map(item => ({
      tRucListaBlanca: item.ruc,
      tRazonSocial: item.razonSocial,
      lActivo: true // Managed by system as per requirement
    }));

    // Start loader timer (2 seconds delay)
    // this.loadingTimeout = setTimeout(() => {
    //   this.isLoading = true;
    // }, 2000);

    this.proveedorService.importBatch(payload).subscribe({
      next: (res: any) => {
        // clearTimeout(this.loadingTimeout);
        // this.isLoading = false;

        this.successMessage = `Importación completada: ${res.created} creados, ${res.updated} actualizados.`;
        this.triggerToastTimeout();
        this.closePreviewModal();
        this.loadProveedores();
      },
      error: (err: any) => {
        // clearTimeout(this.loadingTimeout);
        // this.isLoading = false;

        console.error('Import error', err);
        this.errorMessage = 'Error al importar datos: ' + (err.error?.detail || err.message);
        this.triggerToastTimeout();
      }
    });
  }

  closePreviewModal(): void {
    this.isPreviewModalOpen = false;
    this.previewData = [];
  }

  openModal(item: any = null): void {
    this.isModalOpen = true;
    if (item) {
      this.isEditMode = true;
      this.newProveedor = {
        ruc: item.ruc,
        razonSocial: item.razonSocial,
        estado: item.estado
      };
    } else {
      this.isEditMode = false;
      this.newProveedor = {
        ruc: '',
        razonSocial: '',
        estado: true
      };
    }
  }

  closeModal(): void {
    this.isModalOpen = false;
  }

  openSociedadesModal(item: any): void {
    this.currentProveedor = item;
    this.selectedSociedades = new Set(item.sociedadesRucs);
    this.sociedadSearchTerm = '';
    this.filteredSociedadesList = [...this.sociedades];
    this.isSociedadesModalOpen = true;
  }

  closeSociedadesModal(): void {
    this.isSociedadesModalOpen = false;
    this.currentProveedor = null;
    this.selectedSociedades.clear();
    this.sociedadSearchTerm = '';
  }

  onSociedadSearch(event: any): void {
    this.sociedadSearchTerm = event.target.value;
    if (!this.sociedadSearchTerm) {
      this.filteredSociedadesList = [...this.sociedades];
    } else {
      const term = this.sociedadSearchTerm.toLowerCase();
      this.filteredSociedadesList = this.sociedades.filter(s => 
        s.tRazonSocial.toLowerCase().includes(term) || 
        s.tRuc.includes(term)
      );
    }
  }

  toggleSociedadSelection(ruc: string): void {
    if (this.selectedSociedades.has(ruc)) {
      this.selectedSociedades.delete(ruc);
    } else {
      this.selectedSociedades.add(ruc);
    }
  }
  
  isSociedadSelected(ruc: string): boolean {
    return this.selectedSociedades.has(ruc);
  }

  saveSociedades(): void {
    if (!this.currentProveedor) return;

    const selectedRucs = Array.from(this.selectedSociedades);
    this.isLoading = true;
    
    this.proveedorService.updateSociedades(this.currentProveedor.ruc, selectedRucs).subscribe({
      next: () => {
        this.isLoading = false;
        this.successMessage = 'Lista blanca actualizada correctamente.';
        this.triggerToastTimeout();
        this.closeSociedadesModal();
        this.loadProveedores();
      },
      error: (err) => {
        this.isLoading = false;
        console.error('Error updating sociedades', err);
        this.errorMessage = 'Error al actualizar lista blanca: ' + (err.error?.detail || err.message);
        this.triggerToastTimeout();
      }
    });
  }

  toggleStatus(item: any): void {
    item.estado = !item.estado;
    // TODO: Call backend to update status immediately if required
  }

  saveProveedor(): void {
    if (!this.newProveedor.ruc || !this.newProveedor.razonSocial) {
      this.errorMessage = 'Por favor complete todos los campos obligatorios.';
      this.triggerToastTimeout();
      return;
    }

    const payload = [{
      tRucListaBlanca: this.newProveedor.ruc,
      tRazonSocial: this.newProveedor.razonSocial,
      lActivo: this.newProveedor.estado
    }];

    this.isLoading = true;
    this.proveedorService.importBatch(payload).subscribe({
      next: (res: any) => {
        this.isLoading = false;
        this.successMessage = this.isEditMode ? 'Proveedor actualizado correctamente.' : 'Proveedor creado correctamente.';
        this.triggerToastTimeout();
        this.closeModal();
        this.loadProveedores();
      },
      error: (err: any) => {
        this.isLoading = false;
        console.error('Error saving proveedor', err);
        this.errorMessage = 'Error al guardar proveedor: ' + (err.error?.detail || err.message);
        this.triggerToastTimeout();
      }
    });
  }

  filterData(): void {
    this.filteredProveedores = this.proveedores.filter(item => {
      const matchesSearch = item.razonSocial.toLowerCase().includes(this.searchTerm.toLowerCase()) || 
                            item.ruc.includes(this.searchTerm);
      
      const matchesStatus = this.selectedStatus === 'TODOS' || 
                            (this.selectedStatus === 'ACTIVO' ? item.estado : !item.estado);
      
      return matchesSearch && matchesStatus;
    });

    // Update pagination info
    this.totalItems = this.filteredProveedores.length;
    this.totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
    
    // Reset to page 1 if current page is out of bounds, unless it's 0 (no items)
    if (this.currentPage > this.totalPages && this.totalPages > 0) {
      this.currentPage = 1;
    }

    this.updatePagination();
  }

  updatePagination(): void {
    const startIndex = (this.currentPage - 1) * this.itemsPerPage;
    const endIndex = startIndex + this.itemsPerPage;
    this.paginatedProveedores = this.filteredProveedores.slice(startIndex, endIndex);
  }

  changePage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.updatePagination();
    }
  }

  onItemsPerPageChange(event: any): void {
    this.itemsPerPage = Number(event.target.value);
    this.currentPage = 1;
    this.filterData(); // Recalculate pages
  }

  onSearch(event: any): void {
    this.searchTerm = event.target.value;
    this.currentPage = 1; // Reset to first page on search
    this.filterData();
  }

  onStatusChange(event: any): void {
    this.selectedStatus = event.target.value;
    this.currentPage = 1; // Reset to first page on filter change
    this.filterData();
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
    if (this.itemToDelete) {
      this.isLoading = true;
      this.proveedorService.deleteProveedor(this.itemToDelete.ruc).subscribe({
        next: (res) => {
          this.isLoading = false;
          this.successMessage = 'Proveedor eliminado correctamente.';
          this.triggerToastTimeout();
          this.closeDeleteModal();
          this.loadProveedores();
        },
        error: (err) => {
          this.isLoading = false;
          console.error('Error deleting proveedor', err);
          this.errorMessage = 'Error al eliminar proveedor: ' + (err.error?.detail || err.message);
          this.triggerToastTimeout();
          this.closeDeleteModal();
        }
      });
    }
  }
}
