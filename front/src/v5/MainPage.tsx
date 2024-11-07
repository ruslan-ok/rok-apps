import { api } from '../API'
import MainPagePublic from './MainPagePublic';
import MainPageProtected from './MainPageProtected';

function MainPage() {
    let layout;
    if (api.isAuthenticated) {
        layout = <MainPageProtected />;
    } else {
        layout = <MainPagePublic />;
    }

    return (<>
        {layout}
    </>);
}
  
export default MainPage;