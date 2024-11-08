import { ReactNode } from 'react';
import { Container, Spinner } from 'react-bootstrap';


function WidgetContainer({ name, status, message, children }: { name: string, status: string, message: string, children: ReactNode }) {
    if (status === 'ready') {
        return (
            <Container style={{maxWidth: '600px'}} className="bg-white p-0 mb-3" data-widget-name={name} >
                {children}
            </Container>
        );
    } else if (status === 'mess') {
        return (
            <Container className="d-flex justify-content-center align-items-center bg-white p-0 mb-3" style={{maxWidth: '600px', minHeight: '200px'}} data-widget-name={name} >
                <span className="warning">{message}</span>
            </Container>
        );
    } else {
        return (
            <Container className="d-flex justify-content-center align-items-center bg-white p-0 mb-3" style={{maxWidth: '600px', minHeight: '200px'}} data-widget-name={name} data-widget-status={status} >
                <div className="d-flex flex-column">
                    <Spinner animation="border" role="status" variant="secondary">
                        <span className="visually-hidden">Loading...</span>
                    </Spinner>
                </div>
            </Container>
        );
    }
};

export default WidgetContainer;