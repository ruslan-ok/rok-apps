import { useEffect } from "react";
import {
  createBrowserRouter,
  RouterProvider,
  useNavigate,
} from "react-router-dom";

import Demo from './components/auth/Demo';
import Login, { action as loginAction } from './components/auth/Login';
import Logout from './components/auth/Logout';
import HeadedPage, { loader as appLoader } from './components/HeadedPage';
import MainPage, { loader as mainPageLoader } from './components/MainPage';
import CurrencyAnalyse, { loader as currencyLoader } from './components/CurrencyAnalyse';

function Root() {
  const navigate = useNavigate();
  useEffect(() => {
    navigate('/react');
  }, []);
  return <></>;
}

let router = createBrowserRouter([
  {
    path: '/:lang?/',
    Component: Root,
  },
  {
    id: 'header',
    path: '/:lang?/react',
    loader: appLoader,
    Component: HeadedPage,
    children: [
      {
        index: true,
        Component: MainPage,
        loader: mainPageLoader,
      },
      {
        path: 'currency',
        Component: CurrencyAnalyse,
        loader: currencyLoader,
      },
    ],
  },
  {
    path: '/:lang?/react/demo',
    Component: Demo,
  },
  {
    path: '/:lang?/react/login',
    action: loginAction,
    Component: Login,
  },
  {
    path: '/:lang?/react/logout',
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

