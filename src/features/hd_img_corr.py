import itertools
from operator import itemgetter

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