import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AppConfigService } from '../../../../services/app-config.service';

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

  constructor(private http: HttpClient, private configService: AppConfigService) {
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
    this.http.get<any[]>(`${this.configService.apiUrl}/crud/sociedades`).subscribe({
      next: (data) => {
        this.ejecuciones = data.map((item, index) => ({
            id: index + 1,
            nombre: item.tRazonSocial,
            ruc: item.tRuc,
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
        }));
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

