import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-programacion',
  templateUrl: './programacion.component.html',
  styleUrls: ['./programacion.component.css']
})
export class ProgramacionComponent implements OnInit {
  
  // Dummy data based on the image and related to Ejecuciones
  programaciones = [
    {
      id: 1,
      nombre: 'Sincronización Nocturna SAP',
      hora: '18:29',
      dias: ['Lun', 'Mar', 'Mier', 'Juev'],
      sociedades: 14,
      estado: true // true for active (blue toggle), false for inactive
    },
    {
      id: 2,
      nombre: 'Sincronización Nocturna SAP', // Example of repeating name with different schedule
      hora: '18:29',
      dias: ['Lun', 'Mar', 'Juev'],
      sociedades: 14,
      estado: true
    },
    {
      id: 3,
      nombre: 'Cierre Diario',
      hora: '23:00',
      dias: ['Lun', 'Mar', 'Mier', 'Juev', 'Vier'],
      sociedades: 5,
      estado: false
    },
    {
      id: 4,
      nombre: 'Reporte Semanal de Ventas',
      hora: '08:00',
      dias: ['Lun'],
      sociedades: 10,
      estado: true
    }
  ];

  filteredProgramaciones = [...this.programaciones];
  searchTerm: string = '';
  selectedStatus: string = 'TODOS';

  // Modal Logic
  isModalOpen: boolean = false;
  
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

  sociedadesList = [
    { id: '123456789', name: 'SERVICIOS LOGISTICOS PERU S.A.', selected: true },
    { id: '123456789', name: 'SERVICIOS LOGISTICOS PERU S.A.', selected: true },
    { id: '123456789', name: 'SERVICIOS LOGISTICOS PERU S.A.', selected: false },
    { id: '123456789', name: 'SERVICIOS LOGISTICOS PERU S.A.', selected: true },
    { id: '123456789', name: 'SERVICIOS LOGISTICOS PERU S.A.', selected: false },
    { id: '123456789', name: 'SERVICIOS LOGISTICOS PERU S.A.', selected: false },
    { id: '123456789', name: 'SERVICIOS LOGISTICOS PERU S.A.', selected: true },
  ];

  societySearchTerm: string = '';
  showSocietySearch: boolean = false;

  // Time Picker Logic
  isTimePickerOpen: boolean = false;
  hours: string[] = Array.from({ length: 24 }, (_, i) => i.toString().padStart(2, '0'));
  minutes: string[] = Array.from({ length: 12 }, (_, i) => (i * 5).toString().padStart(2, '0'));
  selectedHour: string = '00';
  selectedMinute: string = '00';

  constructor() { }

  ngOnInit(): void {
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
    } else {
      // Optional: Focus logic could be added here with ViewChild
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

  toggleSociety(society: any): void {
    society.selected = !society.selected;
  }

  getSelectedSocietiesCount(): number {
    return this.sociedadesList.filter(s => s.selected).length;
  }

  saveProgramacion(): void {
    console.log('Guardando programación...', this.newProgramacion);
    console.log('Sociedades seleccionadas:', this.sociedadesList.filter(s => s.selected));
    this.closeModal();
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
    item.estado = !item.estado;
    // Here you would typically call an API to update the status
    console.log(`Status toggled for ${item.nombre}: ${item.estado}`);
  }
}
