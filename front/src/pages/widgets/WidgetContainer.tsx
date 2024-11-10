import { ReactNode } from 'react';
import { Spinner } from 'react-bootstrap';


function WidgetContainer({ status, message, children }: { status: string, message: string, children: ReactNode }) {
    if (status === 'ready') {
        return (<>
            {children}
        </>);
    } else if (status === 'message') {
        return (
            <span className="d-flex justify-content-center align-items-center" style={{minHeight: '200px', }} >
                {message}
            </span>
        );
    } else {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{minHeight: '200px', }} >
                <Spinner animation="border" role="status" variant="secondary">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
            </div>
        );
    }
};

export default WidgetContainer;