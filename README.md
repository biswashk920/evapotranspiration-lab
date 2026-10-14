# ET Compare

**[Open the live app](https://biswashk920.github.io/evapotranspiration-lab/)**

Calculate **reference evapotranspiration (ET₀)** from weather data and compare three standard methods side by side: **FAO-56 Penman-Monteith**, **Hargreaves-Samani** and **Thornthwaite**.

- **Hosting:** served by GitHub Pages from the `/docs` folder.
- **No installs needed:** the app is one HTML file in `docs/index.html`. It works offline and nothing is uploaded anywhere.
- **Python reference:** `etcompare/`, pure Python, no dependencies.

## What is evapotranspiration?

Evapotranspiration (ET) is the water that goes from the land surface back into the atmosphere. It has two parts:

- **Evaporation:** water turning to vapour from soil, wet leaves, rivers, lakes and reservoirs.
- **Transpiration:** water that plants draw up through their roots and release as vapour through tiny leaf pores (stomata).

The two happen together and are hard to separate in the field, so they are treated as one number, normally in **millimetres per day** (1 mm over a surface equals 1 litre per square metre).

ET is driven by **energy and dryness of the air**. Four weather factors control it:

1. **Radiation.** Sunlight supplies the energy to turn liquid water into vapour. This is usually the largest driver.
2. **Temperature.** Warm air holds more vapour, and warm surfaces evaporate faster.
3. **Humidity.** The drier the air, the stronger the pull on water (the vapour pressure deficit).
4. **Wind.** Wind carries away moist air next to the surface and keeps the pull strong.

### Reference ET₀ versus actual ET

- **ET₀ (reference evapotranspiration)** is the *demand* of the atmosphere. It is defined for a standard, well-watered grass surface (0.12 m tall, fixed surface resistance, albedo 0.23). It depends only on weather, so it can be calculated anywhere from weather data.
- **Actual ET (ETa)** is what really happens. It also depends on the crop, its growth stage and how much water is in the soil. In dry soil, ETa is lower than ET₀.
- Crop water use is usually estimated as ETc = Kc × ET₀, where Kc is a crop coefficient. This app stops at ET₀ and does not model crops.

## Why it matters

- **Water balance.** In most catchments, ET returns more than half of the rainfall to the atmosphere. Runoff and recharge are what is left, so a wrong ET gives a wrong water balance.
- **Irrigation.** Farms use ET₀ and crop coefficients to decide how much water crops need and when.
- **Hydrological modelling.** Models such as SWAT, HEC-HMS and others need potential ET as an input.
- **Reservoir and water-supply planning.** Evaporation losses reduce yield.
- **Drought and climate studies.** Warming raises atmospheric demand, so ET₀ trends show how water stress is changing.
- **Data availability.** Full Penman-Monteith needs four weather variables that many stations do not record. Simpler methods exist for that reason, and this app shows how much accuracy you give up by using them.

## How to use the web app

Open `docs/index.html` in a browser, or use the GitHub Pages link. There are four tabs.

### 1. Calculator
Calculates one day.
1. Pick a **date** and set **latitude** (north positive) and **elevation**.
2. Move the sliders for **Tmax, Tmin, RH max, RH min, wind speed at 2 m and sunshine hours**.
3. Read the result cards: Penman-Monteith, Hargreaves, and the difference between them.
4. The **steps table** shows every intermediate value (vapour pressures, Ra, Rs, Rn and so on) so you can follow the calculation.
5. The **sensitivity bars** show how much ET₀ changes if one input rises (temperatures by 1 °C, others by 10%). This tells you which measurement matters most for your site.

### 2. Compare methods
Calculates a full year.
1. Choose a **climate preset** (Kathmandu Valley, Terai plains, dry mountain, humid tropics, hot desert). The presets are rounded illustrative values, not observed station records.
2. Change latitude and elevation, or **edit any monthly value** in the table. The chart and totals update immediately.
3. Read the chart (mm/month for each method) and the annual totals with the percentage difference from Penman-Monteith.

Daily ET₀ is computed for the middle day of each month and multiplied by the number of days. In this tab, RH max is taken as mean RH + 10 and RH min as mean RH − 15 (limited to 100 and 5), because monthly tables usually give only mean humidity.

### 3. Upload CSV
1. Prepare a file with the header `date,tmax,tmin,rh_mean,wind,sunshine` (date as `YYYY-MM-DD`, wind at 2 m in m/s, sunshine in hours). See `examples/sample_weather.csv`.
2. Set latitude and elevation, then choose the file (or press *Load sample data*).
3. Check the chart and totals, then press *Download results CSV*. Rows with missing values, bad dates or Tmin above Tmax are skipped and counted in the message.

### 4. How it works
The equations and the limits of each method.

## The three methods

| Method | Inputs | Time step | Typical behaviour |
|---|---|---|---|
| **Penman-Monteith (FAO-56)** | Temperature, humidity, wind, sunshine or radiation, latitude, elevation | Daily | FAO's standard. Best accuracy when data are good. |
| **Hargreaves-Samani** | Tmax, Tmin, latitude | Daily | Reasonable in many places. Can overestimate in humid, cloudy areas and miss the effect of strong wind. |
| **Thornthwaite** | Monthly mean temperature, latitude | Monthly | Simplest. Often underestimates in dry and tropical climates. |

## More methods and tools (in the Compare tab)

- **Seven lines side by side.** Penman-Monteith, Hargreaves, Hargreaves (calibrated), Thornthwaite, Penman-Monteith with temperature only, Priestley-Taylor and Blaney-Criddle. Tick the boxes above the chart to show or hide lines. Each total shows the percentage difference and monthly RMSE against Penman-Monteith.
- **Temperature-only Penman-Monteith.** The FAO-56 procedure for stations that record only Tmax and Tmin: solar radiation from the daily temperature range, dew point from Tmin minus 2 °C, and a default wind of 2 m/s. Useful where humidity, wind and radiation are not measured.
- **Hargreaves local calibration.** A least-squares factor k fitted to Penman-Monteith, with the error before and after. It is fitted on the same 12 months it is tested on, so treat it as a best case.
- **Warming slider.** Adds 0 to 4 °C to temperature and shows the change in annual ET₀. Humidity, wind and sunshine are held constant, so it is a sensitivity test, not a climate projection.
- **Rainfall and aridity.** Rainfall versus ET₀, the aridity index (rain / ET₀) with its UNEP class, and the number of months where ET₀ exceeds rainfall.
- **Season player (its own tab).** It starts playing when you open the tab. Press *Pause* to stop, or drag the slider to pick a day. Watch ET₀, daylight and extraterrestrial radiation change through the year, with a sun that grows with radiation and vapour that increases with ET₀.

## Python usage

```python
from etcompare import penman_monteith, hargreaves, thornthwaite

et0 = penman_monteith(tmax=21.5, tmin=12.3, rh_max=84, rh_min=63, u2=2.08,
                      lat=50.8, elev=100, doy=187, sunshine=9.25)   # 3.88 mm/day
hg = hargreaves(21.5, 12.3, 50.8, 187)
# also: penman_monteith_temp_only, priestley_taylor, blaney_criddle, fit_hargreaves_coefficient
monthly = thornthwaite([19, 22, 26, 29, 30, 29, 28, 28, 27, 25, 22, 19], lat=27.7)
```

Wind measured at another height can be converted with `etcompare.core.wind_at_2m(uz, z)`.

## Validation

- `tests/test_fao56.py` reproduces worked examples from FAO Irrigation and Drainage Paper 56: saturation vapour pressure (Example 2), extraterrestrial radiation (Example 8) and the Uccle, Belgium daily ET₀ of 3.9 mm/day (Example 18; this code gives 3.88).
- `tests/check_web_parity.js` runs the JavaScript inside `docs/index.html` and checks it matches the Python code (difference below 1e-6).

Run them:

```
python tests/test_fao56.py        # or: python -m pytest tests
node tests/check_web_parity.js
```

## Limitations

- Penman-Monteith in this app uses sunshine hours to estimate solar radiation (Angström coefficients 0.25 and 0.50). Local calibration, or measured radiation, is better. The Python function accepts `rs=` directly.
- Daily soil heat flux is taken as zero.
- The Thornthwaite and Hargreaves results are shown for comparison, not as replacements for Penman-Monteith.
- Monthly values in the comparison tab come from mid-month days, so they smooth out day-to-day variation.
- The climate presets, including rainfall, are illustrative values, not observed station records.
- Priestley-Taylor uses the standard alpha of 1.26, and Blaney-Criddle is the simple uncorrected form. Both are for comparison.

## Project layout

```
etcompare/        Python reference implementation
docs/index.html   web app (GitHub Pages)
tests/            FAO-56 checks and Python/JS parity check
examples/         sample daily weather CSV
```

## Reference

Allen, R. G., Pereira, L. S., Raes, D., Smith, M. (1998). *Crop evapotranspiration: guidelines for computing crop water requirements.* FAO Irrigation and Drainage Paper 56.

## License

MIT
