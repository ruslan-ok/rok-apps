import { 
  redirect,
} from "react-router-dom";

export const apiUrl: string = 'http://localhost:8000/en-gb/';

export interface AuthProvider {
  username: null | string;
  isAuthenticated: null | boolean;
  init(): Promise<AuthProvider>;
  signin(username: string, password: string): Promise<Response>;
  signout(): Promise<void>;
}
  
export const appAuthProvider: AuthProvider = {
  username: null,
  isAuthenticated: null,

  async init(): Promise<AuthProvider> {
    const token = getCookie('accessToken');
    if (!token) {
      appAuthProvider.username = null;
      appAuthProvider.isAuthenticated = false;
    }
    else {
      const data = `accessToken=${token}`;
      const resp = await fetch(apiUrl + 'api/react/check_token', { method: 'POST', headers: {'Content-type': 'application/x-www-form-urlencoded'}, body: data }).then((response) => response.json());
      if (resp && resp.ok && resp.username) {
        appAuthProvider.username = resp.username;
        appAuthProvider.isAuthenticated = true;
      }
    }
    return appAuthProvider;
  },

  async signin(username: string, password: string): Promise<Response> {
    const data = `grant_type=password&username=${username}&password=${password}`;
    const resp = await fetch(apiUrl + 'api/react/login', { method: 'POST', headers: {'Content-type': 'application/x-www-form-urlencoded'}, body: data }).then((response) => response.json());
    if (resp && resp.ok && resp.username) {
      appAuthProvider.username = resp.username;
      appAuthProvider.isAuthenticated = true;
      setCookie('accessToken', resp.accessToken, resp.expires);
    }
    return resp;
  },

  async signout(): Promise<void> {
    const resp = await fetch(apiUrl + 'api/react/logout', { method: 'GET', headers: {'Content-type': 'application/json'} }).then((response) => response.json());
    if (resp && resp.ok) {
      appAuthProvider.isAuthenticated = false;
      appAuthProvider.username = '';
      setCookie('accessToken', '', 0);
    }
  }
};

export function demo() {
  console.log('demo();');
  return redirect('/react');
}
/*
async function demo() {
  console.log('demo();');
  const apiUrl = '/api/react/demo';
  console.log(apiUrl);
  const options = {
    method: 'GET',
    headers: {
      'Content-type': 'application/json',
    },
  }

  fetch(apiUrl, options)
    .then((response) => response.json())
    .then((data) => {
      console.log(data.user);
    });

  return null;
}
*/

export async function logout() {
  console.log('logout();');
  await appAuthProvider.signout();
  return redirect('/react');
}

function setCookie(cname: string, cvalue: string, exdays: number) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  let expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname: string) {
  let name = cname + "=";
  let ca = document.cookie.split(';');
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}
import type {
  ActionFunctionArgs 
} from "react-router-dom";

export interface postResponse {
  ok: boolean,
  info: string
}

export async function logoutAction() {
  await appAuthProvider.signout();
  return redirect('/react');
}

export async function loginAction({ request }: ActionFunctionArgs): Promise<postResponse | Response> {
  let response: postResponse = {
    ok: false,
    info: 'Unknown error.'
  };

  const formData = await request.formData();
  const username = formData.get("username") as string | null;
  const password = formData.get("password") as string | null;

  // Validate our form inputs and return validation errors via useActionData()
  if (!username || !password) {
    response.info = 'You must provide a username and password to log in.';
    return response;
  }

  try {
    const tmp: any = await appAuthProvider.signin(username, password);
    response.ok = tmp.ok;
    response.info = tmp.info;
    if (!tmp.info && tmp.username) {
      response.info = tmp.username;
    }
  } catch (error) {
    // Unused as of now but this is how you would handle invalid
    // username/password combinations - just like validating the inputs
    // above
    response.info = 'Invalid login attempt.';
  }

  if (response && response.ok) {
    let redirectTo = (formData.get("redirectTo") || "/react") as string;
    return redirect(redirectTo);
  }

  return response;
}

export function getAccessToken() {
  return getCookie('accessToken');
}