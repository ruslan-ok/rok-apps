import type { IUserMenuElement } from './Header';

function UserMenu({avatar, username, items}: {avatar: undefined | string, username: undefined | string, items: IUserMenuElement[]}) {
    let users = <section className='user-menu s-f-container dropdown mx-4'></section>;

    if (items.length) {
      let userMenu = items.map((item) => {
        if (item.item_id === 'separator') {
          return <li key={item.name}><hr className='dropdown-divider' /></li>;
        } else {
          return (
            <li key={item.name}>
              <a className='dropdown-item d-flex justify-content-between' href={item.href}>
                <span>{item.name}</span>
                <i className={item.icon}></i>
              </a>
            </li>
          );
        }
      });
  
      users =
        <section className='user-menu s-f-container dropdown mx-4'>
          <a href='/' className='d-flex align-items-center justify-content-center link-light text-decoration-none dropdown-toggle' id='dropdownUser2' data-bs-toggle='dropdown' aria-expanded='false'>
            <img src={avatar} alt='' width='32' height='32' className='rounded-circle me-2' />
            <span className='d-md-none d-lg-block'>{username}</span>
          </a>
          <ul className='dropdown-menu text-small shadow' aria-labelledby='dropdownUser2'>
            {userMenu}
          </ul>
        </section>;
    }
  
    return users;
}

export default UserMenu;
