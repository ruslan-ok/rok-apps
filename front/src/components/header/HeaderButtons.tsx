import type { HeaderButton } from './Header';
import './HeaderButtons.css';

function HeaderButtons({items}: {items: HeaderButton[]}) {
  let buttons;
  let buttonList;

  if (items.length) {
    buttonList = items.map((item) => {
      return (<a className='button' href={item.href} key={item.button_id}>{item.name}</a>);
    });
  }

  buttons = <section className='buttons'>{buttonList}</section>;

  return buttons;
}

export default HeaderButtons;