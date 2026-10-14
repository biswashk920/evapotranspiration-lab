// Runs the JS core inside docs/index.html and compares it with the Python reference. Usage: node tests/check_web_parity.js
const fs = require('fs'), cp = require('child_process');
const html = fs.readFileSync(__dirname + '/../docs/index.html', 'utf8');
const core = html.split('// ==== ET CORE START')[1].split('// ==== ET CORE END')[0];
const { PM, HG, TH, PMt, PT, BC } = new Function(core + '; return {PM,HG,TH,PMt,PT,BC};')();
const py = JSON.parse(cp.execSync(`python3 -c "
import json,sys; sys.path.insert(0,'.')
from etcompare import *
print(json.dumps([penman_monteith(21.5,12.3,84,63,2.08,50.8,100,187,sunshine=9.25), hargreaves(21.5,12.3,50.8,187), penman_monteith(34,22,70,35,1.5,13.7,2,100,sunshine=7), thornthwaite([19,22,26,29,30,29,28,28,27,25,22,19],27.7), penman_monteith_temp_only(21.5,12.3,50.8,100,187), priestley_taylor(21.5,12.3,84,63,2.08,50.8,100,187,sunshine=9.25), blaney_criddle(21.5,12.3,50.8,187)]))"`, { cwd: __dirname + '/..' }));
const a = { tmax: 21.5, tmin: 12.3, rhmax: 84, rhmin: 63, u2: 2.08, lat: 50.8, elev: 100, doy: 187, sun: 9.25 };
const js = [PM(a).et0, HG(a), PM({ tmax: 34, tmin: 22, rhmax: 70, rhmin: 35, u2: 1.5, lat: 13.7, elev: 2, doy: 100, sun: 7 }).et0, TH([19,22,26,29,30,29,28,28,27,25,22,19], 27.7), PMt(a), PT(a), BC(a)];
const flat = x => x.flat(), A = flat(py), B = flat(js);
const worst = Math.max(...A.map((v, i) => Math.abs(v - B[i])));
console.log('max |python - js| =', worst.toExponential(2)); process.exit(worst < 1e-6 ? 0 : 1);
