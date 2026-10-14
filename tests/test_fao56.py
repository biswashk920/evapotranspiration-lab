"""Checks against worked examples in FAO Irrigation and Drainage Paper 56 (Allen et al., 1998).
Run with:  python -m pytest tests   (or)   python tests/test_fao56.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from etcompare import penman_monteith, hargreaves, thornthwaite, extraterrestrial_radiation, daylight_hours
from etcompare.core import sat_vp, wind_at_2m

def test_saturation_vapour_pressure():   # Example 2
    assert abs(sat_vp(24.5) - 3.075) < 0.005

def test_extraterrestrial_radiation():   # Example 8: 3 Sep, 20 deg S
    assert abs(extraterrestrial_radiation(-20, 246) - 32.2) < 0.2
    assert abs(daylight_hours(-20, 246) - 11.7) < 0.1

def test_uccle_example_18():             # 6 July, Uccle, Belgium -> 3.9 mm/day
    d = penman_monteith(21.5, 12.3, 84, 63, wind_at_2m(2.78, 10), 50.8, 100, 187, sunshine=9.25, details=True)
    assert abs(d["et0"] - 3.9) < 0.1
    assert abs(d["Rn"] - 13.3) < 0.2  # net radiation, MJ m-2 day-1

def test_hargreaves_close_to_pm_in_temperate_summer():
    pm = penman_monteith(21.5, 12.3, 84, 63, 2.08, 50.8, 100, 187, sunshine=9.25)
    assert abs(hargreaves(21.5, 12.3, 50.8, 187) - pm) < 1.0

def test_thornthwaite_shape():
    pet = thornthwaite([-2, 0, 5, 10, 15, 19, 22, 21, 16, 10, 4, 0], 45)
    assert pet[0] == 0 and pet[6] == max(pet) and 0 < sum(pet) < 800

def test_other_methods_sane():
    from etcompare import penman_monteith_temp_only, priestley_taylor, blaney_criddle, fit_hargreaves_coefficient
    pm = penman_monteith(21.5, 12.3, 84, 63, 2.08, 50.8, 100, 187, sunshine=9.25)
    assert abs(penman_monteith_temp_only(21.5, 12.3, 50.8, 100, 187) - pm) < 1.5
    assert abs(priestley_taylor(21.5, 12.3, 84, 63, 2.08, 50.8, 100, 187, sunshine=9.25) - pm) < 1.5
    assert 1 < blaney_criddle(21.5, 12.3, 50.8, 187) < 8
    assert abs(fit_hargreaves_coefficient([2, 4], [1, 2]) - 2) < 1e-12

if __name__ == "__main__":
    for k, f in list(globals().items()):
        if k.startswith("test_"): f(); print("ok", k)
