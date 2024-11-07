import { Container, Row } from 'react-bootstrap';
import Weight from './widgets/Weight';
import Currency from './widgets/Currency';
import Crypto from './widgets/Crypto';


function MainPageProtected() {
    return (
        <Container fluid>
            <Row>
                <Weight />
                <Currency />
                <Crypto />
            </Row>
        </Container>
    );
}

export default MainPageProtected;
