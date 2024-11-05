import ButtonGroup from 'react-bootstrap/ButtonGroup';
import { IItemInfo } from './ItemTypes';
import ItemMyDay from './fields/ItemMyDay';
import ItemTermin from './fields/ItemTermin';
import ItemRepeat from './fields/ItemRepeat';
import ItemRemind from './fields/ItemRemind';

function ItemDates({item, onChange}: {item: IItemInfo, onChange: Function}) {
    return (
        <ButtonGroup className="todo-dates mb-3 d-flex flex-wrap align-items-start">
            <ItemMyDay myDay={item.in_my_day} onChange={onChange} />
            <ItemTermin termin={item.stop} onChange={onChange} />
            <ItemRepeat id={item.id} repeat={item.repeat || 0} days={item.repeat_days || 0} num={item.repeat_num || 0} start={item.start || ''} stop={item.stop} />
            <ItemRemind id={item.id} remind={item.remind || ''} />
        </ButtonGroup>
    );
}

export default ItemDates;
