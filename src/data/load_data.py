import pandas as pd
import numpy as np
import os

class HeadOrientation():
    def __init__(self, filepath, filename='headOrientation.csv'):
        self.fpath = filepath
        self.fname = filename
        self.data = pd.DataFrame()
        
    def load(self):
        self.data =  pd.read_csv(os.path.join(self.fpath, self.fname))
        
    

# load data into data frames # TODO: access files directly from ftp server

# from ftplib import FTP

# load data from minian

def load_all_data(subject,session,project_dir):

    img_fname = subject+'_'+session[-8:]+'_C.csv'
    img_data = pd.read_csv(os.path.join(project_dir,'data/processed',subject, session,img_fname), index_col=0)
    print(img_data.isna().sum()) # check for nan values

    # load data from head orientation
    head_orient_fname = 'headOrientation.csv'
    head_orient_data = pd.read_csv(os.path.join(project_dir,'data/raw',subject, session, 'Miniscope',head_orient_fname))
    print(head_orient_data.isna().sum()) # check for nan values

    # load data from miniscope timestamp
    timestamp_fname = 'timeStamps.csv'
    img_time_data = pd.read_csv(os.path.join(project_dir,'data/raw',subject, session, 'Miniscope',timestamp_fname))
    print(img_time_data.isna().sum()) # check for nan values
    
    return {'img_data': img_data, 'head_data': head_orient_data, 'img_time_stamps': img_time_data}

# if __name__ == '__main__':

def to_dF_F(df):
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