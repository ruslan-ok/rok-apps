import { useState, useEffect } from 'react';
import { Container } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { Link } from 'react-router-dom';
import { api } from '../../API'
import WidgetContainer from './WidgetContainer';


export default function LastVisited() {
    const [status, setStatus] = useState('init');
    const [values, setValues] = useState<any>(null);
    const [message, setMessage] = useState('');
    const [redraw, setRedraw] = useState('1');

    useEffect(() => {

        async function getData() {
            setStatus('loading');
            let resp_data = await api.get('chart', {mark: 'visited', version: 5});
            if (resp_data) {
                if (resp_data.result === 'ok') {
                    setValues(resp_data);
                    setStatus('ready');
                }
                else {
                    if (!resp_data?.info) {
                        setMessage('Bad Last Visited Widget responce');
                        setStatus('message');
                    } else {
                        let prefix = '';
                        if (resp_data.procedure) {
                            prefix = resp_data.procedure + ': ';
                        }
                        setMessage(prefix + resp_data.info);
                        setStatus('message');
                    }
                }
            }
        }

        getData();
    }, []); // [redraw]);

    async function toggle(id: number) {
        let resp_data = await api.get(`visited/${id}/toggle_pin`, {});
        if (resp_data) {
            setRedraw(redraw === '0' ? '1' : '0');
        }
    }

    function togglePin(event: any) {
        const id = event.currentTarget.dataset.id;
        toggle(id);
    }

    if (status === 'ready') {
        var links = values.data.map((page: any) => {
            const href = page.url.split('?')[0];
            const search = page.url.split('?')[1] || '';
            const value = page.title || '';
            const pinStyle = page.pinned ? {color: 'orange'} : {};
            return (
                <tr key={page.id} >
                    <td><i className={ page.icon } title={ page.stamp }></i></td>
                    <td>
                        <LinkContainer to={href} search={search}>
                            <Link to={href} className="text-decoration-none">{value}</Link>
                        </LinkContainer>
                    </td>
                    <td>
                        <button type="button" className="border-0 bg-white" data-id={page.id} onClick={togglePin}>
                            <i className={ page.pinned ? 'bi-pin-fill' : 'bi-pin-angle' } style={pinStyle} />
                        </button>
                    </td>
                </tr>
            );
        });
    }

    const style = {
        height: '39px',
        paddingTop: '8px',
        paddingLeft: '16px',
        margin: '0',
    }
    return (
        <Container style={{maxWidth: '600px', minHeight: '200px', }} className="bg-white p-0 mb-3 align-self-start" >
            <h6 className="bg-info-subtle" style={style} >Last visited</h6>
            <WidgetContainer status={status} message={message} >
                {status === 'ready' &&
                    <table className="table table-sm">
                        <tbody>
                            {links}
                        </tbody>
                    </table>
                }
            </WidgetContainer>
        </Container>
    );
}