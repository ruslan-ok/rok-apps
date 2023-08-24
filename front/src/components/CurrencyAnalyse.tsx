import { useLoaderData } from 'react-router-dom';
import Currency from './widgets/Currency';

import { apiUrl, getAccessToken } from './Auth';
import './CurrencyAnalyse.css';

interface CurrencyInfo {
  id: number;
  code: string;
}

interface CurrencyData {
  currList: CurrencyInfo[];
}

export async function loader(): Promise<CurrencyData> {
  const token = getAccessToken();
  const options = {method: 'GET', headers: {'Content-type': 'application/json'}};
  const res = await fetch(apiUrl +  'api/react/currency?userToken=' + token, options);
  const resp_data = await res.json();
  const data: CurrencyData = JSON.parse(resp_data.json_data);
  return data;
}

function CurrencyAnalyse() {
  const data = useLoaderData() as CurrencyData;
  const currList = data.currList.map(element => {
    return (<li key={element.id}>{element.code}</li>);
  });
  return (
    <>
      <div id='currency-analyse'>
        <div className='static-widgets'>
          <Currency width={1200} height={800} />
        </div>
        <ul>
          {currList}
        </ul>
      </div>
    </>
  );
}

export default CurrencyAnalyse;