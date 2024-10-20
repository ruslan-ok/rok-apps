import { IPageConfig } from '../PageConfig';
import { ItemInfo } from './ItemTypes';


function Item({item, config}: {item: ItemInfo, config: IPageConfig}) {
    console.log(item);
    console.log(config);
    return (
        <li className="">
        </li>
    );
}

export default Item;