import { useState, useEffect } from 'react';
import './Todo.css';

export default function Todo() {
    const [widgetWidth, setWidgetWidth] = useState(300);

    useEffect(() => {
        updateDimensions();
        window.addEventListener("resize", updateDimensions);
        return () => window.removeEventListener("resize", updateDimensions);
    }, [])

    const updateDimensions = () => {
        const el = document.getElementById('widget-container');
        if (el) {
            setWidgetWidth(el.offsetWidth);
        }
    };

    return (
        <div className='widget-container' id='todo'>
            <div className='widget-content'>
                <p>widgetWidth = {widgetWidth}</p>
            </div>
        </div>
    );
}