import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import DefaultSpinner from './components/DefaultSpinner';
import HeadedPage, { loader as appLoader } from './components/HeadedPage';
import MainPage from './components/MainPage';
import Demo from './components/auth/Demo';
import Login, { action as loginAction } from './components/auth/Login';
import Logout from './components/auth/Logout';
import TodoPage, { loader as todoLoader } from './components/todo/TodoPage';

import './components/main.css'

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
            },
            {
                path: 'todo',
                Component: TodoPage,
                loader: todoLoader,
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

export default function App() {
    return <RouterProvider router={router} fallbackElement={<Fallback />} />;
}

export function Fallback() {
    return <DefaultSpinner />;
}
