import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-config',
  templateUrl: './config.component.html',
  styleUrls: ['./config.component.css']
})
export class ConfigComponent {
  configData = {
    sunat: {
      ruc: '',
      usuario: '',
      claveSol: ''
    },
    sap: {
      email: '',
      password: ''
    },
    general: {
      sociedad: '',
      fecha: '',
      folder: ''
    }
  };

  sociedades = [
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

  filteredSociedades: any[] = [];
  searchTerm: string = '';
  isDropdownOpen: boolean = false;
  isConfirmModalOpen: boolean = false;

  showSolPassword = false;
  showSapPassword = false;
  errorMessage = '';
  successMessage = '';

  sunatImage: string = 'assets/images/logo-sunat.svg';
  sapImage: string = 'assets/images/logo-sap.png';

  constructor(private router: Router, private http: HttpClient) {
    // No cargar configuración guardada para iniciar siempre limpio
  }

  toggleDropdown() {
    this.isDropdownOpen = !this.isDropdownOpen;
    if (this.isDropdownOpen) {
      // Reset search when opening
      this.searchTerm = '';
      this.filterSociedades();
    }
  }

  selectSociedad(sociedad: any) {
    this.configData.general.sociedad = sociedad.id;
    this.isDropdownOpen = false;
  }

  filterSociedades() {
    if (!this.searchTerm) {
      this.filteredSociedades = [...this.sociedades];
    } else {
      const term = this.searchTerm.toLowerCase();
      this.filteredSociedades = this.sociedades.filter(soc => 
        soc.name.toLowerCase().includes(term) || soc.id.includes(term)
      );
    }
  }

  getSelectedSociedadName(): string {
    const selected = this.sociedades.find(s => s.id === this.configData.general.sociedad);
    return selected ? selected.name : 'Seleccione una sociedad';
  }

  // Calendar Logic
  isCalendarOpen = false;
  currentCalendarDate = new Date();
  weekDays = ['Do', 'Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sa'];
  daysInMonth: { day: number, currentMonth: boolean, date?: Date }[] = [];
  months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];

  toggleCalendar() {
    this.isCalendarOpen = !this.isCalendarOpen;
    if (this.isCalendarOpen) {
      if (this.configData.general.fecha) {
        const parts = this.configData.general.fecha.split('-');
        this.currentCalendarDate = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
      } else {
        this.currentCalendarDate = new Date();
      }
      this.generateCalendar();
    }
  }

  generateCalendar() {
    const year = this.currentCalendarDate.getFullYear();
    const month = this.currentCalendarDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    
    const startingDay = firstDay.getDay(); 
    const totalDays = lastDay.getDate();
    
    this.daysInMonth = [];
    
    // Previous month filler
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = 0; i < startingDay; i++) {
       this.daysInMonth.unshift({ day: prevMonthLastDay - i, currentMonth: false });
    }
    
    // Current month
    for (let i = 1; i <= totalDays; i++) {
       this.daysInMonth.push({ day: i, currentMonth: true, date: new Date(year, month, i) });
    }
    
    // Next month filler
    const remaining = 42 - this.daysInMonth.length;
    for (let i = 1; i <= remaining; i++) {
        this.daysInMonth.push({ day: i, currentMonth: false });
    }
  }

  changeMonth(delta: number, event: Event) {
      event.stopPropagation();
      this.currentCalendarDate.setMonth(this.currentCalendarDate.getMonth() + delta);
      this.currentCalendarDate = new Date(this.currentCalendarDate);
      this.generateCalendar();
  }

  selectDate(day: any) {
      if (!day.currentMonth || !day.date) return;
      
      const year = day.date.getFullYear();
      const month = (day.date.getMonth() + 1).toString().padStart(2, '0');
      const d = day.date.getDate().toString().padStart(2, '0');
      
      this.configData.general.fecha = `${year}-${month}-${d}`;
      this.isCalendarOpen = false;
  }

  getFormattedDate(): string {
    if (!this.configData.general.fecha) return 'dd/mm/aaaa';
    const parts = this.configData.general.fecha.split('-');
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
  }

  saveConfig() {
    this.errorMessage = '';
    this.successMessage = '';

    // Validaciones
    if (!this.configData.sunat.ruc || this.configData.sunat.ruc.length > 11) {
      this.showError('El RUC debe tener máximo 11 caracteres.');
      return;
    }

    if (!this.configData.sunat.usuario) {
      this.showError('El usuario SOL es requerido.');
      return;
    }

    if (!this.configData.sunat.claveSol) {
      this.showError('La clave SOL es requerida.');
      return;
    }

    if (!this.configData.sap.email || !this.configData.sap.email.includes('@')) {
      this.showError('El correo electrónico debe ser válido (contener @).');
      return;
    }

    if (!this.configData.sap.password) {
      this.showError('La contraseña SAP es requerida.');
      return;
    }

    if (!this.configData.general.sociedad) {
      this.showError('Debe seleccionar una sociedad.');
      return;
    }

    if (!this.configData.general.fecha) {
      this.showError('Debe seleccionar una fecha.');
      return;
    }

    if (!this.configData.general.folder) {
      this.showError('Debe seleccionar una carpeta de salida.');
      return;
    }

    // Si todo está válido, abrir el modal de confirmación
    this.isConfirmModalOpen = true;
  }

  confirmProcess() {
    this.isConfirmModalOpen = false;
    
    // Convertir fecha de YYYY-MM-DD a DD/MM/YYYY
    const dateParts = this.configData.general.fecha.split('-');
    const formattedDate = `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`;

    // Crear payload con fecha formateada
    const payload = {
      sunat: this.configData.sunat,
      sap: this.configData.sap,
      general: {
        ...this.configData.general,
        fecha: formattedDate
      }
    };

    console.log('Iniciando proceso...', payload);
    this.showSuccess('Iniciando proceso...');

    this.http.post(`${environment.apiUrl}/bot/run`, payload)
      .subscribe({
        next: (res: any) => {
          console.log('Bot response:', res);
          this.showSuccess('Proceso iniciado correctamente.');
        },
        error: (err) => {
          console.error('Error starting bot:', err);
          this.showError('Error al iniciar el proceso: ' + (err.error?.detail || err.message));
        }
      });
  }

  cancelProcess() {
    this.isConfirmModalOpen = false;
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

  // Mantenemos showToast por compatibilidad si es necesario, pero redirigimos
  showToast(isSuccess: boolean = false) {
    this.triggerToastTimeout();
  }

  // File Browser Logic
  isBrowserModalOpen = false;
  browserCurrentPath = '';
  browserFolders: string[] = [];
  browserLoading = false;

  openBrowser() {
    this.isBrowserModalOpen = true;
    this.loadFolders(this.configData.general.folder || '');
  }

  closeBrowser() {
    this.isBrowserModalOpen = false;
  }

  loadFolders(path: string) {
    this.browserLoading = true;
    this.http.post<any>(`${environment.apiUrl}/utils/list-folders`, { path })
      .subscribe({
        next: (res) => {
          this.browserCurrentPath = res.current_path;
          this.browserFolders = res.folders;
          this.browserLoading = false;
        },
        error: (err) => {
          console.error('Error listing folders', err);
          this.showError('Error al listar carpetas: ' + err.message);
          this.browserLoading = false;
        }
      });
  }

  navigateUp() {
    // Simple logic to go up
    // En Windows las rutas son C:\algo\otro. En Linux /algo/otro
    // El backend ya nos devuelve el parent, pero por ahora lo calculamos o pedimos al backend
    // Mejor pedir al backend la ruta padre, pero en este caso simple:
    // Reutilizamos loadFolders con '..' relative path logic o dejamos que el backend maneje parent
    // Vamos a asumir que el usuario hace click en ".." que vendrá en la lista si lo implementamos así
    // O mejor, implementamos un botón "Subir nivel"
    
    // Hack rápido: Pedir al backend el padre.
    // Vamos a modificar loadFolders para que el backend nos de el padre, 
    // pero como ya lo hice en el backend (parent_path), lo usamos si lo guardamos.
    // Necesito guardar el parent_path.
    
    // Para simplificar, simplemente recargamos el path actual + '/..'
    // O mejor, implementamos navigateTo
  }

  navigateTo(folderName: string) {
    let newPath = '';
    if (this.browserCurrentPath.endsWith('\\') || this.browserCurrentPath.endsWith('/')) {
        newPath = this.browserCurrentPath + folderName;
    } else {
        // Detect separator
        const sep = this.browserCurrentPath.includes('\\') ? '\\' : '/';
        newPath = this.browserCurrentPath + sep + folderName;
    }
    this.loadFolders(newPath);
  }
  
  navigateParent() {
      // Simple parent detection
      const sep = this.browserCurrentPath.includes('\\') ? '\\' : '/';
      const parts = this.browserCurrentPath.split(sep);
      parts.pop(); // Remove current
      const parent = parts.join(sep) || sep; // Fallback to root
      this.loadFolders(parent);
  }

  selectCurrentFolder() {
      this.configData.general.folder = this.browserCurrentPath;
      this.closeBrowser();
  }

  // Legacy (Server-side Dialog)
  selectFolder() {
    // Ahora abrimos nuestro propio navegador
    this.openBrowser();
  }

  backToLogin() {
    this.router.navigate(['/login']);
  }
}
