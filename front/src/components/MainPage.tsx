import { auth } from './auth/Auth';
import MainPagePublic from './MainPagePublic';
import MainPageProtected from './MainPageProtected';
import 'bootstrap/dist/css/bootstrap.css';
import './css/custom.css';
import "./css/title.min.css";
import './css/tune.min.css';
import './css/list.min.css';

function MainPage() {
  let layout;
  if (auth.isAuthenticated) {
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