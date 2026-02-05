import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './modules/auth/login/login.component';
import { ConfigComponent } from './modules/auth/config/config.component';
import { DashboardComponent } from './modules/dashboard/dashboard.component';
import { DashboardHomeComponent } from './modules/dashboard/pages/home/home.component';
import { EjecucionesComponent } from './modules/dashboard/pages/ejecuciones/ejecuciones.component';
import { ProgramacionComponent } from './modules/dashboard/pages/programacion/programacion.component';
import { SociedadesComponent } from './modules/dashboard/pages/sociedades/sociedades.component';
import { UsuariosComponent } from './modules/dashboard/pages/usuarios/usuarios.component';
import { ProveedoresComponent } from './modules/dashboard/pages/proveedores/proveedores.component';

const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { 
    path: '', 
    component: DashboardComponent,
    children: [
      { path: 'ejecuciones', component: EjecucionesComponent },
      { path: 'programacion', component: ProgramacionComponent },
      { path: 'maestros/sociedades', component: SociedadesComponent },
      { path: 'maestros/usuarios', component: UsuariosComponent },
      { path: 'maestros/proveedores', component: ProveedoresComponent },
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
