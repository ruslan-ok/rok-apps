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
import { api } from '../API'

interface ILoginResult {
    ok: boolean,
    info: string
}
  
export async function action({ request }: ActionFunctionArgs): Promise<ILoginResult | Response>  {
    let response: ILoginResult = {
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
        const params = {
            'grant_type': 'password',
            'username': username,
            'password': password,
        };
        response = await api.post('login', params);
        if (response && response.ok && response.info) {
            api.username = response.info;
            api.isAuthenticated = true;
        }
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
  
    const actionData = useActionData() as ILoginResult;

    useEffect(() => {
        async function csrf_setup() {
            await api.free_get('csrf_setup', {});
        }
        
        csrf_setup();
    }, []);
    
    return (
      <div className="dialog-form form-container rok-login">
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
          <button className="primary w-100 btn btn-primary" type="submit" disabled={isLoggingIn}>Login</button>
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