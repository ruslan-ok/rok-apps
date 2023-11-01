import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";

import Demo from './components/auth/Demo';
import Login, { action as loginAction } from './components/auth/Login';
import Logout from './components/auth/Logout';
import HeadedPage, { loader as appLoader } from './components/HeadedPage';
import MainPage, { loader as mainPageLoader } from './components/MainPage';

let router = createBrowserRouter([
  {
    id: 'header',
    path: '/:lang?',
    loader: appLoader,
    Component: HeadedPage,
    children: [
      {
        index: true,
        Component: MainPage,
        loader: mainPageLoader,
      },
    ],
  },
  {
    path: '/:lang?/demo',
    Component: Demo,
  },
  {
    path: '/:lang?/login',
    action: loginAction,
    Component: Login,
  },
  {
    path: '/:lang?/logout',
    Component: Logout,
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

