import { useState } from 'react';
import { useRouteLoaderData } from 'react-router-dom';

import Logo from './Logo';
import Search from './Search';
import Hamburger from './Hamburger';
import AppList from './AppList';
import UserMenu from './UserMenu';
import HeaderButtons from './HeaderButtons';

export interface Application {
  name: string;
  icon: string;
  href: string;
  active: boolean;
};

export interface UserMenuElement {
  item_id: string;
  name: string;
  href: string;
  icon: string;
};

export interface HeaderButton {
  button_id: string;
  name: string;
  href: string;
};

export interface HeaderData {
  appIcon: string;
  appTitle: undefined | string;
  applications: Application[];
  searchPlaceholder: string;
  searchText: string;
  userName: undefined | string;
  avatar: undefined | string;
  userMenu: UserMenuElement[];
  buttons: HeaderButton[];
};

function Header({windowWidth}: {windowWidth: number}) {
  const [expanded, setExpanded] = useState(0);

  function handleClick() {
    setExpanded(expanded ? 0 : 1);
  }

  const headerData = useRouteLoaderData('header') as HeaderData;

  if (windowWidth < 768) {
    let section_top = 
      <section className='header-top'>
        <Logo icon={headerData.appIcon} title={headerData.appTitle} />
        <Search placeholder={headerData.searchPlaceholder} hide={!headerData.userName} />
        <Hamburger onClick={handleClick} hide={!headerData.userName} />
        <HeaderButtons items={headerData.buttons} />
      </section>;

    let section_bottom;
    if (expanded) {
      section_bottom =
        <section>
          <hr />
          <AppList mobile={true} items={headerData.applications} />
          <hr />
          <UserMenu avatar={headerData.avatar} username={headerData.userName} items={headerData.userMenu} />
        </section>;
    }

    return (
      <header>
        <nav className='mobile'>
          {section_top}
          {section_bottom}
        </nav>
      </header>
    );
  } else {
    return (
      <header>
        <nav className='desktop'>
          <section className='logo-apps'>
            <Logo icon={headerData.appIcon} title={headerData.appTitle} />
            <AppList mobile={false} items={headerData.applications} />
          </section>
          <Search placeholder={headerData.searchPlaceholder} hide={!headerData.userName} />
          <UserMenu avatar={headerData.avatar} username={headerData.userName} items={headerData.userMenu} />
          <HeaderButtons items={headerData.buttons} />
        </nav>
      </header>
    );
  }
}

export default Header;
