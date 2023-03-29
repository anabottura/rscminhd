import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
# plot all units - lineplot
# plot C
def plot_ROI_activity(img_data, roi, variable='C'):
    
    plt.figure(figsize=(10,2))
    unit_data = img_data[img_data['unit_id']==img_data['unit_id'].unique()[roi]]
    
    return sns.lineplot(data=unit_data, x='frame',y=variable)


# # plot occurances of bins
# fig, axs = plt.subplots(1,4, sharey=True, figsize=(20,5))
# head_qua_vars = head_data.columns[1:]

# for ax,var in zip(axs,head_qua_vars):
#     p = sns.countplot(x=head_data['binned_'+var], ax=ax)
#     ax.set_xticklabels(head_data['binned_qx'].cat.categories, rotation=45, ha='right')
#     ax.set(ylabel=None)

# axs[0].set_ylabel('Count')

def plot_dir_tunning(dir_tunning, unit=None, hue = None, ncols=10, id_vars = 'unit_id', radial=True):
    new_melt = pd.melt(dir_tunning, id_vars=id_vars)
    if unit is not None:
        units = [unit]
    else:
        units = dir_tunning.unit_id.unique()
    num_units = len(units)
    if radial:
        new_melt.loc[:,'degree'] = pd.IntervalIndex(new_melt['variable']).left*np.pi/180
        g = sns.FacetGrid(new_melt[new_melt.unit_id.isin(units)],
                          hue=hue,
                          col='unit_id',
                          col_wrap=ncols,
                          subplot_kws=dict(projection='polar'),
                          height=4.5,
                          sharex=False, 
                          sharey=False, 
                          despine=False)
        g.map(sns.lineplot,"degree","value")
        # g.set_xticklabels(rotation=45, ha='right')
        # g.set_axis_labels(x_var='Direction qx', y_var='Direction Tuning')
        # g.fig.tight_layout()
        g.fig.set_size_inches(20,20)
        g.fig.subplots_adjust(wspace=0.5)
        plt.show()
        return g
    else:
        nrows = (num_units + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(15, 5*nrows))
        for i, unit in enumerate(units):
            row = i // ncols
            col = i % ncols
            plot_unit = new_melt[new_melt.unit_id == unit]
            ax = sns.lineplot(data=plot_unit, x='variable', y='value', ax=axes[row, col])
            ax.set_xticklabels(plot_unit.variable.astype(str), rotation=45, ha='right')
            ax.set(ylabel='Direction Tuning', xlabel='Direction qx')
            ax.set_title(f"Unit {unit}")
        fig.tight_layout()
        plt.show()
        return ax