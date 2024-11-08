import './Hamburger.css';

function Hamburger({onClick, hide}: {onClick: () => void, hide: boolean}) {

    if (hide)
        return <></>;

    return (
        <section className='navbar-toggler' onClick={onClick}>
            <button className='navbar-toggler' type='button' data-bs-toggle='collapse' data-bs-target='#bdNavbar' aria-controls='bdNavbar' aria-expanded='false' aria-label='Toggle navigation'>
                <svg xmlns='http://www.w3.org/2000/svg' width="32" height="32" className='bi' fill='currentColor' viewBox='0 0 16 16'>
                    <path fillRule='evenodd' d='M2.5 11.5A.5.5 0 0 1 3 11h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4A.5.5 0 0 1 3 7h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5zm0-4A.5.5 0 0 1 3 3h10a.5.5 0 0 1 0 1H3a.5.5 0 0 1-.5-.5z'></path>
                </svg>
            </button>
        </section>
    );
}

export default Hamburger;