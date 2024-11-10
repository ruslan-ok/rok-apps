import { useEffect, useState } from "react";
// import SideBar from "./SideBar";
// import Content from "./Content";

function AppPage() {
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

    const isMobile = width < 768;
    let style;
    if (isMobile) {
        style = {
            flexDirection: 'column',
        };
    } else {
        style = {
            flexDirection: 'row',
        };
    }

    return (<div className="d-flex" style={style}>
        {/* <SideBar width={width} />
        <Content width={width} /> */}
    </div>);
}

export default AppPage;