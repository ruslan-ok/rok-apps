import { ILink } from '../ItemTypes';

function delURL() {
    console.log('delURL');
}

function ItemLinks({links}: {links: ILink[]}) {
    const urlList = links.map(url => {
        return (
            <div className="url-link" id="id_url_{{url.id|escape}}">
                <div className="label">
                    <a href="{{ url.href|escape }}" className="value">{url.name}</a>
                </div>
                <div className="icon" onClick={delURL} >
                    <div className="delete">
                        <svg height="8" width="8" style={{fill: 'currentcolor'}}>
                            <path d="M4.46607 4L8 7.53905L7.53905 8L4 4.46607L0.460948 8L0 7.53905L3.53393 4L0 0.460948L0.460948 0L4 3.53393L7.53905 0L8 0.460948L4.46607 4Z"></path>
                        </svg>
                    </div>
                </div>
            </div>
        );
    });

    return (
        <div className="col">
            <label htmlFor="id_url">URLs:</label>
            <div className="url-list" id="url-list-dst">
                {urlList}
            </div>
            <input type="text" id="id_url" className="form-control mb-3" placeholder="Add link" />
        </div>
    );
}

export default ItemLinks;