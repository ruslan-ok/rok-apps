import './Spinner.css';

function Spinner({width, height}: {width: number, height: number}) {
    const compStyle = {width: width, height: height};
    return (
        <div className='spinner-place rok-spinner' style={compStyle} >
            <div className='spinner'>
                <div className="loader"></div>
            </div>
        </div>
    );
}

export default Spinner;