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
    return <a className='todo-item' href={ todo.url }>{ event }: { todo.name } - { todo.group.name }</a>
}