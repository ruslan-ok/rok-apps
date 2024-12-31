import { useState } from 'react';
import { LoaderFunctionArgs, useOutletContext, useLoaderData, Form, redirect } from "react-router-dom";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import { IDateTime, IItemInfo } from './ItemTypes';
import ItemName from './fields/ItemName';
import ItemSteps from './fields/ItemSteps';
import ItemDates from './ItemDates';
import ItemInfo from './fields/ItemInfo';
import ItemGroup from './fields/ItemGroup';
import ItemCategories from './fields/ItemCategories';
import ItemLinks from './fields/ItemLinks';
import ItemFiles from './fields/ItemFiles';
import PageTitle from './PageTitle';


function delItemConfirm() {
    console.log('delItemConfirm');
}

type ITodoItemPageParams = {
    id: string;
}

async function saver(id: number, values: Object) {
    await api.put(`todo/${id}`, values);
    // console.log(`saved: id=${id}, values=${JSON.stringify(values)}`);
}

export async function action({request, params}: {request: Request; params: ITodoItemPageParams;}) {
    const formData = await request.formData();
    const id = +params.id;
    const name = formData.get('name');
    const info = formData.get('info');
    const stop = formData.get('stop');
    await saver(id, {name: name, info: info, stop: stop});
    return {};
}

export async function loader({ params }: LoaderFunctionArgs) {
    const data = await api.get(`todo/${params.id}`, {});
    if (JSON.stringify(data) === JSON.stringify({detail: 'No Task matches the given query.'}))
        return redirect('/todo');
    const item: IItemInfo = new IItemInfo(data);
    return item;
}
  
function TodoItemPage() {
    const config = useOutletContext() as IPageConfig;
    const itemData = useLoaderData() as Object;
    const item = new IItemInfo(itemData);
    const [theItem, setItem] = useState(item);
    const [changed, setChanged] = useState(false);

    function onlyEditableFields(values: Object): boolean {
        let result = true;
        const editableFields = new Set(['name', 'info', 'stop']);
        for (const key in values) {
            if (!editableFields.has(key)) {
                result = false;
                break;
            }
        }
        return result;
    }

    async function changeTracker(values: Object) {
        if (onlyEditableFields(values)) {
            const newItem = Object.assign(theItem, values);
            setItem(newItem);
            setChanged(true);
        } else {
            let newValues = values;

            if (item.name !== theItem.name)
                newValues = Object.assign(newValues, {name: theItem.name});
            if (item.info !== theItem.info)
                newValues = Object.assign(newValues, {info: theItem.info});
            if (item.stop !== theItem.stop)
                newValues = Object.assign(newValues, {stop: theItem.stop});

            for (const key in newValues) {
                if (key.startsWith('set_')) {
                    const newKey = key.replace('set_', '');
                    newValues[newKey] = newValues[key];
                    delete newValues[key];
                }
            }

            await saver(item.id, newValues);
            setChanged(false);
        }
    }

    const itemCreated = new IDateTime(item.created).strftime('%d %b %Y, %H:%M');
    const itemCompleted = new IDateTime(item.completion).strftime('%d %b %Y, %H:%M');
    if (!item)
        return <></>;
    return (
        <div className="item-form px-2" id="article_form" data-item_id={item.id}>
            <PageTitle config={config} setTheme={()=>{}} />
            <Form method="post" encType="multipart/form-data">
                <ItemName completed={item.completed} name={item.name} important={item.important} onChange={changeTracker} />
                <ItemSteps steps={item.steps} />
                <ItemDates item={item} onChange={changeTracker} />
                <div className="row g-3">
                    <ItemInfo info={item.info} />
                    <ItemGroup group_id={item.group_id} groups={item.groups} />
                    <ItemCategories categories={item.categories} />
                </div>
                <div className="row">
                    <ItemLinks links={item.links} />
                    <ItemFiles files={item.files} />
                </div>

                <div className="d-flex justify-content-evenly mt-3 pb-5">
                    <button type="submit" className="btn btn-primary bi-save" title="Save changes" disabled={!changed} >
                        <span className="px-2">Save</span>
                    </button>
                    <button type="button" className="btn btn-secondary bi-x" title="Close edit form">
                        <span className="px-2">Close</span>
                    </button>
                    <button type="button" className="btn btn-danger bi-trash" onClick={delItemConfirm} title="Delete record">
                        <span className="px-2">Delete</span>
                    </button>
                </div>

                <div className="row">
                    <div className="col">Created: {itemCreated}</div>
                    {item.completed &&
                        <div className="col">Completed: {itemCompleted}</div>
                    }
                </div>
            </Form>
        </div>
    );
}
  
export default TodoItemPage;