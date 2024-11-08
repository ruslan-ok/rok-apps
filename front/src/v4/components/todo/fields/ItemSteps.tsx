import { IStep } from '../ItemTypes';
import { getStrId, extraClass } from '../TodoItemPage';


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

function ItemSteps({steps}: {steps: IStep[]}) {
    const stepList = steps.map(step => {
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
                <input type="text" maxLength={200} required={false} placeholder="Next step"
                        id="add_step" onChange={addStep}  className="form-control form-control-sm small-input" />
            </div>
        </div>
    );
}

export default ItemSteps;