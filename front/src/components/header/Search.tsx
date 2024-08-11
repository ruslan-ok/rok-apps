import { Form, useSearchParams } from 'react-router-dom';
import './Search.css';

function Search({placeholder, hide, searchText}: {placeholder: string, hide: boolean, searchText: string}) {
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
        <Form id="search-form" role="search">
            {hidden_view}
            {hidden_group}
            {hidden_folder}
            <input id="q" aria-label="Search items" placeholder={placeholder} type="search" name="q" defaultValue={searchText} />
            <div id="search-spinner" aria-hidden hidden={true} />
            <div className="sr-only" aria-live="polite"/>
        </Form>
    );
}

export default Search;