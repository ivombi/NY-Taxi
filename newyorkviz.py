# nytaxiviz.py

""" New york taxi vizualisation class"""

#importing necessary libraries
from __future__ import print_function
from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets
import pandas as pd
import numpy as np
from sort_dataframeby_monthorweek import Sort_Dataframeby_Month
import matplotlib.pyplot as plt
import seaborn as sns


import warnings
warnings.filterwarnings('ignore')

class NYTaxiViz():
    """Class for producing a visualization dashboard for New York Taxi"""
    
    # Class variables shared by all instances
        
    stat_list = [('mean','mean'),('median','median')]
    field_list = [('Trip duration','trip_duration'),('Trip Amount','total_amount'),('Tips Amount','tip_amount'),\
                  ('Trip distance','trip_distance')] 
    
    def __init__(self,df_yellow=0,df_green=0, df_loc=0):
        
        """Initialize NYTaxiViz attributes"""
        
        self._df_yellow = df_yellow # validate via property
        self._df_green  = df_green # validate via property
        self._df_loc = df_loc
       
        
        # Class variables shared by all instances
        
        stat_list = [('mean','mean'),('median','median')]
        field_list = [('Trip duration','trip_duration'),('Trip Amount','total_amount'),('Tips Amount','tip_amount'),\
                  ('Trip distance','trip_distance')]  


        
    @property
    def df_yellow(self):
        return self._df_yellow
    
    @df_yellow.setter
    def df_yellow(self,directory):
        self._df_yellow = directory
    
    @property
    def df_green(self):
        return self._df_green
    
    @df_green.setter
    def df_green(self,directory):
        self._df_green = directory
        
    @property
    def df_loc(self):
        return self._df_loc
    
    @df_loc.setter
    def df_loc(self,directory):
        self._df_loc = directory
    
    
    def set_directory(self,df_y,df_g, df_loc):
        """Set all directories at once"""
        self.df_yellow = df_y
        self.df_green = df_g
        self.df_loc = pd.read_csv(df_loc)
        
    def process(self):
        """Importing the needed dataframes and process them to output a single dataframe"""
        
        df_y = pd.read_csv(self.df_yellow)
        df_g = pd.read_csv(self.df_green)
        df_loc = self.df_loc
         
        # Filtering needed columns 
        df_y = df_y[['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'trip_distance', 'pulocationid', \
         'dolocationid', 'tip_amount', 'total_amount', 'fare_amount', 'trip_month' ]]

        df_g = df_g[['lpep_pickup_datetime', 'lpep_dropoff_datetime', 'trip_distance', 'pulocationid', \
         'dolocationid', 'tip_amount', 'total_amount', 'trip_month' ]]
        
        # Ensuring pickup and dropoff fields are datetime

        df_y['tpep_pickup_datetime'] = pd.to_datetime(df_y['tpep_pickup_datetime'])
        df_y['tpep_dropoff_datetime'] = pd.to_datetime(df_y['tpep_dropoff_datetime'])
        df_g['lpep_pickup_datetime'] = pd.to_datetime(df_g['lpep_pickup_datetime'])
        df_g['lpep_dropoff_datetime'] = pd.to_datetime(df_g['lpep_dropoff_datetime'])
        
        # Extracting new columns
        df_y['day'] = df_y['tpep_pickup_datetime'].apply(lambda time: time.dayofweek)
        df_y['day_name'] = df_y['tpep_pickup_datetime'].dt.day_name()
        df_y['month_name'] = df_y['tpep_pickup_datetime'].dt.month_name()
        df_y['year'] = pd.DatetimeIndex(df_y.loc[:,'tpep_pickup_datetime']).year
        df_y['hour'] = pd.DatetimeIndex(df_y.loc[:,'tpep_pickup_datetime']).hour
        df_y['trip_duration'] = (df_y['tpep_dropoff_datetime'] -\
                                 df_y['tpep_pickup_datetime']).astype('timedelta64[m]')
        df_y['uc_mile'] = df_y['total_amount']/df_y['trip_distance']
        df_y['taxi_type'] = 'yellow'

        df_g['day'] = df_g['lpep_dropoff_datetime'].apply(lambda time: time.dayofweek)
        df_g['day_name'] = df_g['lpep_dropoff_datetime'].dt.day_name()
        df_g['month_name'] = df_g['lpep_dropoff_datetime'].dt.month_name()
        df_g['year'] = pd.DatetimeIndex(df_g.loc[:,'lpep_pickup_datetime']).year
        df_g['hour'] = pd.DatetimeIndex(df_g.loc[:,'lpep_pickup_datetime']).hour
        df_g['trip_duration'] = (df_g['lpep_dropoff_datetime'] - \
                                 df_g['lpep_pickup_datetime']).astype('timedelta64[m]')
        df_g['uc_mile'] = df_g['trip_distance']/df_g['total_amount']
        df_g['taxi_type'] = 'green'
        
        # Renaming the schema of green taxi to match that of yellow
        df_g.rename(columns={'lpep_dropoff_datetime':'tpep_dropoff_datetime', 'lpep_pickup_datetime': 'tpep_pickup_datetime'},inplace=True)
        
        # concat both datasets
        df_concat = pd.concat([df_y,df_g])
        
        # Deleting rows with pickup time less than dropoff time
        index_name = df_concat[df_concat['trip_duration']<0].index
        df_concat.drop(index_name,inplace=True)
        
        return df_concat
    
    
    def loc_list(self):
        
        dict = {}
        for i in range(self.df_loc.shape[0]):
            dict[self.df_loc['Zone'][i]] = self.df_loc['LocationID'][i]

        loc_list = [(k, v) for k, v in dict.items()] 
        return loc_list
    
    def taxi_plot(self, df,stat,taxi,field,start,end,date,size):
        """Method to generate the plots. It is called from the taxi_viz method"""
        
        x_axis_labels = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'] # labels for x-axis
        y_axis_labels = ['Mon','Tue','Wed','Thur','Fri','Sat','Sun'] # labels for y-axis

        x1 = df.groupby(['hour','day']).agg(value = (field,stat),).reset_index()
        x1 = x1.pivot('day', 'hour', "value")
        y1 = df.groupby(['trip_month','taxi_type']).agg(value = (field,stat),).reset_index() 

        y = size*100
        print('Records from: ', pd.to_datetime(date))
        print('Records in use: ', '{:,.2f} %'.format(y))
        print('Number of Trips: ', f'{df[field].count():,}')
        x = df['uc_mile'].median()
        print('Expected Unit cost per Mile: ', '${:,.2f}'.format(x)) 



        fig = plt.figure(figsize=(15, 12))
        a = plt.subplot2grid((3, 3), (0, 0), colspan=2)
        a = sns.barplot(x='trip_month', y="value", data=y1, hue='taxi_type',palette="Paired")
        a.set(xlabel='Month', ylabel=field, xticklabels=x_axis_labels)
        a.legend(loc='outside')
        b = plt.subplot2grid((3, 3), (1, 0), colspan=3)
        b = sns.heatmap(x1, annot=True,linewidths=.5, yticklabels=y_axis_labels, cmap="YlOrBr") 
        c = plt.subplot2grid((3, 3), (0, 2), rowspan=1)
        c = sns.violinplot(x=field,palette="Paired", data= df)     

        if field == 'trip_duration':    
            a.set_ylabel('Trip_duration (mins)')
            a.set_xlabel('')
            a.set_title('Monthly '+stat+ ' '+ field +' for '+ taxi + ' taxi '  )
            b.set_title('Daily Heatmap for '+stat+ ' ' + field + ' for ' + taxi +  ' taxi ')
            c.set_title('Distribution for '+ field + ' for ' + taxi + ' taxi ')

        elif field == 'total_amount':
            a.set_ylabel('Total amount (dollars)')
            a.set_xlabel('')
            a.set_title('Monthly '+stat+ ' '+ field +' for '+ taxi + ' taxi '  )
            b.set_title('Daily Heatmap for '+stat+ ' ' + field + ' for ' + taxi +  ' taxi ')
            c.set_title('Distribution for '+ field + ' for ' + taxi + ' taxi ')

        elif field == 'tip_amount':
            a.set_ylabel('Tip amount (dollars)')
            a.set_xlabel('')
            a.set_title('Monthly '+stat+ ' '+ field +' for '+ taxi + ' taxi '  )
            b.set_title('Daily Heatmap for '+stat+ ' ' + field + ' for ' + taxi +  ' taxi ')
            c.set_title('Distribution for '+ field + ' for ' + taxi + ' taxi ')

        elif field == 'trip_distance':
            a.set_ylabel('Trip distance (Miles)')
            a.set_xlabel('')
            a.set_title('Monthly '+stat+ ' '+ field +' for '+ taxi + ' taxi '  )
            b.set_title('Daily Heatmap for '+stat+ ' ' + field + ' for ' + taxi +  ' taxi ')
            c.set_title('Distribution for '+ field + ' for ' + taxi + ' taxi ')


        fig.suptitle('Visualization Dashboard  from ' + self.df_loc['Zone'][self.df_loc['LocationID']==start].any() + \
                                 ' to ' + self.df_loc['Zone'][self.df_loc['LocationID']==end].any() + ' Zone', fontsize=16)
       

        plt.show()
        
        
    def taxi_viz(self,start, end,stat,field,taxi,borough,month,size,date,df,df_zone):
    
        '''Function to create plot base on selected criteria'''
        
        dict = {}
        df_zone = df_zone.reset_index()
        for i in range(df_zone.shape[0]):
            dict[df_zone['Zone'][i]] = df_zone['LocationID'][i]
        dict['ALL'] = 265
        df_zone = df_zone[df_zone['Borough'].isin(list(borough))]
        
        #loc_list =  loc_list()


        df = pd.DataFrame(df.loc[(df['pulocationid'].isin(dict.values())) & (df['dolocationid'].isin(dict.values()))\
                                & (df['month_name'].isin(month)) & (df['tpep_pickup_datetime'] >= pd.to_datetime(date))])

        df = df.sample(frac=size)
        print(size)
        if (start ==265  and end == 265 ) and taxi=='All':

            NYTaxiViz.taxi_plot(self,df,stat,taxi,field,start,end,date,size)

        elif (start==265  and end ==265) and taxi=='green':
            df_g = pd.DataFrame(df.loc[(df.taxi_type=='green')])
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:       

                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size)

        elif (start==265  and end ==265) and taxi=='yellow':
            df_g = pd.DataFrame(df.loc[(df.taxi_type=='yellow')])
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:       

                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size)

        elif start!=265  and end ==265 and taxi =='All':
            df_g = pd.DataFrame(df.loc[(df.pulocationid==int(start))])
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:       

                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size)



        elif (start!=265  and end ==265) and taxi=='green':
            df_g = pd.DataFrame(df.loc[(df.pulocationid==int(start)) & (df.taxi_type=='green')])
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:       

                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size)

        elif (start!=265  and end ==265) and taxi=='yellow':
            df_g = pd.DataFrame(df.loc[(df.pulocationid==int(start)) & (df.taxi_type=='yellow')])
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:       

                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size)

        elif not (start ==265  and end == 265 ) and taxi=='All':



            df_g = pd.DataFrame(df.loc[(df.pulocationid==int(start)) & (df.dolocationid==int(end))] )
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:       

                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size)

        elif not (start ==265  and end == 265 ) and taxi=='green':

            df_g = pd.DataFrame(df.loc[(df.pulocationid==int(start)) & (df.dolocationid==int(end)) \
                               & (df.taxi_type=='green')])
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:
                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size) 

        elif not (start ==265  and end == 265 ) and taxi=='yellow':

            df_g = pd.DataFrame(df.loc[(df.pulocationid==int(start)) & (df.dolocationid==int(end)) \
                               & (df.taxi_type=='yellow')])
            if df_g.shape[0] == 0:
                print('No record to display for this route')
            else:
                NYTaxiViz.taxi_plot(df_g,stat,taxi,field,start,end,date,size)
        
        
    