import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfigService } from '../../../../services/app-config.service';
import { SociedadService } from '../../../../services/sociedad.service';
import { ProveedorService } from '../../../../services/proveedor.service';
import { SocketService } from '../../../../services/socket.service';
import { Subscription } from 'rxjs';

const SAP_SOCIEDADES = [
    { id: 'PE01', name: 'PE01 - Country Template PE' },
    { id: 'PE02', name: 'PE02 - COSAPI S.A' },
    { id: 'PE03', name: 'PE03 - CSP. MINERIA S.A.C.' },
    { id: 'PE04', name: 'PE04 - CSP. GESTION INMB. S.A.C.' },
    { id: 'PE05', name: 'PE05 - COSAPI CONSORCIOS (HCM)' },
    { id: 'PE06', name: 'PE06 - CONSORCIO BELLAVISTA' },
    { id: 'PE07', name: 'PE07 - CONSORCIO COSAPI - JOHESA' },
    { id: 'PE08', name: 'PE08 - CONS VIAL CHONGOYAPE-LLAM' },
    { id: 'PE09', name: 'PE09 - CC. VIAL TAMBILLO' },
    { id: 'PE10', name: 'PE10 - CONS VIAL QUILCA MATARANI' },
    { id: 'PE11', name: 'PE11 - CONSORCIO VIAL OAS-COSAPI' },
    { id: 'PE12', name: 'PE12 - CC. COSAPI MAS ERRAZURIZ' },
    { id: 'PE13', name: 'PE13 - CSP. INMB. & DES. INMB' },
    { id: 'PE14', name: 'PE14 - CC. SADE - COSAPI' },
    { id: 'PE15', name: 'PE15 - INVERSION CD S.A.' },
    { id: 'PE16', name: 'PE16 - DRLLO. SALAVERRY S.A.C.' },
    { id: 'PE17', name: 'PE17 - DESARROLLO BELISARIO 1035' },
    { id: 'PE18', name: 'PE18 - CONSORCIO JJC-COSAPI' },
    { id: 'PE19', name: 'PE19 - CONSORCIO VIAL VIZCACHANE' },
    { id: 'PE20', name: 'PE20 - CSP. INMOBILIARIA S.A.' },
    { id: 'PE21', name: 'PE21 - CONSORCIO SEÑOR DE LUREN' },
    { id: 'PE22', name: 'PE22 - DESARROLLO SUCRE 132 S.A.' },
    { id: 'PE23', name: 'PE23 - CC. VIAL DEL SUR' },
    { id: 'PE24', name: 'PE24 - CC. PUENTES DE LORETO' },
    { id: 'PE25', name: 'PE25 - CONS HOTEL ATTON COSAPI' },
    { id: 'PE26', name: 'PE26 - DRLLO. OLGUIN S.A.C.' },
    { id: 'PE27', name: 'PE27 - CC. COSAPI - JJC-SC' },
    { id: 'PE28', name: 'PE28 - CC. BELFI-COSAPI PERU' },
    { id: 'PE29', name: 'PE29 - CONSORCIO NUEVO LIMATAMBO' },
    { id: 'PE30', name: 'PE30 - DRLLO. LINCE S.A.C.' },
    { id: 'PE31', name: 'PE31 - DRLLO. INMB. DERBY S.A.C.' },
    { id: 'PE32', name: 'PE32 - DRLLO. AGUARICO S.A.C.' },
    { id: 'PE33', name: 'PE33 - INTERANDES HOLDING S.A.' },
    { id: 'PE34', name: 'PE34 - CC. COSAPI - HV' },
    { id: 'PE35', name: 'PE35 - DESARROLLO BELLAVISTA SAC' },
    { id: 'PE36', name: 'PE36 - DESARROLLO LANCEROS SAC' },
    { id: 'PE37', name: 'PE37 - CONSORCIO R&H' },
    { id: 'PE38', name: 'PE38 - CONS CONSTRUCT PERU - CCP' },
    { id: 'PE39', name: 'PE39 - CONSORCIO CCMS' },
    { id: 'CL01', name: 'CL01 - Country Template CL' },
    { id: 'CL02', name: 'CL02 - COSAPI SA AGENCIA CHILE' },
    { id: 'CL03', name: 'CL03 - COSAPI CHILE SA' }
];

@Component({
  selector: 'app-ejecuciones',
  templateUrl: './ejecuciones.component.html',
  styleUrls: ['./ejecuciones.component.css']
})
export class EjecucionesComponent implements OnInit {
  
  ejecuciones: any[] = [];
  filteredEjecuciones: any[] = [];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Calendar Logic
  weekDays = ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'];
  months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  currentCalendarDate: Date = new Date();
  daysInMonth: any[] = [];
  activeCalendarRowId: number | null = null;

  // Params Modal Logic
  isParamsModalOpen = false;
  selectedParamsTask: any = null;
  isLoadingSap = false;
  showSunatPassword = false;
  showSapPassword = false;
  
  // UI Helpers
  // Images removed as per user request


  constructor(
    private http: HttpClient, 
    private configService: AppConfigService,
    private sociedadService: SociedadService,
    private proveedorService: ProveedorService,
    private socketService: SocketService,
    private cdr: ChangeDetectorRef
  ) {
    // Click outside listener for calendar
    document.addEventListener('click', (e: any) => {
        if (!e.target.closest('.custom-date-wrapper')) {
            this.activeCalendarRowId = null;
        }
    });
  }

  ngOnInit(): void {
    this.loadSociedades();
    this.loadWhitelistCount();
  }

  loadWhitelistCount(): void {
    this.proveedorService.getProveedores().subscribe({
      next: (data) => {
        // Filter providers that are active AND have at least one society linked
        const activeProviders = data.filter(p => p.lActivo && p.sociedades_rucs && p.sociedades_rucs.length > 0);
        this.globalWhitelist = activeProviders.map(p => ({
          ruc: p.tRucListaBlanca,
          razonSocial: p.tRazonSocial,
          sociedadesNombres: p.sociedades_nombres ? p.sociedades_nombres.join(', ') : ''
        }));
        this.filterWhitelist();
      },
      error: (err) => console.error('Error fetching whitelist count', err)
    });
  }

  loadSociedades(): void {
    const today = new Date();
    this.sociedadService.getAll().subscribe({
      next: (data) => {
        this.ejecuciones = data.map((item: any, index: number) => {
            // Find SAP Code if missing
            let codigoSap = item.tCodigoSap;
            if (!codigoSap && item.tRazonSocial) {
                const found = SAP_SOCIEDADES.find(s => s.name.toUpperCase().includes(item.tRazonSocial.toUpperCase()));
                if (found) {
                    codigoSap = found.id;
                }
            }

            return {
                id: index + 1,
                nombre: item.tRazonSocial,
                codigoSap: codigoSap, 
                ruc: item.tRuc,
                // Credentials from Sociedad Service
                sunatUsuario: item.tUsuario,
                sunatClave: item.tClave,
                
                ultimaEjecucion: '-', 
                totalEjecuciones: 0,
                listaBlanca: 0, 
                listaBlancaTotal: 0, 
                estado: 'Ejecutar', 
                isSocietyActive: item.lActivo,
                activas: [],
                historial: [],
                // New Date Fields
                selectedDate: today,
                selectedDateFormatted: this.formatDate(today)
            };
        });
        this.filterData();
      },
      error: (err) => console.error('Error loading sociedades', err)
    });
  }

  // ... Calendar Methods ...
  toggleCalendar(item: any, event: Event): void {
      event.stopPropagation();
      if (this.activeCalendarRowId === item.id) {
          this.activeCalendarRowId = null;
      } else {
          this.activeCalendarRowId = item.id;
          this.currentCalendarDate = new Date(item.selectedDate);
          this.generateCalendar(this.currentCalendarDate);
      }
  }

  generateCalendar(date: Date): void {
      const year = date.getFullYear();
      const month = date.getMonth();
      
      const firstDay = new Date(year, month, 1);
      const lastDay = new Date(year, month + 1, 0);
      
      const days = [];
      const startDay = firstDay.getDay(); // 0 = Sunday
      const totalDays = lastDay.getDate();
      
      // Previous month days
      const prevMonthLastDay = new Date(year, month, 0).getDate();
      for (let i = startDay - 1; i >= 0; i--) {
          days.push({
              day: prevMonthLastDay - i,
              currentMonth: false,
              date: new Date(year, month - 1, prevMonthLastDay - i)
          });
      }
      
      // Current month days
      for (let i = 1; i <= totalDays; i++) {
          days.push({
              day: i,
              currentMonth: true,
              date: new Date(year, month, i)
          });
      }
      
      // Next month days to fill grid (42 cells total usually)
      const remaining = 42 - days.length;
      for (let i = 1; i <= remaining; i++) {
          days.push({
              day: i,
              currentMonth: false,
              date: new Date(year, month + 1, i)
          });
      }
      
      this.daysInMonth = days;
  }

  changeMonth(delta: number, event: Event): void {
      event.stopPropagation();
      this.currentCalendarDate.setMonth(this.currentCalendarDate.getMonth() + delta);
      this.currentCalendarDate = new Date(this.currentCalendarDate); // Trigger change detection
      this.generateCalendar(this.currentCalendarDate);
  }

  selectDate(dayObj: any, item: any): void {
      item.selectedDate = dayObj.date;
      item.selectedDateFormatted = this.formatDate(dayObj.date);
      this.activeCalendarRowId = null;
  }

  formatDate(date: Date): string {
      const day = date.getDate().toString().padStart(2, '0');
      const month = (date.getMonth() + 1).toString().padStart(2, '0');
      const year = date.getFullYear();
      return `${day}/${month}/${year}`;
  }
  
  // Params Modal Methods
  openParamsModal(item: any): void {
      this.selectedParamsTask = item;
      this.isParamsModalOpen = true;
      this.showSunatPassword = false;
      this.showSapPassword = false;

      // Initialize defaults
      this.selectedParamsTask.sapUsuario = 'Cargando...';
      this.selectedParamsTask.sapClave = '';

      // Fetch SAP Accounts
      this.isLoadingSap = true;
      this.sociedadService.getSociedadSapAccounts(item.ruc).subscribe({
          next: (accounts) => {
              if (accounts && accounts.length > 0) {
                  // Assuming the first active one is used, matching backend logic
                  this.selectedParamsTask.sapUsuario = accounts[0].tUsuario;
                  this.selectedParamsTask.sapClave = accounts[0].tClave;
              } else {
                  this.selectedParamsTask.sapUsuario = 'No asignado';
                  this.selectedParamsTask.sapClave = '';
              }
              this.isLoadingSap = false;
          },
          error: (err) => {
               console.error('Error loading SAP accounts', err);
               this.selectedParamsTask.sapUsuario = 'Error';
               this.isLoadingSap = false;
          }
      });
  }

  closeParamsModal(): void {
      this.isParamsModalOpen = false;
      this.selectedParamsTask = null;
  }

  executeFromModal(): void {
      if (!this.selectedParamsTask) return;
      
      const payload = {
        date: this.selectedParamsTask.selectedDateFormatted
      };

      // Use the sociedad execution endpoint instead of programacion
      this.http.post(`${this.configService.apiUrl}/crud/sociedades/${this.selectedParamsTask.ruc}/execute`, payload)
        .subscribe({
          next: (res: any) => {
            alert(`Ejecución iniciada correctamente para ${this.selectedParamsTask.nombre}.`);
            this.closeParamsModal();
          },
          error: (err) => {
            console.error('Error executing manually', err);
            const msg = err.error?.detail || err.error?.message || 'Error al iniciar la ejecución. Verifique que la sociedad tenga cuenta SAP activa.';
            alert(msg);
          }
        });
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

  // Execution Modal Logic
  isExecutionModalOpen = false;
  isExecutionModalClosing = false;
  selectedExecution: any = null;
  
  // History Pagination & Controls
  paginatedHistory: any[] = [];
  historyCurrentPage: number = 1;
  historyItemsPerPage: number = 10;
  historyTotalPages: number = 1;
  historyDateRange: string = ''; // Placeholder for now

  openExecutionModal(item: any): void {
    this.selectedExecution = item;
    this.isExecutionModalOpen = true;
    this.isExecutionModalClosing = false;
    this.historyCurrentPage = 1; // Reset page
    
    // Set default date range to today for display (mock)
    const today = new Date();
    const formatted = this.formatDate(today);
    this.historyDateRange = `${formatted} - ${formatted}`;

    document.body.style.overflow = 'hidden';
    
    // Fetch details for this RUC
    this.fetchExecutionDetails(item);
  }

  fetchExecutionDetails(item: any): void {
    this.http.get<any>(`${this.configService.apiUrl}/crud/sociedades/${item.ruc}/ejecuciones`).subscribe({
        next: (resp) => {
            this.selectedExecution.activas = resp.active;
            this.selectedExecution.historial = resp.history;
            this.updateHistoryPagination(); // Init pagination
        },
        error: (err) => console.error('Error fetching details', err)
    });
  }

  updateHistoryPagination(): void {
    if (!this.selectedExecution || !this.selectedExecution.historial) {
        this.paginatedHistory = [];
        return;
    }
    const totalItems = this.selectedExecution.historial.length;
    this.historyTotalPages = Math.ceil(totalItems / this.historyItemsPerPage) || 1;
    
    const startIndex = (this.historyCurrentPage - 1) * this.historyItemsPerPage;
    const endIndex = startIndex + this.historyItemsPerPage;
    this.paginatedHistory = this.selectedExecution.historial.slice(startIndex, endIndex);
  }

  changeHistoryPage(delta: number): void {
    const newPage = this.historyCurrentPage + delta;
    if (newPage >= 1 && newPage <= this.historyTotalPages) {
        this.historyCurrentPage = newPage;
        this.updateHistoryPagination();
    }
  }
  
  setHistoryPage(page: number): void {
    if (page >= 1 && page <= this.historyTotalPages) {
        this.historyCurrentPage = page;
        this.updateHistoryPagination();
    }
  }

  onHistoryItemsPerPageChange(event: any): void {
      this.historyItemsPerPage = parseInt(event.target.value, 10);
      this.historyCurrentPage = 1;
      this.updateHistoryPagination();
  }

  exportHistoryExcel(): void {
      console.log('Exporting history to Excel...');
      // Implement export logic here
      alert('Funcionalidad de exportar a Excel en desarrollo.');
  }

  runProgramacion(progId: number, ruc: string): void {
    if(!confirm('¿Estás seguro de ejecutar esta programación ahora?')) return;

    this.http.post(`${this.configService.apiUrl}/crud/programacion/${progId}/execute?ruc=${ruc}`, {}).subscribe({
        next: (resp) => {
            alert('Ejecución iniciada correctamente');
            this.fetchExecutionDetails(this.selectedExecution);
        },
        error: (err) => {
            console.error('Error executing programacion', err);
            const msg = err.error?.detail || err.error?.message || 'Error al iniciar la ejecución';
            alert(msg);
        }
    });
  }

  closeExecutionModal(): void {
    if (this.isLogModalOpen) {
        this.closeLogModal();
    }
    
    this.isExecutionModalClosing = true;

    setTimeout(() => {
        this.isExecutionModalOpen = false;
        this.isExecutionModalClosing = false;
        this.selectedExecution = null;
        // Restore body scroll
        document.body.style.overflow = 'auto';
    }, 200);
  }

  // Logs Modal Logic
  isLogModalOpen = false;
  isLogModalClosing = false;
  selectedLogTask: any = null;
  private logSubscription: Subscription | null = null;

  downloadFiles(item: any): void {
    console.log('Descargando archivos para ejecución:', item);
    // TODO: Implement actual download logic via backend endpoint
    // Example: this.http.get(..., { responseType: 'blob' })...
    alert(`Iniciando descarga de archivos para: ${item.nombre}\n(Funcionalidad pendiente de backend)`);
  }

  openLogModal(task: any, event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.selectedLogTask = task;
    this.selectedLogTask.logs = []; // Clear previous logs to avoid duplication
    this.isLogModalOpen = true;
    this.isLogModalClosing = false;

    // Load logs from history if execution ID exists
    if (this.selectedLogTask.iMEjecucion) {
        this.http.get<any[]>(`${this.configService.apiUrl}/crud/ejecuciones/${this.selectedLogTask.iMEjecucion}/logs`).subscribe({
            next: (logs) => {
                const historyLogs = logs.map(log => ({
                    fecha: log.date,
                    configuracion: this.selectedLogTask.nombre,
                    estado: log.message
                }));
                // Prepend history logs to any logs that might have arrived via socket
                this.selectedLogTask.logs = [...historyLogs, ...this.selectedLogTask.logs];
            },
            error: (err) => console.error('Error fetching logs', err)
        });
    }

    // Subscribe to socket logs
    this.logSubscription = this.socketService.onLog().subscribe((logData: any) => {
      if (!this.selectedLogTask.logs) {
        this.selectedLogTask.logs = [];
      }
      
      // Ensure we are adding to the currently selected task logs
      // Note: In a real multi-user scenario, we might want to filter by RUC or ID in the log message
      // But for now, we just append logs as they come in while the modal is open.
      this.selectedLogTask.logs.push({
        fecha: logData.date,
        configuracion: this.selectedLogTask.nombre, // Or use data from log if available
        estado: logData.message
      });
      
      // Force view update since socket events run outside Angular zone
      this.cdr.detectChanges();
    });
  }

  closeLogModal(): void {
    this.isLogModalClosing = true;
    
    // Unsubscribe to avoid memory leaks
    if (this.logSubscription) {
      this.logSubscription.unsubscribe();
      this.logSubscription = null;
    }

    setTimeout(() => {
      this.isLogModalOpen = false;
      this.isLogModalClosing = false;
      this.selectedLogTask = null;
    }, 200); // Matches animation duration
  }

  // Whitelist Modal Logic
  isWhitelistModalOpen = false;
  globalWhitelist: any[] = [];
  filteredWhitelist: any[] = [];
  paginatedWhitelist: any[] = [];
  whitelistSearchTerm: string = '';
  whitelistCurrentPage: number = 1;
  whitelistItemsPerPage: number = 10;
  totalWhitelistPages: number = 1;

  openWhitelistModal(): void {
    this.isWhitelistModalOpen = true;
    this.whitelistSearchTerm = '';
    this.whitelistCurrentPage = 1;
    this.loadWhitelistCount(); // Refresh on open to ensure latest data
  }

  closeWhitelistModal(): void {
    this.isWhitelistModalOpen = false;
  }

  onWhitelistSearch(event: any): void {
    this.whitelistSearchTerm = event.target.value;
    this.whitelistCurrentPage = 1;
    this.filterWhitelist();
  }

  filterWhitelist(): void {
    if (!this.whitelistSearchTerm) {
      this.filteredWhitelist = [...this.globalWhitelist];
    } else {
      const term = this.whitelistSearchTerm.toLowerCase();
      this.filteredWhitelist = this.globalWhitelist.filter(item => 
        (item.sociedadesNombres && item.sociedadesNombres.toLowerCase().includes(term)) ||
        (item.razonSocial && item.razonSocial.toLowerCase().includes(term)) ||
        (item.ruc && item.ruc.includes(term))
      );
    }
    this.totalWhitelistPages = Math.ceil(this.filteredWhitelist.length / this.whitelistItemsPerPage) || 1;
    this.updateWhitelistPagination();
  }

  updateWhitelistPagination(): void {
    const startIndex = (this.whitelistCurrentPage - 1) * this.whitelistItemsPerPage;
    const endIndex = startIndex + this.whitelistItemsPerPage;
    this.paginatedWhitelist = this.filteredWhitelist.slice(startIndex, endIndex);
  }

  changeWhitelistPage(delta: number): void {
    const newPage = this.whitelistCurrentPage + delta;
    if (newPage >= 1 && newPage <= this.totalWhitelistPages) {
      this.whitelistCurrentPage = newPage;
      this.updateWhitelistPagination();
    }
  }
}