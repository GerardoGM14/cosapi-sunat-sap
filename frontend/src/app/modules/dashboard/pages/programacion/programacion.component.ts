import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfigService } from '../../../../services/app-config.service';

interface Sociedad {
  id: string; // tCodigoSap or tRuc
  name: string; // tRazonSocial
  ruc: string; // tRuc
  tUsuario?: string; // SUNAT user
  tClave?: string; // SUNAT pass
  selected: boolean;
  hasSunatCredentials: boolean;
  sapAccounts: any[];
  selectedSapAccount?: any;
  loadingSap?: boolean;
}

@Component({
  selector: 'app-programacion',
  templateUrl: './programacion.component.html',
  styleUrls: ['./programacion.component.css']
})
export class ProgramacionComponent implements OnInit {
  
  // Data will be loaded from backend
  programaciones: any[] = [];

  filteredProgramaciones: any[] = [];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Modal Logic
  isModalOpen: boolean = false;
  isDeleteModalOpen: boolean = false;
  isConfirmModalOpen: boolean = false;
  itemToDelete: any = null;
  pendingPayload: any = null;
  pendingSociedadesDisplay: any[] = [];
  
  newProgramacion = {
    nombre: '',
    hora: '',
    dias: [
      { label: 'L', selected: true },
      { label: 'M', selected: false },
      { label: 'M', selected: true },
      { label: 'J', selected: true },
      { label: 'V', selected: false },
      { label: 'S', selected: false },
      { label: 'D', selected: true }
    ]
  };

  sociedadesList: Sociedad[] = [];

  societySearchTerm: string = '';
  showSocietySearch: boolean = false;
  selectedSocietiesCount: number = 0;

  // Time Picker Logic
  isTimePickerOpen: boolean = false;
  hours: string[] = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));
  minutes: string[] = Array.from({ length: 12 }, (_, i) => (i * 5).toString().padStart(2, '0'));
  selectedHour: string = '00';
  selectedMinute: string = '00';

  // Toast Logic
  errorMessage: string = '';
  successMessage: string = '';

  constructor(private http: HttpClient, private configService: AppConfigService) { }

  ngOnInit(): void {
    this.loadSociedades();
    this.loadProgramaciones();
  }

  loadProgramaciones() {
    this.http.get<any[]>(`${this.configService.apiUrl}/crud/programacion`)
      .subscribe({
        next: (data) => {
          this.programaciones = data.map(p => ({
            id: p.iMProgramacion,
            nombre: p.tNombre,
            hora: p.tHora,
            dias: p.tDias,
            sociedades: p.iSociedadesCount,
            estado: p.lActivo
          }));
          this.filteredProgramaciones = [...this.programaciones];
          this.filterData(); // Apply any existing filters
        },
        error: (err) => console.error('Error loading programaciones', err)
      });
  }

  loadSociedades() {
    this.http.get<any[]>(`${this.configService.apiUrl}/crud/sociedades`)
      .subscribe({
        next: (data) => {
          this.sociedadesList = data.map(s => ({
            id: s.tCodigoSap || s.tRuc,
            name: s.tRazonSocial,
            ruc: s.tRuc,
            tUsuario: s.tUsuario,
            tClave: s.tClave,
            selected: false,
            hasSunatCredentials: !!(s.tUsuario && s.tClave),
            sapAccounts: [],
            loadingSap: false
          }));
        },
        error: (err) => console.error('Error loading sociedades', err)
      });
  }

  get filteredSocieties() {
    return this.sociedadesList.filter(s => 
      s.name.toLowerCase().includes(this.societySearchTerm.toLowerCase()) || 
      s.id.includes(this.societySearchTerm)
    );
  }

  toggleSocietySearch(): void {
    this.showSocietySearch = !this.showSocietySearch;
    if (!this.showSocietySearch) {
      this.societySearchTerm = '';
    }
  }

  toggleTimePicker(): void {
    this.isTimePickerOpen = !this.isTimePickerOpen;
  }

  selectHour(h: string): void {
    this.selectedHour = h;
    this.updateTime();
  }

  selectMinute(m: string): void {
    this.selectedMinute = m;
    this.updateTime();
    this.isTimePickerOpen = false;
  }

  updateTime(): void {
    this.newProgramacion.hora = `${this.selectedHour}:${this.selectedMinute}`;
  }

  openModal(): void {
    this.isModalOpen = true;
    // Initialize time picker with current time or existing value
    if (this.newProgramacion.hora) {
      const parts = this.newProgramacion.hora.split(':');
      if (parts.length === 2) {
        this.selectedHour = parts[0];
        this.selectedMinute = parts[1];
      }
    } else {
      const now = new Date();
      this.selectedHour = now.getHours().toString().padStart(2, '0');
      const roundedMinutes = Math.floor(now.getMinutes() / 5) * 5;
      this.selectedMinute = roundedMinutes.toString().padStart(2, '0');
      this.updateTime();
    }
  }

  closeModal(): void {
    this.isModalOpen = false;
  }

  toggleDay(index: number): void {
    this.newProgramacion.dias[index].selected = !this.newProgramacion.dias[index].selected;
  }

  toggleSociety(soc: Sociedad): void {
    soc.selected = !soc.selected;
    this.updateSelectedCount();
    if (soc.selected) {
        this.loadSapAccounts(soc);
    }
  }

  updateSelectedCount(): void {
    this.selectedSocietiesCount = this.sociedadesList.filter(s => s.selected).length;
  }

  loadSapAccounts(soc: Sociedad) {
      soc.loadingSap = true;
      this.http.get<any[]>(`${this.configService.apiUrl}/crud/sociedades/${soc.ruc}/sap-accounts`)
          .subscribe({
              next: (accounts) => {
                  soc.sapAccounts = accounts;
                  if (accounts.length > 0) {
                      soc.selectedSapAccount = accounts[0]; // Auto-select first or logic
                  }
                  soc.loadingSap = false;
              },
              error: (err) => {
                  console.error('Error loading SAP accounts', err);
                  soc.loadingSap = false;
              }
          });
  }

  getSelectedSocietiesCount(): number {
    return this.sociedadesList.filter(s => s.selected).length;
  }

  preSaveProgramacion(): void {
    console.log('Pre-guardando programación...', this.newProgramacion);

    // Validation
    if (!this.newProgramacion.nombre.trim()) {
      this.showError('Faltan completar campos: Nombre de la programación');
      return;
    }

    if (!this.newProgramacion.hora) {
      this.showError('Faltan completar campos: Hora de ejecución');
      return;
    }

    const hasSelectedDays = this.newProgramacion.dias.some(d => d.selected);
    if (!hasSelectedDays) {
      this.showError('Faltan completar campos: Seleccione al menos un día');
      return;
    }

    const hasSelectedSocieties = this.sociedadesList.some(s => s.selected);
    if (!hasSelectedSocieties) {
      this.showError('Faltan completar campos: Seleccione al menos una sociedad');
      return;
    }
    
    // Better mapping based on index
    const daysMap = ['Lun', 'Mar', 'Mier', 'Juev', 'Vier', 'Sab', 'Dom'];
    const activeDays = this.newProgramacion.dias
        .map((d, index) => d.selected ? daysMap[index] : null)
        .filter(d => d !== null) as string[];

    const selectedRucs = this.sociedadesList
        .filter(s => s.selected)
        .map(s => s.ruc);

    this.pendingSociedadesDisplay = this.sociedadesList
        .filter(s => s.selected)
        .map(s => ({ 
            ruc: s.ruc, 
            name: s.name,
            codeSociedad: s.id,
            sunatUser: s.tUsuario,
            sunatPass: s.tClave,
            sapUser: s.selectedSapAccount?.tUsuario,
            sapPass: s.selectedSapAccount?.tClave
        }));

    this.pendingPayload = {
        tNombre: this.newProgramacion.nombre || 'Nueva Programación',
        tHora: `${this.selectedHour}:${this.selectedMinute}`,
        tDias: activeDays,
        sociedades: selectedRucs,
        lActivo: true
    };
    
    this.isConfirmModalOpen = true;
  }

  closeConfirmModal(): void {
    this.isConfirmModalOpen = false;
    this.pendingPayload = null;
    this.pendingSociedadesDisplay = [];
  }

  confirmSaveProgramacion(): void {
    if (!this.pendingPayload) return;

    this.http.post<any>(`${this.configService.apiUrl}/crud/programacion`, this.pendingPayload)
        .subscribe({
            next: (resp) => {
                console.log('Programación creada', resp);
                this.loadProgramaciones(); // Reload list
                this.closeConfirmModal(); // Close confirm modal
                this.closeModal(); // Close create modal
                this.resetForm();
            },
            error: (err) => console.error('Error creando programación', err)
        });
  }

  resetForm(): void {
    this.newProgramacion = {
        nombre: '',
        hora: '',
        dias: [
          { label: 'L', selected: true },
          { label: 'M', selected: false },
          { label: 'M', selected: true },
          { label: 'J', selected: true },
          { label: 'V', selected: false },
          { label: 'S', selected: false },
          { label: 'D', selected: true }
        ]
    };
    // Reset societies selection
    this.sociedadesList.forEach(s => {
        s.selected = false;
        s.selectedSapAccount = undefined;
    });
    this.selectedSocietiesCount = 0;
    this.selectedHour = '00';
    this.selectedMinute = '00';
  }

  openDeleteModal(item: any): void {
    this.isDeleteModalOpen = true;
    this.itemToDelete = item;
  }

  closeDeleteModal(): void {
    this.isDeleteModalOpen = false;
    this.itemToDelete = null;
  }

  confirmDelete(): void {
    if (this.itemToDelete) {
      this.http.delete(`${this.configService.apiUrl}/crud/programacion/${this.itemToDelete.id}`)
        .subscribe({
            next: () => {
                console.log('Programación eliminada exitosamente');
                this.loadProgramaciones(); // Reload list
                this.closeDeleteModal();
            },
            error: (err) => {
                console.error('Error eliminando programación', err);
                // Optionally show user error
                this.closeDeleteModal();
            }
        });
    }
  }

  filterData(): void {
    this.filteredProgramaciones = this.programaciones.filter(item => {
      const matchesSearch = item.nombre.toLowerCase().includes(this.searchTerm.toLowerCase());
      
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
    // Optimistic update
    const previousState = item.estado;
    item.estado = !item.estado;

    this.http.put(`${this.configService.apiUrl}/crud/programacion/${item.id}/toggle`, {})
        .subscribe({
            next: (resp: any) => {
                console.log(`Status toggled for ${item.nombre}: ${resp.lActivo}`);
                item.estado = resp.lActivo; // Ensure sync with backend
            },
            error: (err) => {
                console.error('Error toggling status', err);
                item.estado = previousState; // Revert on error
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
