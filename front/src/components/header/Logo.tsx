import './Logo.css';

function Logo({icon, title}: {icon: string, title: undefined | string}) {
    let appTitle;
    if (title) {
      appTitle = <span className='brand'>{title}</span>;
    }
  
    let logo = 
      <div className='logo'>
        <img src={icon} />
        {appTitle}
      </div>;
  
    return logo;
}

export default Logo;