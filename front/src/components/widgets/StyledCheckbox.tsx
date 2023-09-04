function StyledCheckbox({id, text, classes, r, g, b, checked, onClick }: {id: string, text: string, classes: string, r: number, g: number, b: number, checked: boolean, onClick: () => void }) {
    const icon = checked ? 'bi-check-square-fill' : 'bi-square';
    return (
        <div className={classes} style={{color: `rgba(${r}, ${g}, ${b}, 1)`}}>
            <label className="styled-checkbox-label" >
                <input type='checkbox' id={id} name={id} className="styled-checkbox" checked={checked} onChange={onClick} />
                <span className="styled-checkbox"><i className={icon}></i></span>
                <span className="styled-checkbox-label">{text}</span>
            </label>
        </div>
    );
}

export default StyledCheckbox;