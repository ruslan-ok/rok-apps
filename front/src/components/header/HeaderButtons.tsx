import { Link } from 'react-router-dom';
import type { HeaderButton } from './Header';
import './HeaderButtons.css';

function HeaderButtons({items}: {items: HeaderButton[]}) {
  let buttons;
  if (items.length) {
    const buttonList = items.map((item) => {
      let href = '/react/' + item.href;
      return (<Link className='button' to={href} key={item.button_id}>{item.name}</Link>);
    });
    buttons = <section className='buttons'>{buttonList}</section>;
  }

  return buttons;
}

export default HeaderButtons;