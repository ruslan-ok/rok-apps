import { LinkContainer } from 'react-router-bootstrap';
import { NavLink, useLoaderData } from 'react-router-dom';
import { Container, Nav, Navbar, NavDropdown, Form, Button, Row, Col } from 'react-bootstrap';
import { api } from '../API'


interface IApplication {
    name: string;
    icon: string;
    href: string;
    active: boolean;
};

interface IUserMenuElement {
    item_id: string;
    name: string;
    href: string;
    icon: string;
};

interface IHeaderButton {
    button_id: string;
    name: string;
    href: string;
};
  
export interface IHeaderData {
    appIcon: string;
    appTitle: undefined | string;
    applications: IApplication[];
    searchPlaceholder: string;
    searchText: string;
    userName: undefined | string;
    avatar: undefined | string;
    userMenu: IUserMenuElement[];
    buttons: IHeaderButton[];
};
  
export async function loader(): Promise<IHeaderData> {
    await api.init();
    const data = await api.get('header', {});
    return data;
}

function AppLink({href, icon, name}: {href: string, icon: string, name: string}) {
    return (<>
        <NavLink to={href} className={({ isActive }) => isActive ? "rok-nav-link active" : "d-none"} >
            <i className={icon} title={name} /> <span className="me-2">{name}</span>
        </NavLink>
        <NavLink to={href} className={({ isActive }) => isActive ? "d-none" : "rok-nav-link"} >
            <i className={icon} title={name} />
        </NavLink>
    </>);
}

function Header() {
    const data = useLoaderData() as IHeaderData;
    const desktopApps = data.applications.filter(app => app.name !== 'Home').map(app => {
        const appIcon = 'p-2 bi-' + app.icon;
        return <AppLink key={app.name} href={app.href} icon={appIcon} name={app.name} />;
    });
    const mobileApps = data.applications.filter(app => app.name !== 'Home').map(app => {
        const appIcon = 'me-2 bi-' + app.icon;
        return (
            <LinkContainer key={app.name} to={app.href}>
                <Nav.Link className="d-flex align-items-center col-6" >
                    <i className={appIcon} />
                    {app.name}
                </Nav.Link>
            </LinkContainer>
        );
    });
    const showSearch = data.userMenu.length > 0;
    const userMenu = data.userMenu.map(item => {
        return (
            <LinkContainer key={item.item_id} to={item.href} >
                <NavDropdown.Item>
                    {item.name}
                </NavDropdown.Item>
            </LinkContainer>
        );
    });
    const buttons = data?.buttons.map(button => {
        return (
            <LinkContainer key={button.button_id} to={button.href}>
                <Button className='rok-button'>{button.name}</Button>
            </LinkContainer>
        );
    });

    function handleToggle() {
        console.log('handleToggle');
    }

    return <Navbar expand="lg" onToggle={handleToggle} className="rok-navbar navbar-dark">
        <Container >
            <LinkContainer to="/">
                <Navbar.Brand className="d-flex align-items-center brand">
                    <img
                        alt="Rok Apps"
                        src="/static/rok.png"
                        width="38"
                        height="38"
                        className="d-inline-block align-top me-2"
                    />
                    Rok Apps
                </Navbar.Brand>
            </LinkContainer>
            
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="me-auto">
                    <Container className="d-lg-none align-items-center">
                        <Row>
                            {mobileApps}
                        </Row>
                    </Container>
                    <Container className="d-none d-lg-flex align-items-center me-5">
                        {desktopApps}
                    </Container>
                    {showSearch &&
                        <Form>
                            <Row>
                                <Col style={{minWidth: '400px'}} >
                                    <Form.Control
                                        type="text"
                                        placeholder="Search"
                                        className=" mr-sm-2 form-control"
                                    />
                                </Col>
                                {/* <Col xs="auto">
                                    <Button type="submit">Submit</Button>
                                </Col> */}
                            </Row>
                        </Form>
                    }
                </Nav>
                <Nav className="d-flex flex-row">
                    {data?.avatar &&
                        <img
                            alt="Avatar"
                            src={data?.avatar}
                            width="32"
                            height="32"
                            className="d-inline-block align-top rounded-circle me-2 mt-1"
                        />
                    }
                    {data.userName &&
                        <NavDropdown title={data.userName} id="basic-nav-dropdown" className="">
                            {userMenu}
                        </NavDropdown>
                    }
                    {buttons}
                </Nav>
            </Navbar.Collapse>
        </Container>
    </Navbar>;
}

export default Header;