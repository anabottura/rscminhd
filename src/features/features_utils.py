import itertools
from operator import itemgetter
# from src.data.load_data import Session
import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation

def get_euler_coords(session):
    """_summary_

    :param session: _description_
    :type session: _type_
    """
        
    quat = np.array([session.ho_data['qx'], session.ho_data['qy'], session.ho_data['qz'], session.ho_data['qw']])
    R = Rotation.from_quat(quat.T)
    euler_data = R.as_euler('xyz', degrees=True)
    euler_df = pd.DataFrame(euler_data)
    session.ho_data['roll_x'] = euler_df.loc[:,0]
    session.ho_data['pitch_y'] = euler_df.loc[:,1]
    session.ho_data['yaw_z'] = euler_df.loc[:,2]
    # session.ho_data = pd.concat([session.ho_data, pd.DataFrame(euler_data, columns=['roll_x', 'pitch_y', 'yaw_z'])], axis=1)

def bin_ho(session, variables, bin_size,start=[-180],end=[180]):
    """Adds binned_variable/s column/s to the head orientation data in session
    which classifies the values of variable/s in bins defined by bin_size, start and end.

    :param session: Object created with class Session
    :type session: Session
    :param variables: List of names of columns in the head orientation dataset
    :type variables: list
    :param bin_size: List of sizes for bins for each variable
    :type bin_size: list
    :param start: List of expected minimum value for columns in head orientation data, defaults to -180
    :type start: list, optional
    :param end: List of expected maximum value for columns in head orientation data, defaults to 180
    :type end: list, optional
    """
    
    for i,v in enumerate(variables):
        bins = int((end[i]-start[i])/bin_size[i])+1
        session.ho_data['binned_'+v] = pd.cut(session.ho_data[v],np.linspace(start[i],end[i],bins))

def find_intervals(data):
    ranges =[]    
    for key, group in itertools.groupby(enumerate(data), lambda x:x[0]-x[1]):
        group = list(map(itemgetter(1), group))
        if len(group) > 1:
            ranges.append(pd.Interval(group[0], group[-1],closed='both'))
        # else:
            # ranges.append(group[0])
    return ranges

def get_intervals(head_data, variable):
    """get frame intervals where angles are within the specified bin

    :param head_data: head orientation data
    :type head_data: pd.DataFrame
    :param variable: name of the variable in head_data to base intervals
    :type variable: str
    :return: intervals of frames with angles between specific groups
    :rtype: dict
    """
    grouped = head_data[[variable,'frame']].groupby(variable)
    intervals = {}
    for name, group in grouped:
        intervals[name] = find_intervals(group['frame'])
    return intervals

def calculate_auc(unit_data, intervals):
    # calculate the area under the curve norm_C for each unit between intervals found and sum the area under the curve
    """_summary_

    :param unit_data: _description_
    :type unit_data: _type_
    :param intervals: _description_
    :type intervals: _type_
    :return: _description_
    :rtype: _type_
    """
    
    all_auc = pd.DataFrame()

    for key, value in intervals.items():
        auc_dict = {}
        for name, unit in unit_data:
            auc=0
            for i in value:
                img_interval = unit[unit['frame'].between(i.left, i.right)]
                auc += np.trapz(img_interval['norm_C'],img_interval['frame'])
            auc_dict[name] = auc
        all_auc[key] = pd.Series(auc_dict)
    
    return all_auc

def calculate_int_length(intervals):
    """Calculate the length of the intervals for a dictionary of intervals and return the total sum of the lengths for a range of angles.

    :param intervals: Dictionary of intervals
    :type intervals: dict
    :return: dictionary of total sum of lengths
    :rtype: dict
    """
    interval_lengths = {}
    for itv in intervals.keys():
        int_idx = pd.IntervalIndex(intervals[itv])
        total_time = np.sum(int_idx.right - int_idx.left +1)
        interval_lengths[itv] = total_time
    return interval_lengths

def get_dir_tunning(img_data,intervals):
    """_summary_

    :param session: _description_
    :type session: _type_
    :param intervals: _description_
    :type intervals: _type_
    :return: _description_
    :rtype: _type_
    """
    # calculate the area under the curve norm_C for each unit between intervals found
    print("calculating area under the curve for intervals...")
    all_auc = calculate_auc(img_data.groupby('unit_id'), intervals)
    print("Done!")
    print("Calculating interval lengths...")
    interval_lengths = calculate_int_length(intervals)
    interval_lengths = pd.Series(interval_lengths, name='interval_lengths')
    print("Done!")
    dir_tuning = all_auc.T.div(interval_lengths, axis=0).T # normalise it by diving by the total amount of time spent looking at that direction
    dir_tuning['unit_id']=dir_tuning.index
    return dir_tuning