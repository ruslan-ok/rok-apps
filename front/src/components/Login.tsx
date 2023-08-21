import type { postResponse } from './Auth'

import { 
  Form, 
  Link,
  useActionData,
  useLocation,
  useNavigation,
} from 'react-router-dom';

import './Login.css';

function Login() {
  let location = useLocation();
  let params = new URLSearchParams(location.search);
  let from = params.get("from") || "/react";

  let navigation = useNavigation();
  let isLoggingIn = navigation.formData?.get("username") != null;

  const actionData = useActionData() as postResponse;

  return (
    <div className="form-container">
      <Form method="post">
        <input type="hidden" name="csrfmiddlewaretoken" value="A0X0GHln6RqbYK1Lp0JUk3tn2jE7JhYpL6x9xSAhruRl4BvgPDU1XMlMPpAQw83G" />
        <input type="hidden" name="redirectTo" value={from} />
        <img className="mb-4" src="/static/favicon.ico" />
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
          <Link to="/react/password_reset">Forgotten your password or username?</Link>
        </div>
        <div className="password-reset-link">
          <Link to="/react/register">Register</Link>
        </div>
      </Form>
    </div>
  );
};

export default Login;