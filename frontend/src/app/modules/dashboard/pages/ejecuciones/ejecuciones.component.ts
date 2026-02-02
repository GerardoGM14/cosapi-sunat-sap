import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfigService } from '../../../../services/app-config.service';
import { SociedadService } from '../../../../services/sociedad.service';

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
    private sociedadService: SociedadService
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

      this.http.post(`${this.configService.apiUrl}/crud/sociedades/${this.selectedParamsTask.ruc}/execute`, payload)
        .subscribe({
          next: (res: any) => {
            alert(`Ejecución iniciada correctamente para ${this.selectedParamsTask.nombre}.`);
            this.closeParamsModal();
          },
          error: (err) => {
            console.error('Error executing manually', err);
            alert('Error al iniciar la ejecución. Verifique que la sociedad tenga cuenta SAP activa.');
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

  // Drawer Logic
  isDrawerOpen = false;
  selectedExecution: any = null;

  openDrawer(item: any): void {
    this.selectedExecution = item;
    this.isDrawerOpen = true;
    document.body.style.overflow = 'hidden';
    
    // Fetch details for this RUC
    this.fetchExecutionDetails(item);
  }

  fetchExecutionDetails(item: any): void {
    this.http.get<any>(`${this.configService.apiUrl}/crud/sociedades/${item.ruc}/ejecuciones`).subscribe({
        next: (resp) => {
            this.selectedExecution.activas = resp.active;
            this.selectedExecution.historial = resp.history;
        },
        error: (err) => console.error('Error fetching details', err)
    });
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
            alert('Error al iniciar la ejecución');
        }
    });
  }

  closeDrawer(): void {
    this.isDrawerOpen = false;
    this.selectedExecution = null;
    // Restore body scroll
    document.body.style.overflow = 'auto';
  }

  // Logs Modal Logic
  isLogModalOpen = false;
  selectedLogTask: any = null;

  openLogModal(task: any, event?: Event): void {
    if (event) {
      event.stopPropagation();
    }
    this.selectedLogTask = task;
    this.isLogModalOpen = true;
  }

  closeLogModal(): void {
    this.isLogModalOpen = false;
    this.selectedLogTask = null;
  }

  // Whitelist Modal Logic
  isWhitelistModalOpen = false;
  globalWhitelist = [
    { ruc: '20100123456', razonSocial: 'PROVEEDOR EJEMPLO 1 S.A.C.' },
    { ruc: '20200123457', razonSocial: 'PROVEEDOR EJEMPLO 2 S.R.L.' },
    { ruc: '20300123458', razonSocial: 'PROVEEDOR EJEMPLO 3 E.I.R.L.' },
    { ruc: '20400123459', razonSocial: 'PROVEEDOR EJEMPLO 4 S.A.' },
    { ruc: '20500123460', razonSocial: 'PROVEEDOR EJEMPLO 5 S.A.C.' },
    { ruc: '20600123461', razonSocial: 'PROVEEDOR EJEMPLO 6 S.A.A.' }
  ];

  openWhitelistModal(): void {
    this.isWhitelistModalOpen = true;
  }

  closeWhitelistModal(): void {
    this.isWhitelistModalOpen = false;
  }
}

