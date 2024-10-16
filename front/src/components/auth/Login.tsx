import { useEffect } from "react";

import {
    Link,
    Form,
    ActionFunctionArgs,
    redirect,
    useActionData,
    useLocation,
    useNavigation,
} from "react-router-dom";

import { auth as api } from './Auth';

import './Login.css';

export interface LoginResult {
    ok: boolean,
    info: string
}
  
export async function action({ request }: ActionFunctionArgs): Promise<LoginResult | Response>  {
    let response: LoginResult = {
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
        const tmp: any = await api.login(username, password);
        response = tmp;
    } catch (error) {
        // Unused as of now but this is how you would handle invalid
        // username/password combinations - just like validating the inputs
        // above
        response.info = 'Invalid login attempt.';
    }
  
    if (response && response.ok) {
        let redirectTo = (formData.get("redirectTo") || "/") as string;
        return redirect(redirectTo);
    }
  
    return response;
}
  
function Login() {
    let location = useLocation();
    let params = new URLSearchParams(location.search);
    let from = params.get("from") || "/";
  
    let navigation = useNavigation();
    let isLoggingIn = navigation.formData?.get("username") != null;
  
    const actionData = useActionData() as LoginResult;

    useEffect(() => {
        async function csrf_setup() {
            await api.get('csrf_setup', {});
        }
        
        csrf_setup();
    }, []);
    
    return (
      <div className="form-container rok-login">
        <Form method="post">
          <input type="hidden" name="csrfmiddlewaretoken" value="A0X0GHln6RqbYK1Lp0JUk3tn2jE7JhYpL6x9xSAhruRl4BvgPDU1XMlMPpAQw83G" />
          <input type="hidden" name="redirectTo" value={from} />
          <img className="mb-4" src="/static/favicon.ico" alt="favicon" />
          <h1 className="h3 mb-3 fw-normal">Log in</h1>
          {actionData && !actionData.ok && actionData.info ? (
            <div className="fieldset">
              <p className="errornote">{actionData?.info}</p> 
            </div>
          ) : null}
          <div className="form-floating">
            <input type="text" name="username" className="form-control" autoCapitalize="none" autoComplete="username" maxLength={150} required={true} id="id_username" />
            <label htmlFor="id_username">Username:</label>
          </div>
          <div className="form-floating">
            <input type="password" name="password" autoComplete="current-password" className="form-control" required={true} id="id_password" />
            <label htmlFor="id_password">Password:</label>
          </div>
          <button className="primary" type="submit" disabled={isLoggingIn}>Login</button>
          <div className="password-reset-link">
            <Link to="/password_reset">Forgotten your password or username?</Link>
          </div>
          <div className="password-reset-link">
            <Link to="/register">Register</Link>
          </div>
        </Form>
      </div>
    );
};
  
export default Login;