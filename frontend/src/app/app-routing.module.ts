import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './modules/auth/login/login.component';
import { ConfigComponent } from './modules/auth/config/config.component';
import { DashboardComponent } from './modules/dashboard/dashboard.component';
import { DashboardHomeComponent } from './modules/dashboard/pages/home/home.component';
import { EjecucionesComponent } from './modules/dashboard/pages/ejecuciones/ejecuciones.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: '', 
    component: DashboardComponent,
    children: [
      { path: 'ejecuciones', component: EjecucionesComponent },
      { path: 'config', component: ConfigComponent },
      { path: '', redirectTo: 'ejecuciones', pathMatch: 'full' }
    ]
  },
  { path: '**', redirectTo: '/login' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
