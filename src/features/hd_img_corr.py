import sys
import os
sys.path.append("/Users/anacarolinabotturabarros/PycharmProjects/RSCMINHD/src/")
from data.session import Session
import features.features_utils as utils
import visualisation.plot_data as myplot
import pandas as pd

## Load Data
print("Loading Data...")
project_dir = "/Users/anacarolinabotturabarros/PycharmProjects/RSCMINHD/data"
animal = 'cohoHDC1_mG1'
session = "2023_03_10/15_12_54"

my_session = Session(project_dir,session,animal)
my_session.load_all_data()
my_session.calculate_dF_F()
my_session.normalise_minmax()

## Process head orientation data
print("Processing head orientation")
utils.get_euler_coords(my_session)
utils.bin_ho(my_session,['yaw_z'],[6]) # bins ho data in 6 degree bins

## Calculating the direction tunning of the different ROIs
print("Getting Direction tunning")
intervals = utils.get_intervals(my_session.ho_data, 'binned_yaw_z') # frame intervals for each bin
dir_tunning = utils.get_dir_tunning(my_session.img_data,intervals) # direction tunning based on auc

spath = os.path.join(project_dir,'processed', animal, session)
print("Saving direction tunning to {}".format(spath))
if not os.path.exists(spath):
    os.makedirs(spath)
dir_tunning.to_csv(os.path.join(spath,'auc_dir_tunning.csv'))

spath = os.path.join(project_dir[:-4],"reports/figures", animal, session)
print("Plotting direction tunning for all units and saving to {}".format(spath))
g = myplot.plot_dir_tunning(dir_tunning)
if not os.path.exists(spath):
    os.makedirs(spath)
g.savefig(os.path.join(spath,"all_ROIs.png"))

## Checking direction tunning on first and second halves
print("Processing direction tunning on first and second halves")
half = int(my_session.ho_data.shape[0]/2)
intervals_1of2 = utils.get_intervals(my_session.ho_data.loc[:half-1,:],'binned_yaw_z')
intervals_2of2 = utils.get_intervals(my_session.ho_data.loc[half:,:],'binned_yaw_z')

dir_tunning_1of2 = utils.get_dir_tunning(
    my_session.img_data[my_session.img_data.frame < half],intervals_1of2)
dir_tunning_2of2 = utils.get_dir_tunning(
    my_session.img_data[my_session.img_data.frame >= half],intervals_2of2)

dir_tunning_1of2.loc[:,'half'] = 1
dir_tunning_2of2.loc[:,'half'] = 2
df = pd.concat([dir_tunning_1of2, dir_tunning_2of2])

spath = os.path.join(project_dir[:-4],"reports/figures", animal, session)
print("Plotting direction tunning for all units split in halves and saving to {}".format(spath))
g = myplot.plot_dir_tunning(df, hue='half', id_vars = ['unit_id', 'half'])
if not os.path.exists(spath):
    os.makedirs(spath)
g.savefig(os.path.join(spath,"all_ROIs_sessionHalves.png"))