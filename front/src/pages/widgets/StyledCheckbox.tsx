function StyledCheckbox({id, text, classes, r, g, b, checked, onClick }: {id: string, text: string, classes: string, r: number, g: number, b: number, checked: boolean, onClick: () => void }) {
    const icon = checked ? 'bi-check-square-fill' : 'bi-square';
    const labelStyle = {
        color: 'var(--basicssecondary)',
        fontFamily: 'var(--body-regular-font-family)',
        fontSize: 'var(--body-regular-font-size)',
        fontStyle: 'var(--body-regular-font-style)',
        fontWeight: 'var(--body-regular-font-weight)',
        letterSpacing: 'var(--body-regular-letter-spacing)',
        lineHeight: 'var(--body-regular-line-height)',
        marginLeft: '6px',

    };
    const inputStyle = {
        visibility: 'hidden',
        display: 'block',
        height: 0,
        width: 0,
        position: 'absolute',
        overflow: 'hidden',
    };

    return (
        <div className={classes} style={{color: `rgba(${r}, ${g}, ${b}, 1)`}}>
            <label className="d-flex" >
                <input type='checkbox' id={id} name={id} checked={checked} onChange={onClick} style={inputStyle} />
                <span><i className={icon}></i></span>
                <span style={labelStyle} >{text}</span>
            </label>
        </div>
    );
}

export default StyledCheckbox;