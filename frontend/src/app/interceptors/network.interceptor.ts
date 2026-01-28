import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { NetworkStatusService } from '../services/network-status.service';

@Injectable()
export class NetworkInterceptor implements HttpInterceptor {

  constructor(private networkService: NetworkStatusService) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 0) {
          this.networkService.updateOnlineStatus(false);
        }
        return throwError(error);
      })
    );
  }
}
