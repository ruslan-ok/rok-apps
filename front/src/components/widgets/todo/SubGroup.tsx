import type { Todo } from './TodoItem';
import TodoItem from './TodoItem';
import './SubGroup.css';

const subGroupIDs = ['none', 'completed', 'earler', 'today', 'tomorrow', 'onWeek', 'later'] as const;

type SubGroupID = typeof subGroupIDs[number];

export const subGroupLabels: Record<SubGroupID, string> = {
    none: '',
    completed: 'Completed',
    earler: 'Earler',
    today: 'Today',
    tomorrow: 'Tomorrow',
    onWeek: 'On the week',
    later: 'Later',
} as const;

const subGroupOrders: Record<string, number> = {
    'none': 0,
    'completed': 1,
    'earler': 2,
    'today': 3,
    'tomorrow': 4,
    'onWeek': 5,
    'later': 6,
} as const;

function getSubGroupId(todo: Todo): SubGroupID {

    if (todo.completed) {
        return 'completed';
    }

    if (!todo.stop) {
        return 'none';
    }

    const today = new Date();
    const factor = 1000 * 3600 * 24;
    const eventDays = Math.floor(todo.stop.getTime() / factor);
    const todayDays = Math.floor(today.getTime() / factor);
    const days = eventDays - todayDays;

    if (days < 0) {
        return 'earler';
    }
    
    if (days == 0) {
        return 'today';
    }
    
    if (days == 1) {
        return 'tomorrow';
    }
    
    if (days < 8) {
        return 'onWeek';
    }
    
    return 'later';
}

export interface SubGroupInfo {
    id: SubGroupID;
    name: string;
    isOpen: boolean;
    items: Todo[];
    order: number;
}

export function buildSubGroupList(items: any[]): SubGroupInfo[] {
    let subGroups: SubGroupInfo[] = [];
    items.forEach((todoInfo: any) => {
        const todo: Todo = {
            id: todoInfo.id,
            name: todoInfo.name,
            stop: new Date(todoInfo.stop),
            url: todoInfo.url,
            group: todoInfo.group,
            completed: todoInfo.completed,
            inMyDay: todoInfo.in_my_day,
            important: todoInfo.important,
            remind: new Date(todoInfo.remind),
            repeat: todoInfo.repeat,
            repeatNum: todoInfo.repeat_num,
            repeatDays: todoInfo.repeat_days,
            categories: todoInfo.categories,
            info: todoInfo.info,
            steps: todoInfo.steps.map((stepInfo: any) => {
                return {
                    id: stepInfo.id, 
                    created: new Date(stepInfo.created), 
                    name: stepInfo.name, 
                    sort: stepInfo.sort, 
                    completed: stepInfo.completed
                };
            }),
        };
        const subGroupId: SubGroupID = getSubGroupId(todo);
        const subGroupName = subGroupLabels[subGroupId];
        const subGroupOrder: number = subGroupOrders[subGroupId];
        const sg = subGroups.filter((x: SubGroupInfo) => x.id == subGroupId);
        if (sg.length) {
            sg[0].items.push(todo);
        } else {
            const sg: SubGroupInfo = {
                id: subGroupId,
                name: subGroupName,
                isOpen: true,
                items: [todo],
                order: subGroupOrder,
            };
            subGroups.push(sg);
        }
    });
    const sortedSubGroups = subGroups.sort((a,b) => (a.order > b.order) ? 1 : ((b.order > a.order) ? -1 : 0));
    return sortedSubGroups;
}

export default function SubGroup({data, doRedraw}: {data: SubGroupInfo, doRedraw: () => void }) {
    let subGroupItems;
    if (data.isOpen) {
        subGroupItems = data.items.map((todo: Todo) => {
            return <TodoItem key={todo.id} todo={todo} doRedraw={doRedraw} />
        });
    }
    return (
        <div className='sub-group-container' id='sub-group'>
            <span className='sub-group'>{data.name}</span>
            {subGroupItems}
        </div>
    );
}
