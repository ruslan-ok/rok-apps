import React from 'react';
import {
  useLoaderData,
} from 'react-router-dom';

import { MainPageData } from './MainPage';
import Header from './header/Header';
import { apiUrl } from './Auth';
// import { Chart } from 'react-chartjs-2';

import './MainPageProtected.css';

interface WidgetInfo {
  id: string;
  name: string;
}

export interface ProtectedData {
  widgets: WidgetInfo[];
}

// async function buildChart(id: string) {
//   const url = apiUrl + 'api/get_chart_data/?mark=' + id;
//   const options: RequestInit = {
//     method: 'GET',
//     headers: {'Content-type': 'application/json'},
//     credentials: 'include',
//   };
//   const response = await fetch(url, options);
//   if (!response.ok) {
//     return;
//   }
//   let data = await response.json();
//   let chartEl: HTMLCanvasElement | null = document.getElementById(id + 'Chart') as HTMLCanvasElement;
//   if (chartEl) {
//       const ctx = chartEl.getContext('2d');
//       if (ctx) {
//         // @ts-ignore
//         new Chart(ctx, data);
//         if (chartEl.parentNode && chartEl.parentNode.firstElementChild) {
//           chartEl.parentNode.removeChild(chartEl.parentNode.firstElementChild);
//         }
//       }
//   }
// }

async function loadWidget(id: string) {
  const url = apiUrl + 'api/get_widget/?id=' + id;
  const options: RequestInit = {method: 'GET', credentials: 'include'};
  const response = await fetch(url, options);

  if (!response.ok) {
      const mess = `HTTP error! Widget: ${id}, Status: ${response.status}`;
      console.log(mess);
      throw new Error(mess);
  }
  let data = await response.text();
  let widget = document.getElementById('id_hp_widget_' + id);
  if (widget) {
    if (data == '') {
      widget.classList.add('d-none');
    } else {
      widget.innerHTML = data;
      // const chartList = ['health', 'crypto', 'currency', 'weather'];
      // if (chartList.includes(id)) {
      //   buildChart(id);
      // }
    }
  }
}

function MainPageProtected({windowWidth}: {windowWidth: number}) {
    let data = useLoaderData() as MainPageData;

    React.useEffect(() => {
      const widget_ids = Array.from(data.protectedData.widgets.map((item) => item.id));
      for (const id of widget_ids) {
        loadWidget(id)
      }
    }, []);

    let widgets = data.protectedData.widgets.map((item) => {
      const id = 'id_hp_widget_' + item.id;
      return (
        <div className='hp-widget' id={id} key={id} >
          <div className='loader'></div>
        </div>
      );
    });

    return (
      <>
        <Header windowWidth={windowWidth} />
        <div className='hp_widgets'>
          {widgets}
        </div>
      </>
    );
}

export default MainPageProtected;