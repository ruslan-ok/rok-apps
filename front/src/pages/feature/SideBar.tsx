import { IPageConfig } from '../PageConfig';


function SideBar({width, config}: {width: number, config: IPageConfig}) {
    const isMobile = width < 768;
    let style;
    if (isMobile) {
        style = {
            height: '50px',
        };
    } else {
        style = {
            width: '500px',
        };
    }

    const useGroups = config.view_group.app === 'todo';

    return (<>
        {isMobile &&
            <div className="d-flex align-items-center bg-success-subtle" style={style}>
                {useGroups}
            </div>
        }
    </>);
}

export default SideBar;