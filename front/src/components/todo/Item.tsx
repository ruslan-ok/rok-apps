import type { PageConfigInfo } from './TodoPage';
import { ItemInfo } from './ItemTypes';


function Item({item, config}: {item: ItemInfo, config: PageConfigInfo}) {
    console.log(item);
    console.log(config);
    return (
        <li className="">
        </li>
    );
}

export default Item;