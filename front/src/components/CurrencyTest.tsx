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

    async function getNetCurrencyRate(rate_mode: string, rate_api: string, base: string, currency: string, rate_date: string) {
        const url = apiUrl + `api/core/get_exchange_rate/?format=json&mode=${rate_mode}&rate_api=${rate_api}&base=${base}&currency=${currency}&date=${rate_date}&skip_db=yes`;
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
                    units = `${currency.toUpperCase()} per ${resp_data.num_units} ${base.toUpperCase()}`;
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
        const rate_mode: string = formJson.rate_mode.toString();
        const rate_api: string = formJson.rate_api.toString();
        const base: string = formJson.base.toString();
        const currency: string = formJson.currency.toString();
        const rate_date: string = formJson.rate_date.toString();
        getNetCurrencyRate(rate_mode, rate_api, base, currency, rate_date);
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
        <Form method="post" onSubmit={handleSubmit} className="d-flex flex-wrap w-100">
            <fieldset className="border m-3 p-2">
                <legend>Mode:</legend>
                <div className="form-check">
                    <input type="radio" id="can_update" value="can_update" name="rate_mode" className="form-check-input p-0" defaultChecked />
                    <label htmlFor="can_update" className="form-check-label">Relaxed</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="db_only" value="db_only" name="rate_mode" className="form-check-input p-0" />
                    <label htmlFor="db_only" className="form-check-label">DB only</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="api_only" value="api_only" name="rate_mode" className="form-check-input p-0" />
                    <label htmlFor="api_only" className="form-check-label">API only</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="db_only_fd" value="db_only_fd" name="rate_mode" className="form-check-input p-0" />
                    <label htmlFor="db_only_fd" className="form-check-label">DB only (fixed date)</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="api_only_fd" value="api_only_fd" name="rate_mode" className="form-check-input p-0" />
                    <label htmlFor="api_only_fd" className="form-check-label">API only (fixed date)</label>
                </div>
            </fieldset>
            <fieldset className="border m-3 p-2">
                <legend>Exchange rate API:</legend>

                <div className="form-check">
                    <input type="radio" id="ca" name="rate_api" value="ca" className="form-check-input p-0" defaultChecked />
                    <label htmlFor="ca" className="form-check-label">CurrencyAPI</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="er" name="rate_api" value="er" className="form-check-input p-0" />
                    <label htmlFor="er" className="form-check-label">ExchangeRate</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="ecb" name="rate_api" value="ecb" className="form-check-input p-0" />
                    <label htmlFor="ecb" className="form-check-label">ECB (EUR)</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="nbp" name="rate_api" value="nbp" className="form-check-input p-0" />
                    <label htmlFor="nbp" className="form-check-label">NBP (PLN)</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="nbrb" name="rate_api" value="nbrb" className="form-check-input p-0" />
                    <label htmlFor="nbrb" className="form-check-label">NB RB (BYN)</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="belta" name="rate_api" value="belta" className="form-check-input p-0" />
                    <label htmlFor="nbrb" className="form-check-label">Belta (BYN)</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="myfin" name="rate_api" value="myfin" className="form-check-input p-0" />
                    <label htmlFor="nbrb" className="form-check-label">Myfin (BYN)</label>
                </div>

                <div className="form-check">
                    <input type="radio" id="boe" name="rate_api" value="boe" className="form-check-input p-0" />
                    <label htmlFor="boe" className="form-check-label">Bank of England (GBP)</label>
                </div>
            </fieldset>
            <div className="m-3 p-2">
                <div className="input-group mb-3">
                    <span className="input-group-text" id="base-field">Base</span>
                    <select id="base" name="base" className="form-select" defaultValue="usd">
                        <option value="usd">USD</option> 
                        <option value="eur">EUR</option> 
                        <option value="pln">PLN</option> 
                        <option value="byn">BYN</option> 
                        <option value="rur">RUR</option> 
                        <option value="gbp">GBP</option> 
                    </select>
                </div>
                <div className="input-group mb-3">
                    <span className="input-group-text" id="currency-field">Currency</span>
                    <select id="currency" name="currency" className="form-select"  defaultValue="pln">
                        <option value="usd">USD</option> 
                        <option value="eur">EUR</option> 
                        <option value="pln">PLN</option> 
                        <option value="byn">BYN</option> 
                        <option value="rur">RUR</option> 
                        <option value="gbp">GBP</option> 
                    </select>
                </div>
                <div className="input-group mb-3">
                    <span className="input-group-text" id="date-field">Date</span>
                    <input type="date" id="rate_date" name="rate_date" className="form-control m-0" defaultValue={today} />
                </div>
            </div>
            <div className="m-3 p-2 info-table">
                <table className="table">
                    <tbody>
                        <tr>
                            <th scope="row">Rate</th>
                            <td>{rate.rate} {rate.units}</td>
                        </tr>
                        <tr>
                            <th scope="row">Info</th>
                            <td>{rate.info}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div className="m-3 p-2">
                <button type="submit" className="btn btn-primary">Submit</button>
            </div>
        </Form>
    );
}

export default CurrencyTest;
