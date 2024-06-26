import { Form, useSearchParams } from 'react-router-dom';
import './Search.css';

function Search({placeholder, hide}: {placeholder: string, hide: boolean}) {
    let [searchParams] = useSearchParams();
    let view = searchParams.get('view');
    let group = searchParams.get('group');
    let folder = searchParams.get('folder');

    if (hide)
        return <></>;
        
    let hidden_view = view ? <input type="hidden" name="view" value={view} readOnly={true}/> : <></>;
    let hidden_group = group ? <input type="hidden" name="group" value={group} readOnly={true} /> : <></>;
    let hidden_folder = folder ? <input type="hidden" name="folder" value={folder} readOnly={true} /> : <></>;

    return (
        <Form action='' method='GET' className='search'>
            {hidden_view}
            {hidden_group}
            {hidden_folder}
            <input type='search' className='' id='search-input' placeholder={placeholder} name="q" />
        </Form>
    );
}

export default Search;