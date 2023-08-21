import {
  createBrowserRouter,
  Outlet,
  RouterProvider,
} from "react-router-dom";

import { appAuthProvider as auth, loginAction, logoutAction } from './components/Auth';
import Login from './components/Login';
import MainPage, { loader as mainPageLoader } from './components/MainPage';

let router = createBrowserRouter([
  {
    id: 'root',
    path: '/:lang?/react',
    loader: auth.init,
    Component: Outlet,
    children: [
      {
        index: true,
        Component: MainPage,
        loader: mainPageLoader,
      },
    ],
  },
  {
    path: '/:lang?/react/login',
    action: loginAction,
    Component: Login,
  },
  {
    path: '/:lang?/react/logout',
    loader: logoutAction,
    element: <p></p>,
  },
]);

if (import.meta.hot) {
  import.meta.hot.dispose(() => router.dispose());
}

export default function App() {
  return <RouterProvider router={router} fallbackElement={<Fallback />} />;
}

export function Fallback() {
  return <p>Performing initial data load</p>;
}

