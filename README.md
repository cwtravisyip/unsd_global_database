# UN Statistic SDG Global Database

This repository contains custom functions developed for the analysis of the SDG indicator. All data used in this repository is publicly accessible through the Global Database API. Given the breadth of series (644) that covers 231 unique indicators, the custom functions were defined to faciliate:
* Analysis of regional progress
* Global progress review

The jupyter notebood depends on the *int_func.py* for its custom-defined function, including:
* `return_seriesCode(indicator: str)`
* `return_datapoints(seriesCode: str, geoAreaCode: str = '001', start_year: int, end_year: int, disagg: bool, plot: bool)`
* `seriesCode:str, regions: dict = region_dict, sdg:int = 0)`
* `return_datapoints`
* `regional analysis_vis`
* `progress_data`
* `progress_CARG_a`
* `progress_cr`
* `plot_trend_required`


This repository adopted the UN M49 standards for the classification of regions.

# Example output
![regional_data_fact_sheet_SSA_p1](https://user-images.githubusercontent.com/78350303/204587763-4566b620-0e33-4e38-9f69-5b0f97d27681.png)
![regional_data_fact_sheet_SSA_p2](https://user-images.githubusercontent.com/78350303/204587775-ab711809-d6e6-4a26-b058-8083c4c7f051.png)
