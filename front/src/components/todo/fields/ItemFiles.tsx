import { getStrId } from '../TodoItemPage';
import { IFile } from '../ItemTypes';

function uploadFile() {
    console.log('uploadFile');
}

function fileSelected() {
    console.log('fileSelected');
}

function delFileConfirm() {
    console.log('delFileConfirm');
}

function ItemFiles({files}: {files: IFile[]}) {
    const filesList = files.map(file => {
        const design = 'brown';
        return (
            <div className="file-item" id={getStrId('id_file', file.id)}>
                <a href={file.href}>
                    <div className="thumbnail-wrapper" style={{backgroundColor: design}} >
                        <div className="thumbnail">{file.ext}</div>
                    </div>
                    <div className="file-content">
                        <div className="file-title">{file.name}</div>
                        <div className="file-metadata">{file.size}</div>
                    </div>
                </a>
                <button type="button" name="file_delete" value={file.href} className="bi-x" onClick={delFileConfirm} />
            </div>
        );
    });

    return (
        <div className="col">
            <label htmlFor="id_upload">Attachments:</label>
            <div className="files-area">
                <div className="file-list" id="file-list-dst">
                    {filesList}
                </div>
                <div className="file-add">
                    <button name="file_upload" className="section-inner-click" onClick={uploadFile}>
                        <div className="bi-paperclip" />
                        <div className="section-content">
                            <div id="loadFile">Add file</div>
                            <input type="file" id="id_upload" style={{display: 'none'}} onChange={fileSelected} />
                        </div>
                    </button>
                    <button type="button" id="id_submit" name="file_upload" className="file-upload" />
                </div>
            </div>
        </div>
    );
}

export default ItemFiles;