import { useState, useEffect } from 'react';

function MainPageSearch({searchString}: {searchString: string}) {
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
        <div>
            <div>Search results for the Search string "{searchString}"</div>
            <div>Window width: {width}</div>
        </div>
      </>
    );
}

export default MainPageSearch;