import { Container, Row } from 'react-bootstrap';
// import TodoList from './widgets/todo/TodoList';
import LastVisited from './widgets/LastVisited';
import Weather from './widgets//weather/Weather';
import Weight from './widgets/Weight';
import Currency from './widgets/Currency';
import Crypto from './widgets/Crypto';


function MainPageProtected() {
    return (
        <Container fluid className="bg-body-tertiary">
            <Row>
                {/* <TodoList /> */}
                <LastVisited />
                <Weather />
                <Weight />
                <Currency />
                <Crypto />
            </Row>
        </Container>
    );
}

export default MainPageProtected;
