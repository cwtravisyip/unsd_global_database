# UN Statistic SDG Global Database

This repository contains custom functions under `int_func.py` developed for the analysis of the SDG indicator. The use case of these functions are showcased in other notebook file. All data used in this repository is publicly accessible through the Global Database API. Given the breadth of series (644) that covers 231 unique indicators, the custom functions were defined to faciliate:
* Analysis of regional progress
* Global progress review

The jupyter notebook depends on the *int_func.py* for its custom-defined function, including:
* `return_seriesCode(indicator: str)`
* `return_datapoints(seriesCode: str, geoAreaCode: str = '001', start_year: int, end_year: int, disagg: bool, plot: bool)`
* `return_datapoints`
* `regional analysis_vis`
* `progress_data`
* `progress_CARG_a`
* `progress_cr`
* `plot_trend_required`


This repository adopted the UN M49 standards for the classification of regions.

## Project output
### Regional data fact sheet
![regional_data_fact_sheet_SSA_p1](https://user-images.githubusercontent.com/78350303/204588291-25488592-f66e-47f3-a074-15955ece0c0f.jpg)
![regional_data_fact_sheet_SSA_p2](https://user-images.githubusercontent.com/78350303/204588294-d3ea481b-fb75-48e7-97c4-3cf5592c6549.jpg)


### Progress chart calculation 
![ind_020102_03](https://user-images.githubusercontent.com/78350303/204906560-5c70f199-d539-4c02-875d-f5d849da7dbd.jpg)


### Regional analysis
![7_1_EG_EGY_CLEAN](https://user-images.githubusercontent.com/78350303/204618662-b9dc292c-ac74-46ff-b158-5839ef5e0e2e.jpg)
