import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import DefaultSpinner from './components/DefaultSpinner';
import ErrorPage from "./error_page";
import HeadedPage, { loader as appLoader } from './components/HeadedPage';
import MainPage from './components/MainPage';
import Demo from './components/auth/Demo';
import Login, { action as loginAction } from './components/auth/Login';
import Logout from './components/auth/Logout';
import TodoPage, { loader as todoLoader } from './components/todo/TodoPage';
import TodoListPage from './components/todo/TodoListPage';
import TodoItemPage from './components/todo/TodoItemPage';

import './components/main.css';
import './components/css/error_page.min.css';

let router = createBrowserRouter([
    {
        id: 'header',
        path: '/',
        // path: '/:lang?',
        loader: appLoader,
        Component: HeadedPage,
        children: [
            {
                path: '',
                index: true,
                Component: MainPage,
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
                    },
                ],
            },
        ],
        errorElement: <ErrorPage />,
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
