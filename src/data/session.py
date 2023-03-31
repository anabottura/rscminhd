import pandas as pd
import numpy as np
import os

class Session():
    def __init__(self, datapath, date_time, animal):
        self.dpath = datapath
        self.date_time = date_time
        self.subject = animal
        # self.img_data = pd.DataFrame()
        # self.ho_data = pd.DataFrame()
        # self.img_time_data = pd.DataFrame()

    def load_all_data(self):
        """Load all the data"""

        imgC_fname = self.subject+'_'+self.date_time[-8:]+'_C.csv'
        imgC_path = os.path.join(self.dpath,'processed',self.subject,self.date_time,imgC_fname)
        imgS_fname = self.subject+'_'+self.date_time[-8:]+'_S.csv'
        imgS_path = os.path.join(self.dpath,'processed',self.subject,self.date_time,imgS_fname)
        if os.path.exists(imgS_path):
             s = pd.read_csv(imgS_path, index_col=0)
        else:
            s=pd.DataFrame()
        if os.path.exists(imgC_path):
            c = pd.read_csv(imgC_path, index_col=0)
        else:
            c=pd.DataFrame()
        img_df = pd.concat([c,s.loc[:,'S']], axis=1)
        self.img_data = img_df
        # print(img_data.isna().sum()) # check for nan values

        # load data from head orientation
        head_orient_fname = 'headOrientation.csv'
        self.ho_data = pd.read_csv(os.path.join(self.dpath,'raw',self.subject,self.date_time, 'Miniscope',head_orient_fname))
        self.ho_data['frame'] = self.ho_data.index
        # print(head_orient_data.isna().sum()) # check for nan values

        # load data from miniscope timestamp
        timestamp_fname = 'timeStamps.csv'
        self.img_time_data = pd.read_csv(os.path.join(self.dpath,'raw',self.subject,self.date_time, 'Miniscope',timestamp_fname))
        # print(img_time_data.isna().sum()) # check for nan values
    
    def calculate_dF_F(self):
        group_by_unit = self.img_data.groupby('unit_id')
        df_units = []
        
        for name, unit in group_by_unit:
            dFF = self._to_dF_F(unit)
            dFF.name = name
            df_units.append(dFF)
        
        self.img_data['df/f'] = pd.concat(df_units)
    
    def normalise_minmax(self):
        group_by_unit = self.img_data.groupby('unit_id')
        normalised_c = []
        
        for name, unit in group_by_unit:
            min_C = unit['C'].min()
            max_C = unit['C'].max()
            min_max_norm = (unit['C']- min_C)/(max_C-min_C)
            normalised_c.append(min_max_norm)
            
        self.img_data['norm_C'] = pd.concat(normalised_c)
    
    
    def _to_dF_F(self,df):
        """_summary_

        :param df: _description_
        :type df: _type_
        :return: _description_
        :rtype: _type_
        """
        percentile10 = np.percentile(df['C'], 10)
        percentile70 = np.percentile(df['C'], 70)
        f0 = np.median(df[(df['C'] >= percentile10) & (df['C'] <= percentile70)]['C'])

        # Correct fluorescence time series for baseline
        if f0 == 0.0:
            dF = df['C']
        else:
            dF = (df['C'] - f0) / f0

        # Shift values so that minimum value is zero
        dF -= dF.min()
        
        return dF
    

# load data into data frames # TODO: access files directly from ftp server

# from ftplib import FTP



# if __name__ == '__main__':