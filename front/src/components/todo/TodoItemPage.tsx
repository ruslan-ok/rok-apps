import { ChangeEvent } from 'react';
import { LoaderFunctionArgs, useOutletContext, useLoaderData } from "react-router-dom";
import { api } from '../../API'
import { IPageConfig } from '../PageConfig';
import { IItemInfo } from './ItemTypes';
import '../css/widgets.min.css';

function editFolder(event: ChangeEvent<HTMLInputElement>) {
    console.log('editFolder');
}

function delFolderConfirm() {
    console.log('delFolderConfirm');
}

function saveFolder() {
    console.log('saveFolder');
}

function AddItem({config}: {config: IPageConfig}) {
    return <div className="btn bi-plus dark-theme"></div>;
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
                            <input type="text" name="file_name" size="15" maxLength={100} value="zzz" />
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
                {config.add_item && <AddItem config={config} />}
            </div>
        </div>
    );
}

function FormErrors() {
    return <></>;
}

function checkCompleted() {
    console.log('checkCompleted');
}

function Completed({item}: {item: IItemInfo}) {
    return (
        <div className="form-check completed-checkbox">
            <input type="checkbox" name="completed" id="id_completed"
                className="form-check-input" onChange={checkCompleted}
                checked={item.completed} />
        </div>
    );
}

function nameChanged() {
    console.log('nameChanged');
}

function ItemName({item}: {item: IItemInfo}) {
    return <input type="text" name="name" defaultValue={item.name} className="form-control mb-3" maxLength={200} id="id_name" onChange={nameChanged} />;
}

function importantChanged() {
    console.log('importantChanged');
}

function Important({item}: {item: IItemInfo}) {
    const iconClass = 'bi-star' + (item.important ? '-fill' : '');
    return (
        <button type="button" onClick={importantChanged} id="toggle-important" className="btn-important" >
            <i className={iconClass} />
        </button>
    );
}

function completeStep() {
    console.log('completeStep');
}

function editStep(event: ChangeEvent<HTMLInputElement>) {
    console.log(`editStep(${event})`);
}

function delStepConfirm() {
    console.log('delStepConfirm');
}

function addStep() {
    console.log('addStep');
}

function getStrId(prefix: string, id: number): string {
    return `${prefix}_${id}`;
}

function extraClass(prefix: string, condition: boolean, extraClass: string): string {
    return prefix + (condition ? ` ${extraClass}` : '');
}

function TodoSteps({item}: {item: IItemInfo}) {
    const stepList = item.steps.map(step => {
        return (
            <div key={step.id} className="field-group mx-2">
                <div className="form-check small-completed-checkbox">
                    <input type="checkbox" data-step_id={step.id} name="step_completed" id={getStrId('step_complete', step.id)}
                        className="form-check-input small-checkbox" defaultChecked={step.completed} onClick={completeStep} />
                </div>
                <input type="text" data-step_id={step.id} name="step_edit_name" defaultValue={step.name} maxLength={200} required={true}
                    id={getStrId('step_edit_name', step.id)} onChange={editStep}
                    className={extraClass('form-control form-control-sm small-input', step.completed, 'completed')} />
                <button data-step_id={step.id} name="step_delete" className="bi-x del-item-icon" onClick={delStepConfirm} />
            </div>
        );
    });
    return (
        <div className="input-group flex-wrap mb-3">
            {stepList}
            <div>
                <input type="text" name="step_edit_name" maxLength={200} required={false} placeholder="Next step"
                        id="add_step" onChange={addStep}  className="form-control form-control-sm small-input" />
            </div>
        </div>
    );
}

function MyDay({item}: {item: IItemInfo}) {
    return <></>;
}

function Termin({item}: {item: IItemInfo}) {
    return <></>;
}

function ItemInfo({item}: {item: IItemInfo}) {
    return <div className="col-sm-7">{item.info}</div>
}

function Group({item}: {item: IItemInfo}) {
    return <div className="col-sm">{item.groups}</div>
}

function Categories({item}: {item: IItemInfo}) {
    return <div className="col-sm">{item.categories}</div>
}


function UrlList({item}: {item: IItemInfo}) {
    return <div className="col">{item.url}</div>
}

function Attachments({item}: {item: IItemInfo}) {
    return <div className="col">{item.upload}</div>
}

function delItemConfirm() {

}

function update() {
}

export async function loader({ params }: LoaderFunctionArgs) {
    const item: IItemInfo = await api.get(`todo/${params.id}`, {});
    return item;
}
  
function TodoItemPage() {
    const config = useOutletContext() as IPageConfig;
    const item = useLoaderData() as IItemInfo;
    const csrfToken = '';
    if (!item)
        return <></>;
    return (
        <form method="post" className="item-form px-2" encType="multipart/form-data" id="article_form" data-item_id="{item.id}">
            {csrfToken}
            <ItemTitle item={item} config={config} />
            <FormErrors />

            <div className="input-group">
                <Completed item={item} />
                <ItemName item={item} />
                <Important item={item} />
            </div>
            <TodoSteps item={item} />
            <div className="termin-row">
                <MyDay item={item} />
                <Termin item={item} />
            </div>
            <div className="row g-3">
                <ItemInfo item={item} />
                <Group item={item} />
                <Categories item={item} />
            </div>
            <div className="row">
                <UrlList item={item} />
                <Attachments item={item} />
            </div>

            <div className="d-flex justify-content-evenly mt-3 pb-5">
                <button type="submit" name="item_save" className="btn btn-primary bi-save" title="Save changes">
                    <span className="px-2">Save</span>
                </button>
                <button type="submit" name="form_close" className="btn btn-secondary bi-x" title="Close edit form">
                    <span className="px-2">Close</span>
                </button>
                <button type="button" name="item_delete" className="btn btn-danger bi-trash" onClick={delItemConfirm} title="Delete record">
                    <span className="px-2">Delete</span>
                </button>
            </div>

            <div className="row">
                <div className="col">Created: {item.created}</div>
                {item.completed &&
                    <div className="col">Completed: {item.completion}</div>
                }
            </div>
        </form>
    );
}
  
export default TodoItemPage;