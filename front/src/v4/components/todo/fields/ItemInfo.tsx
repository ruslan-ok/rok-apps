function ItemInfo({info}: {info: string}) {
    return (
        <div className="col-sm-7">
            <label htmlFor="id_info">Information:</label>
            <textarea name="info" cols={40} rows={10} className="form-control mb-3" id="id_info" defaultValue={info} />
        </div>
    );
}

export default ItemInfo;