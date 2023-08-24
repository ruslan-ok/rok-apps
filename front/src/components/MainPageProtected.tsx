import Crypto from './widgets/Crypto';
import Weight from './widgets/Weight';
import Currency from './widgets/Currency';

import './MainPageProtected.css';

interface WidgetInfo {
  id: string;
  name: string;
}

export interface ProtectedData {
  widgets: WidgetInfo[];
}

function MainPageProtected() {
    return (
      <>
        <div className='hp_widgets'>
          <div className='static-widgets'>
            <Currency width={500} height={300} />
            <Crypto />
            <Weight />
          </div>
        </div>
      </>
    );
}

export default MainPageProtected;