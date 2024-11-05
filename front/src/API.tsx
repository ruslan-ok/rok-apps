import type { MouseEvent } from 'react'

function getApiUrl(): string {
    const parts = window.location.pathname.split('/');
    const baseUrl: string = window.location.protocol + '//' + window.location.host + '/' + (parts[1] ? parts[1] + '/' : '');
    if (baseUrl.includes('localhost:3000'))
        return 'http://localhost:8000/';
    return baseUrl;
}

const apiUrl: string = getApiUrl();

interface IAPIProvider {
    username: null | string;
    isAuthenticated: null | boolean;
    buttonData(event: MouseEvent<HTMLElement>, attributes: string[]): Object;
    objectToUrlParams(obj: Object): string;
    free_get(url: string, params: Object): Promise<Response>;
    modify(method: string, url: string, params: Object): Promise<Response>;
    get(url: string, params: Object): Promise<Response>;
    post(url: string, params: Object): Promise<Response>;
    put(url: string, params: Object): Promise<Response>;
    options(url: string): Promise<Response>;
    init(): Promise<IAPIProvider>;
}
  
export const api: IAPIProvider = {
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
      
    async free_get(url: string, params: Object): Promise<Response> {
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

    async modify(method: string, url: string, params: Object): Promise<Response> {
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
        let urlParams, data: string | undefined;
        if (method === 'OPTIONS') {
            urlParams = '';
            data = undefined;
        } else if (method === 'GET') {
            urlParams = this.objectToUrlParams(params);
            data = undefined;
        } else {
            urlParams = '';
            data = JSON.stringify(params);
        }
        const mode = apiUrl.includes('localhost') ? 'cors' : 'same-origin';
        const resp = await fetch(
            apiUrl + correctedUrl + urlParams,
            { method: method, headers: headers, mode: mode, credentials: cred, body: data }
        ).then((response) => response.json());
        return resp;
    },

    async get(url: string, params: Object): Promise<Response> {
        return await this.modify('GET', url, params);
    },

    async post(url: string, params: Object): Promise<Response> {
        return await this.modify('POST', url, params);
    },

    async put(url: string, params: Object): Promise<Response> {
        return await this.modify('PUT', url, params);
    },

    async options(url: string): Promise<Response> {
        return await this.modify('OPTIONS', url, {});
    },

    async init(): Promise<IAPIProvider> {
        const resp = await this.free_get('auth', {});
        if (resp && resp.ok && resp.username) {
            api.username = resp.username;
            api.isAuthenticated = true;
        }
        return api;
    },
};
