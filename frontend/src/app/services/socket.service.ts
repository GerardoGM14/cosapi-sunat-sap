import { Injectable } from '@angular/core';
import { io, Socket } from 'socket.io-client';
import { AppConfigService } from './app-config.service';
import { Observable, BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SocketService {
  private socket: Socket | undefined;
  private isConnectedSubject = new BehaviorSubject<boolean>(false);
  public isConnected$ = this.isConnectedSubject.asObservable();
  private connectionTimer: any;

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
      path: '/api/socket.io',
      // Force WebSocket to avoid polling issues (400 Bad Request) and sticky session requirements
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 20000,
    });

    this.socket.on('connect', () => {
      console.log('Socket connected:', this.socket?.id);
      
      // Clear any existing timer
      if (this.connectionTimer) {
        clearTimeout(this.connectionTimer);
      }

      // Wait 2 seconds before marking as stable
      this.connectionTimer = setTimeout(() => {
        if (this.socket?.connected) {
          console.log('Socket connection stable');
          this.isConnectedSubject.next(true);
        }
      }, 2000);
    });

    this.socket.on('disconnect', () => {
      console.log('Socket disconnected');
      // Immediate feedback: connection lost
      this.isConnectedSubject.next(false);
      
      if (this.connectionTimer) {
        clearTimeout(this.connectionTimer);
        this.connectionTimer = null;
      }
    });
    
    this.socket.on('connect_error', (err) => {
        console.error('Socket connection error:', err);
        this.isConnectedSubject.next(false);
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
