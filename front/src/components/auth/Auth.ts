export function getApiUrl(): string {
    const parts = window.location.pathname.split('/');
    const baseUrl: string = window.location.protocol + '//' + window.location.host + '/' + (parts[1] ? parts[1] + '/' : '');
    if (baseUrl.includes('localhost:3000'))
        return 'http://localhost:8000/';
    return baseUrl;
}

export const apiUrl: string = getApiUrl();

export interface AuthProvider {
    username: null | string;
    isAuthenticated: null | boolean;
    init(): Promise<AuthProvider>;
    demo(): Promise<Response>;
    login(username: string, password: string): Promise<Response>;
    logout(): Promise<void>;
}
  
export const auth: AuthProvider = {
    username: null,
    isAuthenticated: null,

    async init(): Promise<AuthProvider> {
        const cred: RequestCredentials = 'include';
        const headers =  {'Content-type': 'application/json'};
        const resp = await fetch(apiUrl + 'api/auth/', { method: 'GET', headers: headers, credentials: cred, }).then((response) => response.json());
        if (resp && resp.ok && resp.username) {
            auth.username = resp.username;
            auth.isAuthenticated = true;
        }
        return auth;
    },

    async demo(): Promise<Response> {
        const data = 'grant_type=password';
        const cred: RequestCredentials = 'include';
        const resp = await fetch(apiUrl + 'api/demo/', { method: 'POST', headers: {'Content-type': 'application/x-www-form-urlencoded'}, credentials: cred, body: data }).then((response) => response.json());
        if (resp && resp.ok && resp.info) {
          auth.username = resp.info;
          auth.isAuthenticated = true;
        }
        return resp;
    },
    
    async login(username: string, password: string): Promise<Response> {
        const data = `grant_type=password&username=${username}&password=${password}`;
        const cred: RequestCredentials = 'include';
        const resp = await fetch(apiUrl + 'api/login/', { method: 'POST', headers: {'Content-type': 'application/x-www-form-urlencoded'}, credentials: cred, body: data }).then((response) => response.json());
        if (resp && resp.ok && resp.info) {
          auth.username = resp.info;
          auth.isAuthenticated = true;
        }
        return resp;
    },

    async logout(): Promise<void> {
        const cred: RequestCredentials = 'include';
        const resp = await fetch(apiUrl + 'api/logout/', { method: 'GET', headers: {'Content-type': 'application/json'}, credentials: cred, }).then((response) => response.json());
        if (resp && resp.ok) {
          auth.isAuthenticated = false;
          auth.username = '';
        }
    },

};
