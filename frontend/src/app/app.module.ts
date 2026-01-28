import { NgModule, APP_INITIALIZER } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LoginComponent } from './modules/auth/login/login.component';
import { ConfigComponent } from './modules/auth/config/config.component';
import { DashboardComponent } from './modules/dashboard/dashboard.component';
import { DashboardHomeComponent } from './modules/dashboard/pages/home/home.component';
import { EjecucionesComponent } from './modules/dashboard/pages/ejecuciones/ejecuciones.component';
import { ProgramacionComponent } from './modules/dashboard/pages/programacion/programacion.component';
import { NavbarComponent } from './modules/dashboard/components/navbar/navbar.component';
import { AppConfigService } from './services/app-config.service';

export function initializeApp(appConfig: AppConfigService) {
  return () => appConfig.loadConfig();
}

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    ConfigComponent,
    DashboardComponent,
    DashboardHomeComponent,
    EjecucionesComponent,
    ProgramacionComponent,
    NavbarComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: initializeApp,
      deps: [AppConfigService],
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
