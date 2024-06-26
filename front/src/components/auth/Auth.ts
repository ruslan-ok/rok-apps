export function getApiUrl(): string {
    const parts = window.location.pathname.split('/');
    const baseUrl: string = window.location.protocol + '//' + window.location.host + '/' + (parts[1] ? parts[1] + '/' : '');
    if (baseUrl.includes('localhost:3000'))
        return 'http://localhost:8001/';
    return baseUrl;
}

export const apiUrl: string = getApiUrl();

export interface AuthProvider {
    username: null | string;
    isAuthenticated: null | boolean;
    init(): Promise<AuthProvider>;
}
  
export const auth: AuthProvider = {
    username: null,
    isAuthenticated: null,

    async init(): Promise<AuthProvider> {
        const cred: RequestCredentials = 'include';
    const resp = await fetch(apiUrl + 'api/react/get_username', { method: 'GET', headers: {'Content-type': 'application/json'}, credentials: cred, }).then((response) => response.json());
        if (resp && resp.ok && resp.username) {
            auth.username = resp.username;
            auth.isAuthenticated = true;
        }
        return auth;
    },
};
