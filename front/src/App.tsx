import { useEffect } from "react";
import {
  createBrowserRouter,
  RouterProvider,
  useNavigate,
} from "react-router-dom";

import { loginAction, logoutAction } from './components/Auth';
import Login from './components/Login';
import HeadedPage, { loader as appLoader } from './components/HeadedPage';
import MainPage, { loader as mainPageLoader } from './components/MainPage';
import CurrencyAnalyse, { loader as currencyLoader } from './components/CurrencyAnalyse';

function FirstPage() {
  const navigate = useNavigate();
  useEffect(() => {
    navigate('/react');
  }, []);
  return <></>;
}

let router = createBrowserRouter([
  {
    path: '/:lang?/',
    Component: FirstPage,
  },
  {
    id: 'root',
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

