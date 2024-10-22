import { api } from '../API'
import MainPagePublic from './MainPagePublic';
import MainPageProtected from './MainPageProtected';
import '../components/main.css';
import '../components/css/error_page.min.css';
import 'bootstrap/dist/css/bootstrap.css';
import './css/custom.css';
import './css/common.css';
import "./css/title.min.css";
import './css/tune.min.css';
import './css/list.min.css';
import './css/form.min.css';

function MainPage() {
  let layout;
  if (api.isAuthenticated) {
    layout = <MainPageProtected />;
  } else {
    layout = <MainPagePublic />;
  }

  return (
    <>
      {layout}
    </>
  );
}
  
export default MainPage;