import { useState, SyntheticEvent } from 'react';
import Form from 'react-bootstrap/Form';


function Completed({completed, onChange}: {completed: boolean, onChange: Function}) {
    const [checked, setChecked] = useState(completed);

    function completedChanged() {
        const newValue = !checked;
        setChecked(newValue);
        onChange({completed: newValue});
    }

    return (
        <div className="form-check completed-checkbox">
            <input type="checkbox" name="completed" id="id_completed"
                className="form-check-input" onChange={completedChanged}
                checked={checked} />
        </div>
    );
}

function Important({important, onChange}: {important: boolean, onChange: Function}) {
    const [checked, setChecked] = useState(important);

    function importantChanged() {
        const newValue = !checked;
        setChecked(newValue);
        onChange({important: newValue});
    }

    const iconClass = 'bi-star' + (checked ? '-fill' : '');
    return (
        <button type="button" onClick={importantChanged} id="toggle-important" className="btn-important" >
            <i className={iconClass} />
        </button>
    );
}

function ItemName({completed, name, important, onChange}: {completed: boolean, name: string, important: boolean, onChange: Function}) {

    function onChangeName(event: SyntheticEvent) {
        const newName = event.target.value;
        onChange({name: newName});
    }

    return (
        <Form.Group className="d-flex mb-3" controlId="todo-name-group">
            <Completed completed={completed} onChange={onChange} />
            <Form.Control type="text" placeholder="Name" name="name" defaultValue={name} onChange={onChangeName} />
            <Important important={important} onChange={onChange} />
        </Form.Group>
    );
}

export default ItemName;