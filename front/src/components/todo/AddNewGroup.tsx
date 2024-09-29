function AddNewGroup({app, role, entity, hint}: {app: string, role: string, entity: string, hint: string}) {
    function addGroup() {
        console.log(app, role, entity)
    }

    return (
        <>
            <div className="add-form position-sticky bottom-0 px-3 py-3 d-flex flex-column">
                <p className="d-none errornote" id="id_add_group_error">Error Description</p>
                <div className="add-form position-sticky bottom-0 px-3 py-3 d-flex flex-nowrap">
                    <button type="button" className="btn btn-primary bi-plus-lg add-form__button" id="add_group_btn_id" onClick={addGroup} />
                    <input type="text" className="add-form__input" placeholder={hint} name="name" id="new_group_id" />
                </div>
            </div>
        </>
    );
}
    
export default AddNewGroup;