import { LinkContainer } from 'react-router-bootstrap';
import { useLoaderData } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';
import Form from 'react-bootstrap/Form';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
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
    const data = await api.get('header', {version: 5});
    return data;
}

function Header() {
    const data = useLoaderData() as IHeaderData;
    // const apps = data.applications.filter(app => app.name !== 'Home').map(app => {
    const desktopApps = data.applications.map(app => {
        const appIcon = 'me-2 bi-' + app.icon;
        const appName = app.active ? app.name : '';
        return (
            <LinkContainer key={app.name} to={app.href}>
                <Nav.Link className="d-flex align-items-center" >
                    <i className={appIcon} />
                    {appName}
                </Nav.Link>
            </LinkContainer>
        );
    });
    const mobileApps = data.applications.map(app => {
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
                <Button className='m-2'>{button.name}</Button>
            </LinkContainer>
        );
    });

    function handleToggle() {
        console.log('handleToggle');
    }

    return <Navbar expand="lg" className="bg-body-tertiary" onToggle={handleToggle}>
        <Container>
            <LinkContainer to="/v5">
                <Navbar.Brand className="d-flex align-items-center">
                    <img
                        alt="Rok Apps"
                        src="/static/rok.png"
                        width="38"
                        height="38"
                        className="d-inline-block align-top me-2"
                    />{' '}
                    Rok Apps
                </Navbar.Brand>
            </LinkContainer>
            
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="me-auto">
                    <Container className="d-lg-none">
                        <Row>
                            {mobileApps}
                        </Row>
                    </Container>
                    <Container className="d-none d-lg-flex">
                        {desktopApps}
                    </Container>
                    {showSearch &&
                        <Form inline="true">
                            <Row>
                                <Col xs="auto">
                                    <Form.Control
                                        type="text"
                                        placeholder="Search"
                                        className=" mr-sm-2"
                                    />
                                </Col>
                                {/* <Col xs="auto">
                                    <Button type="submit">Submit</Button>
                                </Col> */}
                            </Row>
                        </Form>
                    }
                </Nav>
                <Nav>
                    {data?.avatar &&
                        <img
                            alt="Avatar"
                            src={data?.avatar}
                            width="32"
                            height="32"
                            className="d-inline-block align-top me-2"
                        />
                    }
                    {data.userName &&
                        <NavDropdown title={data.userName} id="basic-nav-dropdown">
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