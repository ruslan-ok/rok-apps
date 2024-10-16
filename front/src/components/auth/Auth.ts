import type { MouseEvent } from 'react'

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
    buttonData(event: MouseEvent<HTMLElement>, attributes: string[]): Object;
    objectToUrlParams(obj: Object): string;
    get(url: string, params: Object): Promise<Response>;
    post(url: string, params: Object): Promise<Response>;
    demo(): Promise<Response>;
    login(username: string, password: string): Promise<Response>;
    logout(): Promise<void>;
}
  
export const auth: AuthProvider = {
    username: null,
    isAuthenticated: null,

    buttonData(event: MouseEvent<HTMLElement>, attributes: string[]): Object {
        let el = event.target as HTMLElement;
        if (el.tagName !== 'BUTTON' && el.parentElement)
            el = el.parentElement;
        let ret = {};
        for (const attr of attributes) {
            const value = el.getAttribute(`data-${attr}`);
            if (value === null)
                throw new Error(`The "${attr}" attribute is not defined.`);
            ret = Object.assign(ret, {[attr]: value});
        }
        return ret;
    },

    objectToUrlParams(obj: Object): string {
        const params = [];

        const extObj = Object.assign(obj, {'format': 'json'});
      
        for (const key in extObj) {
          params.push(`${encodeURIComponent(key)}=${encodeURIComponent(extObj[key])}`);
        }
      
        return (params.length ? '?' : '') + params.join('&');
    },
      
    async get(url: string, params: Object): Promise<Response> {
        const cred: RequestCredentials = 'include';
        const headers =  {'Content-type': 'application/json'};
        const urlParams = this.objectToUrlParams(params);
        const correctedUrl = (url.startsWith('api/') ? '' : 'api/') + url + (url.endsWith('/') ? '' : '/');
        const resp = await fetch(
            apiUrl + correctedUrl + urlParams, 
            { method: 'GET', headers: headers, credentials: cred }
        ).then((response) => response.json());
        return resp;
    },

    async post(url: string, params: Object): Promise<Response> {
        function getCookie(name: string): string {
            let cookieValue = '';
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
        const headers =  {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        };
        const cred: RequestCredentials = 'include';
        const correctedUrl = (url.startsWith('api/') ? '' : 'api/') + url + (url.endsWith('/') ? '' : '/');
        const data = JSON.stringify(params);
        const mode = apiUrl.includes('localhost') ? 'cors' : 'same-origin';
        const resp = await fetch(
            apiUrl + correctedUrl,
            { method: 'POST', headers: headers, mode: mode, credentials: cred, body: data }
        ).then((response) => response.json());
        return resp;
    },

    async init(): Promise<AuthProvider> {
        const resp = await this.get('auth', {});
        if (resp && resp.ok && resp.username) {
            auth.username = resp.username;
            auth.isAuthenticated = true;
        }
        return auth;
    },

    async demo(): Promise<Response> {
        const params = {'grant_type': 'password'};
        const resp = await this.post('demo', params);
        if (resp && resp.ok && resp.info) {
          auth.username = resp.info;
          auth.isAuthenticated = true;
        }
        return resp;
    },
    
    async login(username: string, password: string): Promise<Response> {
        const params = {
            'grant_type': 'password',
            'username': username,
            'password': password,
        };
        const resp = await this.post('login', params);
        if (resp && resp.ok && resp.info) {
          auth.username = resp.info;
          auth.isAuthenticated = true;
        }
        return resp;
    },

    async logout(): Promise<void> {
        const resp = await this.get('logout', {});
        if (resp && resp.ok) {
          auth.isAuthenticated = false;
          auth.username = '';
        }
    },
};
