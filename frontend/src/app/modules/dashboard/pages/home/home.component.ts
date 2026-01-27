import { Component } from '@angular/core';

@Component({
  selector: 'app-dashboard-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class DashboardHomeComponent {
  username = 'Usuario Contable'; // Should be passed from parent or service, but for now hardcoded to match
}
