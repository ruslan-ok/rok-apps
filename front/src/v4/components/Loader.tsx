import './Loader.css';

function Loader({loading}: {loading: boolean}) {
    return (
        <div className={loading ? "loader" : ""}></div>
    );
}

export default Loader;