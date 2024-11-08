import { IPageConfig } from '../PageConfig';
import { IItemInfo } from './ItemTypes';


function Item({item, config}: {item: IItemInfo, config: IPageConfig}) {
    console.log(item);
    console.log(config);
    return (
        <li className="">
        </li>
    );
}

export default Item;