import { Injectable } from '@angular/core';
import { BehaviorSubject, merge, fromEvent } from 'rxjs';
import { mapTo } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class NetworkStatusService {
  private onlineStatus$ = new BehaviorSubject<boolean>(navigator.onLine);
  public isOnline$ = this.onlineStatus$.asObservable();

  constructor() {
    this.initNetworkListeners();
  }

  private initNetworkListeners(): void {
    merge(
      fromEvent(window, 'online').pipe(mapTo(true)),
      fromEvent(window, 'offline').pipe(mapTo(false))
    ).subscribe((status) => {
      if (status) {
        this.verifyInternetConnection();
      } else {
        this.updateOnlineStatus(false);
      }
    });
  }

  public verifyInternetConnection(): void {
    // Usamos 'Image' para hacer un ping simple que no sea bloqueado por CORS
    // Google favicon es fiable, pero HttpClient (XHR) es bloqueado por CORS.
    // La carga de imágenes permite verificar si hay acceso a internet sin leer el contenido.
    const url = 'https://www.google.com/favicon.ico';
    const img = new Image();
    
    img.onload = () => {
      this.updateOnlineStatus(true);
    };

    img.onerror = () => {
      // Si falla la carga de la imagen (y no es por 404, que google no suele dar para favicon), asumimos sin conexión
      // Nota: Si google está bloqueado pero hay internet, esto dará falso, lo cual es aceptable para "acceso a internet global"
      this.updateOnlineStatus(false);
    };

    // Agregamos timestamp para evitar caché
    img.src = url + '?t=' + new Date().getTime();
  }

  public updateOnlineStatus(isOnline: boolean): void {
    if (this.onlineStatus$.value !== isOnline) {
      this.onlineStatus$.next(isOnline);
    }
  }
}
