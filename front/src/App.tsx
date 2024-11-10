import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import ErrorPage from "./ErrorPage";
import Demo from './auth/Demo';
import Login, { action as loginAction } from './auth/Login';
import Logout from './auth/Logout';

import HeadedPage from './pages/HeadedPage';
import { loader as headLoader } from './pages/Header';
import MainPage from './pages/MainPage';

import TodoPage, { loader as todoLoader } from './pages/todo/TodoPage';
import TodoListPage from './pages/todo/TodoListPage';
import TodoItemPage, { loader as todoItemLoader, action as todoItemAction } from './pages/todo/TodoItemPage';

import 'bootstrap/dist/css/bootstrap.css';
import './css/App.min.css';


let router = createBrowserRouter([
    {
        path: '',
        Component: HeadedPage,
        loader: headLoader,
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
]);

export default function App() {
    return <RouterProvider router={router} fallbackElement={<Fallback />} />;
}

export function Fallback() {
    return <span>Loading...</span>;
}
