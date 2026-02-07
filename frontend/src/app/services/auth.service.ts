import { Injectable, NgZone } from '@angular/core';
import { Router } from '@angular/router';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private authChannel: BroadcastChannel;
  private sessionExpiredSubject = new BehaviorSubject<boolean>(false);
  public sessionExpired$ = this.sessionExpiredSubject.asObservable();

  constructor(private router: Router, private ngZone: NgZone) {
    // 1. Initialize BroadcastChannel for modern cross-tab communication
    this.authChannel = new BroadcastChannel('auth_channel');
    
    // 2. Initialize listeners
    this.initBroadcastListener();
    this.initStorageListener();
    
    console.log('AuthService initialized with BroadcastChannel and Storage Listener');
  }

  private initBroadcastListener() {
    this.authChannel.onmessage = (event) => {
      console.log('BroadcastChannel message received:', event.data);
      if (event.data.type === 'LOGOUT') {
        this.handleRemoteLogout('BroadcastChannel');
      }
    };
  }

  private initStorageListener() {
    // 3. Fallback: Storage event fires when localStorage changes in OTHER tabs
    window.addEventListener('storage', (event) => {
      if (event.key === 'token' && event.newValue === null) {
        console.log('Storage event detected token removal');
        this.handleRemoteLogout('StorageEvent');
      }
    });
  }

  /**
   * Called when the user clicks "Logout" in the current tab.
   */
  logout() {
    console.log('Logging out from current tab...');
    this.clearSession();
    
    // Notify other tabs via BroadcastChannel
    this.authChannel.postMessage({ type: 'LOGOUT' });
    
    // Navigate to login immediately
    this.router.navigate(['/login']);
  }

  /**
   * Called when another tab has logged out.
   */
  private handleRemoteLogout(source: string) {
    console.log(`Handling remote logout triggered by: ${source}`);
    
    // Use NgZone to ensure Angular detects the change immediately
    // because BroadcastChannel and Storage events run outside Angular's zone
    this.ngZone.run(() => {
      // If we are already on the login page, do nothing
      if (this.router.url.includes('/login')) {
        return;
      }
  
      // Always ensure session is cleared locally
      this.clearSession();
      
      // Trigger the modal
      this.sessionExpiredSubject.next(true);
    });
  }

  private clearSession() {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  }

  closeExpiredModal() {
    this.sessionExpiredSubject.next(false);
    this.router.navigate(['/login']);
  }
}
