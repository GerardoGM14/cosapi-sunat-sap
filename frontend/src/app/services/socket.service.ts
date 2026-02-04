import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { AppConfigService } from './app-config.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: Socket | undefined;

  constructor(private configService: AppConfigService) {
    this.initSocket();
  }

  private initSocket(): void {
    const apiUrl = this.configService.apiUrl;
    let socketUrl = '';

    if (apiUrl.startsWith('http')) {
      const url = new URL(apiUrl);
      socketUrl = `${url.protocol}//${url.host}`;
    } else {
      socketUrl = '/'; 
    }

    console.log('Connecting to socket at:', socketUrl);

    this.socket = io(socketUrl, {
      path: '/api/socket.io', // Changed to /api/socket.io to work through Nginx /api proxy
      transports: ['websocket', 'polling'],
      autoConnect: true
    });

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id);
    });

    this.socket.on('disconnect', () => {
      console.log('Socket disconnected');
    });
    
    this.socket.on('connect_error', (err) => {
        console.error('Socket connection error:', err);
    });
  }

  on(eventName: string): Observable<any> {
    return new Observable((subscriber) => {
      if (!this.socket) {
        subscriber.error('Socket not initialized');
        return;
      }

      this.socket.on(eventName, (data) => {
        subscriber.next(data);
      });
      
      return () => {
        this.socket?.off(eventName);
      };
    });
  }

  onLog(): Observable<any> {
    return this.on('log:bot');
  }
}
