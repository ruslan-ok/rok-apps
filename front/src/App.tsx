import {
    createBrowserRouter,
    RouterProvider,
    Outlet,
} from "react-router-dom";

import DefaultSpinner from './components/DefaultSpinner';
import ErrorPage from "./error_page";
import HeadedPage4, { loader as appLoader } from './components/HeadedPage';
import MainPage4 from './components/MainPage';
import Demo from './components/auth/Demo';
import Login, { action as loginAction } from './components/auth/Login';
import Logout from './components/auth/Logout';
import TodoPage, { loader as todoLoader } from './components/todo/TodoPage';
import TodoListPage from './components/todo/TodoListPage';
import TodoItemPage, { loader as todoItemLoader, action as todoItemAction } from './components/todo/TodoItemPage';

import HeadedPage from './v5/HeadedPage';
import { loader as headLoader } from './v5/Header';
import MainPage from './v5/MainPage';



let router = createBrowserRouter([
    {
        id: 'header',
        path: '/',
        // path: '/:lang?',
        loader: appLoader,
        Component: HeadedPage4,
        children: [
            {
                path: '',
                index: true,
                Component: MainPage4,
            },
            {
                path: 'todo',
                Component: TodoPage,
                loader: todoLoader,
                children: [
                    {
                        path: '',
                        Component: TodoListPage,
                    },
                    {
                        path: ':id',
                        Component: TodoItemPage,
                        loader: todoItemLoader,
                        action: todoItemAction,
                    },
                ],
            },
        ],
        errorElement: <ErrorPage />,
    },
    {
        path: '/demo',
        Component: Demo,
    },
    {
        path: '/login',
        action: loginAction,
        Component: Login,
    },
    {
        path: '/logout',
        Component: Logout,
    },
    {
        path: '/v5',
        Component: Outlet,
        children: [
            {
                path: '',
                Component: HeadedPage,
                loader: headLoader,
                children: [
                    {
                        path: '',
                        Component: MainPage,
                    },
                ],
            },
            {
                path: 'demo',
                Component: Demo,
            },
            {
                path: 'login',
                action: loginAction,
                Component: Login,
            },
            {
                path: 'logout',
                Component: Logout,
            },
            {
                path: 'profile',
                Component: Logout,
            },
        ],
    },
]);

export default function App() {
    return <RouterProvider router={router} fallbackElement={<Fallback />} />;
}

export function Fallback() {
    return <DefaultSpinner />;
}
