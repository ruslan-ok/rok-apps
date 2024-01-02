import { useState } from 'react';
import {
    Form,
} from "react-router-dom";
import "./CurrencyTest.css";
import { apiUrl } from './auth/Auth';

interface RateInfo {
    rate: number|undefined;
    info: string;
    units: string;
  }


function CurrencyTest() {
    const [rate, setRate] = useState<RateInfo>({rate: undefined, info: '', units: ''});

    async function getNetCurrencyRate(rate_api: string, base: string, currency: string, rate_date: string) {
        const url = apiUrl + `api/core/get_exchange_rate/?format=json&rate_api=${rate_api}&base=${base}&currency=${currency}&date=${rate_date}&skip_db=yes`;
        const cred: RequestCredentials = 'include';
        const options = {
            method: 'GET',
            headers: {'Content-type': 'application/json'},
            credentials: cred,
        };
        const response = await fetch(url, options);
        if (response.ok) {
            let resp_data = await response.json();
            if (resp_data) {
                let units = '';
                if (resp_data.rate)
                    units = `${currency.toUpperCase()} per ${base.toUpperCase()}`;
                let info;
                if (typeof resp_data.info == 'string')
                    info = resp_data.info;
                else
                    info = JSON.stringify(resp_data.info);
                const rate = {
                    rate: resp_data.rate, 
                    info: info,
                    units: units
                };
                setRate(rate);
            }
        }
    }
    
    function handleSubmit(e: any) {
        e.preventDefault();
        const form = e.target;
        const formData = new FormData(form);
        const formJson = Object.fromEntries(formData.entries());
        const rate_api: string = formJson.rate_api.toString();
        const base: string = formJson.base.toString();
        const currency: string = formJson.currency.toString();
        const rate_date: string = formJson.rate_date.toString();
        getNetCurrencyRate(rate_api, base, currency, rate_date);
    }
            
    var date = new Date();

    var day = date.getDate().toString();
    var month = (date.getMonth() + 1).toString();
    var year = date.getFullYear().toString();
    if (+month < 10)
        month = "0" + month;
    if (+day < 10)
        day = "0" + day;

    var today = year + "-" + month + "-" + day;
    return (
        <div className="currency-test">
            <Form method="post" className="d-flex" onSubmit={handleSubmit}>
                <fieldset>
                    <legend>Exchange rate API:</legend>

                    <div>
                        <input type="radio" id="ecb" name="rate_api" value="ecb" />
                        <label htmlFor="ecb">ECB</label>
                    </div>

                    <div>
                        <input type="radio" id="nbp" name="rate_api" value="nbp" />
                        <label htmlFor="nbp">NBP</label>
                    </div>

                    <div>
                        <input type="radio" id="nbrb" name="rate_api" value="nbrb" />
                        <label htmlFor="nbrb">NB RB</label>
                    </div>

                    <div>
                        <input type="radio" id="boe" name="rate_api" value="boe" />
                        <label htmlFor="boe">Bank of England</label>
                    </div>

                    <div>
                        <input type="radio" id="er" name="rate_api" value="er" />
                        <label htmlFor="er">ExchangeRate</label>
                    </div>

                    <div>
                        <input type="radio" id="ca" name="rate_api" value="ca" defaultChecked />
                        <label htmlFor="ca">CurrencyAPI</label>
                    </div>
                </fieldset>
                <div className="right-fields">
                    <div className="param-fields d-flex">
                        <label htmlFor="base">Base</label>
                        <select id="base" name="base" defaultValue="usd">
                            <option value="usd">USD</option> 
                            <option value="eur">EUR</option> 
                            <option value="pln">PLN</option> 
                            <option value="byn">BYN</option> 
                            <option value="gbp">GBP</option> 
                        </select>
                        <label htmlFor="base">Currency</label>
                        <select id="currency" name="currency" defaultValue="eur">
                            <option value="usd">USD</option> 
                            <option value="eur">EUR</option> 
                            <option value="pln">PLN</option> 
                            <option value="byn">BYN</option> 
                            <option value="gbp">GBP</option> 
                        </select>
                        <input type="date" id="rate_date" name="rate_date" defaultValue={today}/>
                    </div>
                    <div className="rate-result">
                        <table>
                            <tbody>
                                <tr>
                                    <th>Rate</th>
                                    <td>{rate.rate} {rate.units}</td>
                                </tr>
                                <tr>
                                    <th>Info</th>
                                    <td>{rate.info}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div className="buttons">
                    <button type="submit" className="button btn btn-primary">Submit</button>
                </div>
            </Form>

        </div>
    );
}

export default CurrencyTest;
