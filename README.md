# UN Statistic SDG Global Database

This repository contains custom functions developed for the analysis of the SDG indicator. All data used in this repository is publicly accessible through the Global Database API. Given the breadth of series (644) that covers 231 unique indicators, the custom functions were defined to faciliate:
* Analysis of regional progress
* Global progress review

The jupyter notebood depends on the *int_func.py* for its custom-defined function, including:
* `return_seriesCode(indicator: str)`
* `return_datapoints(seriesCode: str, geoAreaCode: str = '001', start_year: int, end_year: int, disagg: bool, plot: bool)


This repository adopted the UN M49 standards for the classification of regions.
