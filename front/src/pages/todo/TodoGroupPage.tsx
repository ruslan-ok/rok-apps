import { useOutletContext } from "react-router-dom";
import Form from 'react-bootstrap/Form';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import { IPageConfig } from '../PageConfig';
import PageTitle from './PageTitle';


function TodoGroupPage() {
    const config = useOutletContext() as IPageConfig;
    return (
        <div className="item-form p-2 w-100" id="article_form" data-item_id={config.view_group.id}>
            <PageTitle config={config} setTheme={()=>{}} />
            <Form method="post" encType="multipart/form-data" className="px-2">
                <Form.Group as={Row} className="mb-3" controlId="groupName">
                    <Form.Label column sm="2">Group name</Form.Label>
                    <Col sm="10">
                        <Form.Control type="text" placeholder="Group name" defaultValue={config.view_group.name} />
                    </Col>
                </Form.Group>
                <Form.Group as={Row} className="mb-3" controlId="sortCode">
                    <Form.Label column sm="2">Sort code</Form.Label>
                    <Col sm="10">
                        <Form.Control type="text" placeholder="Sort code" />
                    </Col>
                </Form.Group>
                <Form.Group as={Row} className="mb-3" controlId="groupNode">
                    <Form.Label column sm="2">Node</Form.Label>
                    <Col sm="10">
                        <Form.Control type="text" placeholder="Group node" />
                    </Col>
                </Form.Group>
            </Form>
        </div>
    );
}

export default TodoGroupPage;