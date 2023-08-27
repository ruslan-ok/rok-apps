import { useState, useEffect } from 'react';

import Weather from './widgets/weather/Weather';
import Crypto from './widgets/Crypto';
import Weight from './widgets/Weight';
import Currency from './widgets/Currency';
// import Todo from './widgets/Todo';

import './widgets/widget.css';

interface WidgetInfo {
  id: string;
  name: string;
}

export interface ProtectedData {
  widgets: WidgetInfo[];
}

function MainPageProtected() {
  const [width, setWindowWidth] = useState(0);

  useEffect( () => {
      updateDimensions();
      window.addEventListener("resize", updateDimensions);
      return () => window.removeEventListener("resize", updateDimensions);
  }, []);

  const updateDimensions = () => {
      const width = window.innerWidth;
      setWindowWidth(width);
  };

  return (
      <>
        <div className='hp_widgets'>
          <div className='widgets-area'>
            <Weather screenWidth={width} />
            <Weight screenWidth={width} />
            <Currency screenWidth={width} />
            <Crypto screenWidth={width} />
            {/* <Todo /> */}
          </div>
        </div>
      </>
    );
}

export default MainPageProtected;