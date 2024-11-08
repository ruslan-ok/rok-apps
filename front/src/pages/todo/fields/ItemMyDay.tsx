import { useState } from 'react';
import ToggleButton from 'react-bootstrap/ToggleButton';
import { extraClass } from '../TodoItemPage'


function ItemMyDay({myDay, onChange}: {myDay: boolean, onChange: Function}) {
    const [checked, setChecked] = useState(myDay);
    const label = checked ? 'Added in "My day"' : 'Add to "My day"';

    function toggleMyDay() {
        setChecked(!checked);
        onChange({in_my_day: !checked});
    }
        
    return (
        <ToggleButton id="in_my_day" type="checkbox" checked={checked} className="in_my_day me-3 mb-2" variant="light" value="1" onClick={toggleMyDay}>
            <i className={extraClass('bi-sun', checked, 'checked')} />
            <div className={extraClass('my_day-title', checked, 'checked')} >
                {label}
            </div>
        </ToggleButton>
    );
}

export default ItemMyDay;