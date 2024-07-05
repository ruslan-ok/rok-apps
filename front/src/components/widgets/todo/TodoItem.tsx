import './TodoItem.css';
import { apiUrl } from '../../auth/Auth';

interface Step {
    id: number;
    name: string;
    created: Date;
    completed: boolean;
    sort: string;
}

interface Group {
    id: number;
    name: string;
}

export interface Todo {
    id: number;
    name: string;
    stop: Date;
    url: string;
    group: Group;
    completed: boolean;
    inMyDay: boolean;
    important: boolean;
    remind: Date;
    repeat: number;
    repeatNum: number;
    repeatDays: number;
    categories: string;
    info: string;
    steps: Step[];
}

export default function TodoItem({ todo, doRedraw }: { todo: Todo, doRedraw: () => void }) {
    const event = todo.stop.toLocaleDateString().replace('/', '.').replace('/', '.');

    async function toggle(method: string, id: number) {
        const url = apiUrl + `api/tasks/${id}/${method}/?format=json`;
        const cred: RequestCredentials = 'include';
        const options = {
            method: 'GET',
            headers: { 'Content-type': 'application/json' },
            credentials: cred,
        };
        const response = await fetch(url, options);
        if (response.ok) {
            let resp_data = await response.json();
            if (resp_data) {
                doRedraw();
            }
        }
    }

    function toggleCompleted(event: any) {
        const id = event.currentTarget.parentNode.dataset.id;
        toggle('completed', id);
    }

    function toggleImportant(event: any) {
        const id = event.currentTarget.parentNode.dataset.id;
        toggle('important', id);
    }

    return (
        <div className='todo-item' data-id={todo.id}>
            <button type="button" className="left-icon" onClick={toggleCompleted}>
                <i className="bi-circle"></i>
            </button>
            <a className='container' href={todo.url}>
                <div className='info'>
                    <span className='name'>
                        {todo.name}
                        <span className='roles'>
                            <object><a href={todo.url} className="role-icon"><i className="bi-check2-square"></i></a></object>
                        </span>
                    </span>
                    <div className='descr'>
                        <div className='inline'>{event}</div>
                        <div className='inline'>{todo.group.name}</div>
                    </div>
                </div>
            </a>
            <button type="button" className="right-icon" onClick={toggleImportant}>
                {todo.important ? (
                    <i className="bi-star-fill"></i>
                ) : (
                    <i className="bi-star"></i>
                )}
            </button>
        </div>
    )
}