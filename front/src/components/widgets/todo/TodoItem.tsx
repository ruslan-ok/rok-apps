import './TodoItem.css';

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

export default function TodoItem({todo}: {todo: Todo}) {
    const event = todo.stop.toISOString().split('T')[0]
    return (
        <div className='todo-item'>
            <button type="button" className="left-icon">
                <i className="bi-circle"></i>
            </button>
            <a className='container' href={ todo.url }>
                <div className='info'>
                    <span className='name'>
                        { todo.name }
                        <span className='roles'>
                            <object><a href={ todo.url } className="role-icon"><i className="bi-check2-square"></i></a></object>
                        </span>
                    </span>
                    <div className='descr'>
                        <div className='inline'>{ event }</div>
                        <div className='inline'>{ todo.group.name }</div>
                    </div>
                </div>
            </a>
            <button type="button" className="right-icon">
                <i className="bi-star"></i>
            </button>
        </div>
    )
}