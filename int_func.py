# function to extract only the aggregated value
import requests
import pandas as pd 
import matplotlib.pyplot as plt

base_url = 'https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Series'
# Set colour template with the index as the goal number, where 0 corredpond to the UN Blue
SDG_col = ['#009EDB','#E5243B',
 '#DDA63A',
 '#4C9F38',
 '#C5192D',
 '#FF3A21',
 '#26BDE2',
 '#FCC30B',
 '#A21942',
 '#FD6925',
 '#DD1367',
 '#FD9D24',
 '#BF8B2E',
 '#3F7E44',
 '#0A97D9',
 '#56C02B',
 '#00689D',
 '#19486A']

m49_region_code ={"001" : "world",
 "202" : "Sub-Saharan Africa",
 "015" : "Northern Africa",
 "419" : "Latin America and the Caribbean",
 "005" : "South America",
 "009" : "Oceania",
 "543" : "Oceania (excluding Australia and New Zealand)", # sometimes referred to Pacific Island Countries
 "053" : "Australia and New Zealand",
 "143" : "Central Asia",
 "145" : "Western Asia",
 "030" : "Eastern Asia",
 "034" : "South-Eastern Asia",
 "062" : "Central and Southern Asia",
 "753" : "Eastern and South-Eastern Asia",
 "747" : "Northern Africa and Western Asia",
 "513" : "Europe and Northern America",
 "199" : "Least Developed Countries (LDCs)",
 "432" : "Landlocked Developing Countries",
 "722" : "Small Island Developing States",
 "514" : "Developed regions (Europe, Cyprus, Israel, Northern America, Japan, Australia & New Zealand)"}

region_dict ={"001" : "world", # this is the dictionary containing the regional disaggregationunder the current scheme for the progress chart
    "202" : "Sub-Saharan Africa",
    "747" : "Northern Africa and Western Asia",
    "062" : "Central and Southern Asia",
    "753" : "Eastern and South-Eastern Asia",
    "419" : "Latin America and the Caribbean",
    "543" : "Oceania (excluding Australia and New Zealand)", # sometimes referred to Pacific Island Countries
    "005" : "South America",
    }
    

def aggregate_val(df):
    disaggregation_columns = df.columns.drop('value').drop('timePeriodStart').drop('Reporting Type')
    if len(disaggregation_columns.values) == 0:
        print('there is no disaggregation available.')
        return df
    else:
        disaggregation_columns = disaggregation_columns.values

        for col in disaggregation_columns:
            df_agg = df[(df[col]=='TOTAL') | (df[col]=='BOTHSEX') | (df[col]=='ALLAREA')| (df[col]=='All')| (df[col]=='ALLAGE')| (df[col]=='ALL') ]

        return df_agg

# requesting series list
series_list = pd.json_normalize(requests.get('https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Series/List').json())

# loading unsd list code list
unsd_list = pd.read_excel("https://unstats.un.org/sdgs/indicators/Global%20Indicator%20Framework%20after%202022%20refinement.English.xlsx", skiprows = [0,1]).iloc[:,2:4].dropna(subset = ['UNSD Indicator Codes†']).reset_index(drop= True)
unsd_list['indicator'] = unsd_list['Indicators'].apply(lambda x: x.split(' ')[0])
unsd_list['description'] = unsd_list.apply(lambda x: x[0].replace(x[2]+ ' ',""), axis = 1)
unsd_list.drop('Indicators', axis = 1,inplace = True)
unsd_list.rename(columns = {'UNSD Indicator Codes†':'indicator_code'}, inplace = True)

# print the seriesCode(s) when passed in the indicator as string
def return_seriesCode(*indicator:str):
    """
    return_seriesCode(indicator:str)
    >>> return_seriesCode('1.1.1')
            There exist 2 measure(s) for this indicators
            SI_POV_DAY1 : Proportion of population below international poverty line (%)
            SI_POV_EMP1 : Employed population below international poverty line, by sex and age (%)
    >>> return_seriesCode('C010101')
            There exist 2 measure(s) for this indicators
            SI_POV_DAY1 : Proportion of population below international poverty line (%)
            SI_POV_EMP1 : Employed population below international poverty line, by sex and age (%)
    """
    # check if the indicator passed is valid:
    for ind in indicator:
        if ind not in list(unsd_list['indicator']):
            print('Invalid indicator code')
        else:
        
            # return indicator number if UNSD Indicator Code is passed
            if ind[0] == 'C':
                if ind not in list(unsd_list['indicator_code']):
                    print('Invalid indicator code')
                else:
                    ind= unsd_list.loc[pd.Index(unsd_list['indicator_code']).get_loc(ind),'indicator']

            boolean = [] # initiate an empty boolean list to get the relevant series code from the series_list dataframe
            for indicators in  series_list['indicator']:
                if ind in indicators:
                    boolean.append(True)
                else:
                    boolean.append(False)
            # if no indicator exist
            if sum(boolean) == 0:
                print('There is no measure for this indicator')

            # if indicator(s) exist
            else:
                print('SDG Target {} \nThere exist {} measure(s) for this indicator:'.format(ind, sum(boolean)))
            
                for code, des in zip(series_list.loc[boolean,'code'],series_list.loc[boolean,'description']):
                    print(code, ':',des)

# return pandas dataframe when passed in indicator and the geoAreaCode (M49)
def return_datapoints(seriesCode: str , geoAreaCode :str = '001' ,start_year:int  = 2010,end_year:int = 2022,disagg = True, plot:bool = True):
    """
    The function returns a dataframe of the given series for it of the given region or country
    """
    if  seriesCode not in series_list['code'].values:
        print('Invalid series code')

    else:
        yearList = '","'.join([str(x) for x in range(start_year, end_year + 1)])
        uri = '/v1/sdg/Series/{seriesCode}/GeoArea/{geoAreaCode}/DataSlice?timePeriods=["{yearList}"]'.format(seriesCode = seriesCode,geoAreaCode= geoAreaCode,yearList = yearList)
        res = requests.get("https://unstats.un.org/sdgs/UNSDGAPIV5{}".format(uri)).json()
        data = res.pop('dimensions')
        metadata = res
        df = pd.json_normalize(data) # need to slice down to dimention to ignore the metadata

        # raise error if no data is found for the geoArea
        if len(df) == 0:
            df = pd.DataFrame([pd.NA for x in range(start_year, end_year)],index =[x for x  in range(start_year, end_year)],columns =['value'] )
            print('No datapoint was retrieved for the geoArea for this series: {}.\nRun the following code to get the regions with available data:'.format(seriesCode))
            print("""available_count = requests.get('https://unstats.un.org/sdgs/UNSDGAPIV5/v1/sdg/Series/{seriesCode}/GeoAreas').json() \n
            print(available_count)""".format(seriesCode=seriesCode))

            return df

        else:
            df['value'] = df['value'].astype('float')
            df['timePeriodStart'] = df['timePeriodStart'].astype('int')
            df.sort_values('timePeriodStart', inplace = True)

            # Refining df 'sex' column if exists
            if 'Sex' in df.columns:
                df.replace({'MALE':'Male','FEMALE' : 'Female','BOTHSEX':'All'}, inplace = True)

            # filter for disaggregation
            if disagg == False:
                df =aggregate_val(df)
            else:
                dis_col = df.columns.drop('value').drop('Reporting Type').drop('timePeriodStart').values
                if len(dis_col) == 1:
                    df = df.pivot(columns = dis_col[0], values = 'value', index = 'timePeriodStart')
                    df = df.reset_index()
                else:
                    print('More than one disaggregative dimension available: {}'.format(dis_col))

            # output explainer
            print('The year available: {}\n There exists {} data points for {}.'.format(df['timePeriodStart'].unique(),len(df),seriesCode))
            df = df.set_index('timePeriodStart')
            print(df.head())

            # plot the data
            if plot == True:
                df.plot(color = SDG_col, marker = 'o')
            return df


def regional_analysis_vis(seriesCode:str, regions: dict = region_dict, sdg:int = 0):
    """
    The current version assumes that 8 regions are plotted and is passed into the regions paramter as a dictionary in geoAreaCode: Name pair.
    The sdg parameter determines the color of the line plot.
    """
    des = series_list.loc[series_list[series_list['code']==seriesCode].index.values, 'description']


    df_data = {'year':[x for x in range(2010, 2023)]}
    df = pd.DataFrame(df_data)
    for key, value in region_dict.items():
        print(value)
        data = return_datapoints(seriesCode,start_year = 2010, end_year = 2022, geoAreaCode = key, disagg=False, plot= False)
        df = df.merge(data['value'], how = 'left',left_on = 'year',right_index = True,suffixes=(None, key))

    df.set_index('year',drop = True, inplace = True)   

    # determine the grid plot ncol and nrow
    nrows = 2
    ncols = round(len(regions.keys())/2)

            
    fig , ax = plt.subplots(nrows = nrows, ncols = ncols, figsize = (ncols * 12.5,20))
    i= 0 
    fig.suptitle(des.values[0], fontsize = 20)
    for x in range(0,nrows):
        # iterate through rows
        for y in range(0,ncols):
            if i < len(regions.keys()):
                # base plot
                ax[x,y].plot(df, color = 'lightgrey',zorder = 1)
                # grid highlight plot
                if df.iloc[:,i].count() != 0 :
                    ax[x,y]. plot(df.iloc[:,i], color = SDG_col[sdg], zorder = 2, linewidth = 3, marker = 'o')
                else:
                    ax[x,y].text(0.5,0.5,'No data point available.',horizontalalignment='center', verticalalignment='center', transform=ax[x,y].transAxes)
                # make sure the annotation above the point is within the axis and the annotation to be reasonable height
                y_division = (ax[x,y].get_yticks()[1] - ax[x,y].get_yticks()[0])/5

                for key, value in df.iloc[:,i].items():
                    ax[x,y].annotate('{:.1f}'.format(value),(key,value+y_division),fontsize = 10)

                # formatting
                ax[x,y].set_title(list(region_dict.values())[i])

                i +=1
            else:
                ax[x,y].remove()
                pass

def progress_data(df, y_t:int, y_0:int = 2015):
    # handling df with and without disaggregation columns
    if 'value' not in df.columns:
        df = aggregate_val(df)
    try:
        x_t = float(df.loc[y_t,'value'])
    except:
        year_latest = df.index.max()
        print("The latest year with data available: {}".format(year_latest))
        x_t = float(df.loc[year_latest,'value'])
    x_0 = float(df.loc[y_0,'value'])
    return x_t, x_0

# return the trend analysis of the indicator without numerical target
def progress_CARG_a(df,y_0:int = 2015):
    """
    Based on the methodology of the progress chart, the function return the actual compound rate of growth.
    df : dataframe for the values
    y_t: current year
    y_0: baseline year (default as 2015)
    """
    y_t = df.index.max()

    x_t, x_0 = progress_data(df, y_t,y_0)
    
    # computation
    carg_a = (x_t/x_0)**(1/(y_t-y_0))-1
    abs_carg_a = abs(carg_a)
    result = ""
    if abs_carg_a >0.01:
        result = 'Substantial progress/ on track'
    elif 0.01 >= abs_carg_a > 0.005:
        result = 'Fair progress but acceleration needed'
    elif 0.005 > abs_carg_a >= -0.01:
        result = 'Limited to no progress'
    else:
        result = 'Deterioration'
    
    print('The latest year of data available: {}'.format(y_t))
    return carg_a, result

# return the trend analysis of the indicator with numerical target
def progress_cr(df:pd.DataFrame,x:float ,y_0:int = 2015,):
    """
    This function  applies to indicators with explicitly stated target, returning the required carg and the actual carg. 
    x  : the target value by 2030 (note the unit of the dataframe)
    y_0: baseline year (default as 2015)
    """
    y_t = df.index.max()
    carg_a,result  = progress_CARG_a(df,y_0 = y_0)
    x_t, x_0 = progress_data(df, y_t,y_0)


    carg_r = (x/x_0)**(1/(2030-y_0))-1

    cr = carg_a/carg_r
    if cr > 0.95:
        result = 'Substantial progress/ on track'
    elif 0.95 > cr >= 0.5:
        result = 'Fair progress but acceleration needed'
    elif 0.5 > cr >= -0.1:
        result = 'Limited to no progress'
    else:
        result = 'Deterioration'
        

    return cr, carg_a, carg_r , result

def plot_trend_and_required(df: pd.DataFrame, base_year = 2015, end_year = 2030, carg_a = None,carg_r = None, sdg = 0, target_value = None, column_name:str = 'value', target_year = 2030, mul_digit = True):
    """
    The function returns a time series plot from the 2015. Where 2015 data is not available, the data point is generated by linear interpolation. Where baseline year is after 2015, the plot begins at baseline year.
    Given the dataframe, the function generates the carg_a. Passing in float into carg_a would override this.
    The target value could be passed in if known. If not, the function accept the carg_r argument, which would generate the target value.
    The sign of the carg_a and the carg_r matters.
    base_year (str):    the year for which the CARG shall be computed
    column_name (str):  this provides the flexibility to pass in DataFrame where the data point is not recorded under the 'value' column
    mul_digit (bool):   this determine the persicion of the annotation of the baseline, latest, projected and target data points
    """
    def interpolate_2015val(df:pd.DataFrame, sdg:int,column_name = 'value'):
        # linear interpolation
        lower_year = df.index[df.index<2015].max()
        upper_year =  df.index[df.index>2015].min()
        pre_val = df.loc[lower_year, column_name]
        post_val = df.loc[upper_year, column_name]
        interpolated_2015val =  pre_val +(post_val - pre_val) / (upper_year - lower_year) *(2015-lower_year)  
        return interpolated_2015val

    font_color = ['#FFFFFF','#FFFFFF','#000000','#FFFFFF', '#FFFFFF','#FFFFFF','#FFFFFF','#000000','#FFFFFF','#FFFFFF','#FFFFFF',
                    '#000000','#FFFFFF','#FFFFFF','#FFFFFF','#FFFFFF','#FFFFFF','#FFFFFF']
    year_latest = df.index.max()
    data_latest = df.loc[df.index.max(),column_name]
    markersize = 15

    fig, ax = plt.subplots()
    # parameters to consider 
    df_renamed = df.rename(columns={column_name:'value'}) # the function carg_a is not adapted to take the column_name arg
    if carg_a == None:
        carg_a = progress_CARG_a(df_renamed,y_0 = base_year)[0]
    if carg_r != None:
        year = [x for x in range(base_year, end_year+1)]
        value = df_renamed.loc[year_latest, 'value'] 
        target_value = value * (1+carg_r)**(end_year - base_year)
    

    if base_year < 2015:
        try:
            # see if 2015 exist in the dataframe
            df.loc[2015, column_name]
            plot_base_year = 2015
            val_2015 = df.loc[plot_base_year,column_name]

        except:
            # execute if 2015 is not in the dataframe and base year is below 2015
            val_2015 = interpolate_2015val(df, sdg, column_name)
            print('Data point for 2015 is estimated by interpolation: {}'.format(val_2015))
            df.loc[2015, column_name] = val_2015
            df = df.sort_index()
            plot_base_year = 2015
        
    else:
        plot_base_year= base_year # base_year could be greater than 2015
        val_2015 = df.loc[plot_base_year,column_name]
    

    if not mul_digit:
        fontsize = 8
    else:
        fontsize = 11

    # plotting the available data 
    df.loc[plot_base_year:].plot(color = SDG_col[sdg], legend = False, ax =ax)
    # base year datapoint
    ax.plot(plot_base_year,val_2015,markersize = markersize, marker = 's', color = SDG_col[sdg])
    ax.annotate("{:.0f}".format(val_2015) if mul_digit else "{:.1f}".format(val_2015),(plot_base_year,val_2015),horizontalalignment = 'center',verticalalignment = 'center', color = font_color[sdg],fontsize = fontsize)
    # latest year figure
    ax.plot(year_latest, data_latest, markersize = markersize, marker = 's', color = SDG_col[sdg])
    ax.annotate("{:.0f}".format(data_latest) if mul_digit else "{:.1f}".format(data_latest), (year_latest,data_latest),horizontalalignment = 'center',verticalalignment = 'center',color = font_color[sdg],fontsize = fontsize)

    # plot target datapoint
    if target_value == 0:
        plot_y = 0
        division = ax.get_yticks()[1] - ax.get_yticks()[0]
        ax.plot(end_year,division/2,markersize = markersize, marker = 's', color = 'lightgrey', zorder= 2)
        ax.annotate("{:.0f}".format(target_value) if mul_digit else "{:.1f}".format(target_value),(end_year,plot_y),horizontalalignment = 'center',verticalalignment = 'center',fontsize = fontsize)
    else:
        ax.plot(end_year,target_value,markersize = markersize, marker = 's', color = 'lightgrey', zorder= 2)
        ax.annotate("{:.0f}".format(target_value) if mul_digit else "{:.1f}".format(target_value),(end_year,target_value),horizontalalignment = 'center',verticalalignment = 'center',fontsize = fontsize)
    # target trajectory line
    year = [year_latest, end_year]
    value_list = [data_latest, target_value]
    pd.Series(value_list,index = year).plot(ax =ax , linestyle = ':', color = 'darkgrey', zorder= 1)

    # getting trend line 
    year = [x for x in range(year_latest, end_year + 1)] 
    trend_value = df.loc[year_latest, column_name] 
    trend_value_list = [trend_value * (1+carg_a)**i for i in range(len(year))]
    pd.Series(trend_value_list,index = year).plot(ax =ax , linestyle = '--', color = SDG_col[sdg])
    # extrapolated datapoint
    ax.plot(2030,trend_value_list[-1],marker = 's',markersize = markersize,color = SDG_col[sdg],zorder= 3)
    ax.annotate("{:.0f}".format(trend_value_list[-1]) if mul_digit else "{:.1f}".format(trend_value_list[-1]),(2030,trend_value_list[-1]), zorder = 3,horizontalalignment = 'center',verticalalignment = 'center',color = font_color[sdg],fontsize = fontsize)

  
    # plot formatting
    ax.set_xlim(2014,2030.5)
    ax.xaxis.set_major_locator(plt.MultipleLocator(5))
    ax.set_xlabel('')
    ax.spines['left'].set_color('darkgrey')
    ax.spines['bottom'].set_color('darkgrey')
    ax.tick_params(axis='y', colors='darkgrey',labelcolor = 'black')

    return ax

