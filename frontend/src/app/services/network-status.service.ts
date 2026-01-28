import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, merge, fromEvent, of, Observable } from 'rxjs';
import { mapTo, map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class NetworkStatusService {
  private onlineStatus$ = new BehaviorSubject<boolean>(navigator.onLine);
  public isOnline$ = this.onlineStatus$.asObservable();

  constructor(private http: HttpClient) {
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
    const url = 'https://www.google.com/favicon.ico';
    this.http.head(url + '?t=' + new Date().getTime(), { responseType: 'text' })
      .pipe(
        map(() => true),
        catchError(() => of(false))
      )
      .subscribe(hasInternet => {
        this.updateOnlineStatus(hasInternet);
      });
  }

  public updateOnlineStatus(isOnline: boolean): void {
    if (this.onlineStatus$.value !== isOnline) {
      this.onlineStatus$.next(isOnline);
    }
  }
}
