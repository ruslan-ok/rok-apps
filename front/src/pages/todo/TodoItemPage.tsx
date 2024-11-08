import { ChangeEvent, useState } from 'react';
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
// import '../css/widgets.min.css';
// import '../css/todo.min.css';

export function getStrId(prefix: string, id: number): string {
    return `${prefix}_${id}`;
}

export function extraClass(prefix: string, condition: boolean, extraClass: string): string {
    return prefix + (condition ? ` ${extraClass}` : '');
}

function editFolder(event: ChangeEvent<HTMLInputElement>) {
    console.log('editFolder');
}

function delFolderConfirm() {
    console.log('delFolderConfirm');
}

function saveFolder() {
    console.log('saveFolder');
}

function addItemKeyDowm() {
    console.log('addItemKeyDowm');
    // "if (event.keyCode == 13) document.getElementById('id_add_item_button_{{ screen_size }}').click()"
}

function addItem() {
    console.log('addItem');
    // addItem('{{ config.app }}', '{{ config.get_cur_role }}', {{ config.cur_view_group.id|escape }}, '{{ screen_size }}')
}

function AddItemInput({config}: {config: IPageConfig}) {
    return (<>
        <div className="dropdown mx-3">
            <button className={config.checkDark('btn bi-plus-lg')} type="button" id="dropdownMenuButton1" data-bs-toggle="dropdown" aria-expanded="false" />
            <ul className="dropdown-menu shadow-lg" aria-labelledby="dropdownMenuButton1">
                <div className="d-flex py-2">
                    <input type="text" name="add_item_name" maxLength={200} id="id_add_item_name" className="add-item-name"
                    placeholder={config.add_item?.placeholder} onKeyDown={addItemKeyDowm} />
                    <div className="btn btn-primary ms-2" id="id_add_item_button" onClick={addItem}>
                        Add
                    </div>
                </div>
            </ul>
        </div>
    </>);
}

function ItemTitle({item, config}: {item: IItemInfo, config: IPageConfig}) {
    return (
        <div className="content-title d-flex justify-content-between">
            <div className="title d-none d-md-flex">
                {config.icon && <i className={config.iconClass}></i>}

                <h3 className={config.checkDark('content-title__text')}>
                    {config.isFolder ? <>
                        <span>{config.folderPath}</span>
                        <span id="id_folder_view" className="folder_view">{config.entity.name}</span>
                        <span id="id_folder_edit" className="folder_edit d-none">
                            <input type="text" name="file_name" size="15" maxLength={100} defaultValue="zzz" />
                        </span>
                    </> : 
                    <>{item.name}</>}
                </h3>
                {config.isFolder && <>
                    <button id="id_folder_edit_btn" className="bi-pen btn folder-mod-btn" onClick={editFolder} />
                    <button id="id_folder_del_btn" className="bi-trash btn folder-mod-btn" onClick={delFolderConfirm} />
                    <button id="id_folder_save_btn" className="bi-save btn folder-mod-btn d-none" onClick={saveFolder} />
                    <span id="id_edit_folder_error" className="d-none errornote">Error Description</span>
                </>}

            </div>
            <div className="title d-md-none"></div>
            <div className="actions d-flex mx-2">
                {/* {% include "core/tune.html" with screen_size="small" %} */}
                {config.add_item && <AddItemInput config={config} />}
            </div>
        </div>
    );
}

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
            <ItemTitle item={item} config={config} />
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