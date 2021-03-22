from typing import Union, Tuple, Sequence, Optional, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from biopsykit.utils.functions import se

_PVALUE_THRESHOLDS = [[1e-3, "***"], [1e-2, "**"], [0.05, "*"]]


def lineplot(data: pd.DataFrame, **kwargs) -> Union[None, Tuple[plt.Figure, plt.Axes]]:
    markers = None
    style = kwargs.get('style', None)
    ax: plt.Axes = kwargs.get('ax', None)
    hue = kwargs.get('hue')
    x = kwargs.get('x')
    y = kwargs.get('y')
    order = kwargs.get('order')
    legend_fontsize = kwargs.get('legend_fontsize', None)

    if style is not None:
        markers = ['o'] * len(data.index.get_level_values(style).unique())

    fig = None
    if ax is None:
        fig, ax = plt.subplots()

    kwargs.update(
        {'dashes': False, 'err_style': 'bars', 'markers': markers, 'ci': 68, 'ax': ax, 'err_kws': {'capsize': 5}}
    )

    data = data.reset_index()
    grouped = {key: val for key, val in data.groupby(hue)}

    if order is not None:
        # reorder group dictionary
        grouped = {key: grouped[key] for key in order}

    x_vals = np.arange(0, len(data[x].unique()))
    for i, (key, df) in enumerate(grouped.items()):
        m_se = df.groupby([x, hue]).agg([np.mean, se])[y]
        err_kws = kwargs.get('err_kws')
        marker = markers[i] if markers else None
        ax.errorbar(x=x_vals + 0.05 * i, y=m_se['mean'], yerr=m_se['se'].values, marker=marker, label=key, **err_kws)

    ylabel = kwargs.get('ylabel', data[y].name)
    xlabel = kwargs.get('xlabel', data[x].name)
    xticklabels = kwargs.get('xticklabels', data[x].unique())
    ylim = kwargs.get('ylim', None)

    ax.set_xticks(x_vals)
    ax.set_xticklabels(xticklabels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(ylim)

    # get handles
    handles, labels = ax.get_legend_handles_labels()
    # remove the errorbars
    handles = [h[0] for h in handles]
    # use them in the legend
    ax.legend(handles, labels, loc='upper left', numpoints=1, fontsize=legend_fontsize)

    if fig is not None:
        return fig, ax


def stacked_barchart(data: pd.DataFrame, **kwargs) -> Union[None, Tuple[plt.Figure, plt.Axes]]:
    fig = None
    ax: plt.Axes = kwargs.get('ax', None)
    if ax is None:
        fig, ax = plt.subplots()

    ylabel = kwargs.get('ylabel', None)
    order = kwargs.get('order', None)
    if order:
        data = data.reindex(order)

    ax = data.plot(kind='bar', stacked=True, ax=ax, rot=0)
    ax.legend().set_title(None)
    if ylabel:
        ax.set_ylabel(ylabel)

    return fig, ax


def feature_boxplot(data: pd.DataFrame, x: str, y: str, stats_kwargs: Optional[Dict] = None, **kwargs):
    from statannot import add_stat_annotation
    fig = None
    ax: plt.Axes = kwargs.pop('ax', None)
    if ax is None:
        fig, ax = plt.subplots()

    if stats_kwargs is None:
        stats_kwargs = {}

    ylabel = kwargs.pop('ylabel', None)

    box_pairs = stats_kwargs.get('box_pairs', {})
    boxplot_pvals = stats_kwargs.get('pvalues', {})

    if len(stats_kwargs) > 0:
        stats_kwargs['comparisons_correction'] = stats_kwargs.get('comparisons_correction', None)
        stats_kwargs['test'] = stats_kwargs.get('test', None)

    if len(boxplot_pvals) > 0:
        stats_kwargs['perform_stat_test'] = False

    stats_kwargs['pvalue_thresholds'] = _PVALUE_THRESHOLDS

    sns.boxplot(data=data.reset_index(), x=x, y=y, ax=ax, **kwargs)
    if len(box_pairs) > 0:
        stats_kwargs['hue_order'] = kwargs.get('hue_order', None)
        stats_kwargs['order'] = kwargs.get('order', None)
        stats_kwargs['hue'] = kwargs.get('hue', None)
        add_stat_annotation(data=data.reset_index(), ax=ax, x=x, y=y, **stats_kwargs)

    if ylabel is not None:
        ax.set_ylabel(ylabel)

    if fig is not None:
        return fig, ax


def multi_feature_boxplot(data: pd.DataFrame, x: str, y: str, hue: str,
                          features: Optional[Sequence[str]] = None, filter_features: Optional[bool] = True,
                          xticklabels: Optional[Dict[str, Sequence[str]]] = None,
                          ylabels: Optional[Dict[str, str]] = None,
                          stats_kwargs: Optional[Dict] = None,
                          **kwargs) -> Union[None, Tuple[plt.Figure, Sequence[plt.Axes]]]:
    """

    Parameters
    ----------
    data
    x
    y
    hue
    features
    filter_features : bool, optional
        ``True`` to filter features by name, ``False`` to match exact feature names. Default: ``True``
    xticklabels
    ylabels
    stats_kwargs
    kwargs

    Returns
    -------

    """
    from statannot import add_stat_annotation

    axs: Sequence[plt.Axes] = kwargs.pop('axs', kwargs.pop('ax', None))

    legend = kwargs.pop('legend', True)
    legend_fontsize = kwargs.pop('legend_fontsize', None)
    rect = kwargs.pop('rect', (0, 0, 0.825, 1.0))

    hue_order = kwargs.pop('hue_order', None)
    xlabels = kwargs.pop('xlabels', {})

    if ylabels is None:
        ylabels = {}
    if xticklabels is None:
        xticklabels = {}

    if axs is None:
        fig, axs = plt.subplots(figsize=(15, 5), ncols=len(features))
    else:
        fig = axs[0].get_figure()

    if stats_kwargs is None:
        stats_kwargs = {}

    dict_box_pairs = stats_kwargs.pop('box_pairs', None)
    dict_pvals = stats_kwargs.pop('pvalues', None)

    h, l = None, None
    for ax, feature in zip(axs, features):
        if filter_features:
            data_plot = data.unstack().filter(like=feature).stack()
        else:
            data_plot = data.unstack().loc[:, pd.IndexSlice[:, feature]].stack()
        sns.boxplot(data=data_plot.reset_index(), x=x, y=y, hue=hue, hue_order=hue_order, ax=ax, **kwargs)

        if len(stats_kwargs) > 0:
            stats_kwargs['comparisons_correction'] = stats_kwargs.get('comparisons_correction', None)
            stats_kwargs['test'] = stats_kwargs.get('test', None)

        if dict_box_pairs is not None:
            # filter box pairs by feature
            stats_kwargs['box_pairs'] = [dict_box_pairs[x] for x in dict_box_pairs if feature in x]
            # flatten list
            stats_kwargs['box_pairs'] = [x for pairs in stats_kwargs['box_pairs'] for x in pairs]

        if dict_pvals is not None:
            # filter pvals by feature
            stats_kwargs['pvalues'] = [dict_pvals[x] for x in dict_pvals if feature in x]
            # flatten list
            stats_kwargs['pvalues'] = [x for pairs in stats_kwargs['pvalues'] for x in pairs]
            stats_kwargs['perform_stat_test'] = False

        stats_kwargs['pvalue_thresholds'] = _PVALUE_THRESHOLDS

        if 'box_pairs' in stats_kwargs and len(stats_kwargs['box_pairs']) > 0:
            add_stat_annotation(ax=ax, data=data_plot.reset_index(), x=x, y=y, hue=hue, hue_order=hue_order,
                                **stats_kwargs)

        if feature in ylabels:
            ax.set_ylabel(ylabels[feature])

        if feature in xticklabels:
            if feature in xlabels:
                ax.set_xlabel(xlabels[feature])
            else:
                ax.set_xlabel(None)
            xt = xticklabels[feature]
            if isinstance(xt, str):
                xt = [xt]
            ax.set_xticklabels(xt)
        h, l = ax.get_legend_handles_labels()
        ax.legend().remove()

    if legend:
        fig.legend(h, l, loc='upper right', bbox_to_anchor=(1.0, 1.0), fontsize=legend_fontsize)
        fig.tight_layout(pad=0.5, rect=rect)

    return fig, axs
