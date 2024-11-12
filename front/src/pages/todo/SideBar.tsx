import { Container, Navbar } from 'react-bootstrap';
import { IPageConfig } from '../PageConfig';
import FixList from './FixList';
import GroupTree from './GroupTree';
import AddNewGroup from './AddNewGroup';


function SideBar({width, config}: {width: number, config: IPageConfig}) {
    const isMobile = width < 768;
    let style;
    if (isMobile) {
        style = {
            height: '50px',
        };
    } else {
        style = {
            width: '400px',
        };
    }

    return (<>
        {!isMobile &&
            <Container style={style} className="mt-3" >
                <FixList config={config} />
                <GroupTree config={config} />
                <AddNewGroup config={config} />
            </Container>
        }
        {isMobile && 
            <Navbar className="bg-body-tertiary" expand="lg">
                <Container className="bg-warning-subtle m-1" >
                    <Navbar.Toggle className="bg-primary-subtle m-2" />
                    <Navbar.Collapse className="justify-content-end">
                        <FixList config={config} />
                        <GroupTree config={config} />
                        <AddNewGroup config={config} />
                    </Navbar.Collapse>
                </Container>
            </Navbar>
        }
    </>);
}

export default SideBar;