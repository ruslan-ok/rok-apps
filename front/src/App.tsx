import {
    createBrowserRouter,
    RouterProvider,
} from "react-router-dom";

import HeadedPage, { loader as appLoader } from './components/HeadedPage';
import MainPage, { loader as mainPageLoader } from './components/MainPage';
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
                loader: mainPageLoader,
            },
        ],
    },
]);

export default function App() {
    return <RouterProvider router={router} fallbackElement={<Fallback />} />;
}

export function Fallback() {
    return <p>Performing initial data load</p>;
}
