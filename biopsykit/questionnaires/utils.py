from typing import Optional, Union, Sequence, Tuple, Callable

import numpy as np
import pandas as pd


def find_cols(df: pd.DataFrame, starts_with: Optional[str] = None, ends_with: Optional[str] = None,
              contains: Optional[str] = None, fill_zeros: Optional[bool] = True) \
        -> Tuple[pd.DataFrame, Sequence[str]]:
    df_filt = df.copy()

    if starts_with:
        df_filt = df_filt.filter(regex="^" + starts_with)
    if ends_with:
        df_filt = df_filt.filter(regex=ends_with + "$")
    if contains:
        df_filt = df_filt.filter(regex=contains)

    cols = df_filt.columns

    if fill_zeros:
        cols = df_filt.columns
        df_filt = fill_col_leading_zeros(df_filt)
    df_filt = df_filt.reindex(sorted(df_filt.columns), axis='columns')

    if not fill_zeros:
        cols = df_filt.columns

    return df_filt, cols


def fill_col_leading_zeros(df: pd.DataFrame, inplace: Optional[bool] = False) -> Union[pd.DataFrame, None]:
    import re

    if not inplace:
        df = df.copy()

    df.columns = [re.sub(r'(\d+)$', lambda m: m.group(1).zfill(2), c) for c in df.columns]

    if not inplace:
        return df


def int_from_str_col(data: pd.DataFrame, name: str, regex: str, func: Optional[Callable] = None) -> Union[
    pd.Series, pd.DataFrame]:
    """
    Extracts an integer from a column containing string values.

    Parameters
    ----------
    data
    name
    regex
    func : function to apply to the extracted integers, such as a lambda function to increment all integers by 1

    Returns
    -------

    """
    if name in data.index.names:
        idx_names = data.index.names
        data = data.reset_index()
        idx_col = data[name].str.extract(regex).astype(int)[0]
        if func is not None:
            idx_col = func(idx_col)
        data[name] = idx_col
        data = data.set_index(idx_names)
        return data
    elif name in data.columns:
        idx_col = data[name].str.extract(regex).astype(int)[0]
        if func is not None:
            idx_col = func(idx_col)
        return idx_col
    else:
        raise ValueError("Name `{}` neither in index nor in columns!".format(name))


#  TODO clean up util functions
def camel_to_snake(name: str):
    """
    Converts string in 'camelCase' to 'snake_case'.

    Parameters
    ----------
    name

    Returns
    -------

    """
    import re
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def replace_missing_data(data: pd.DataFrame, target_col: str, source_col: str, dropna: Optional[bool] = False):
    """
    Replaces missing data in one column by data from another column.

    Parameters
    ----------
    data
    target_col
    source_col
    dropna

    Returns
    -------

    """
    data[target_col] = data[target_col].fillna(data[source_col])
    if dropna:
        return data.dropna(subset=[target_col])
    else:
        return data


def convert_nan(
        data: Union[pd.DataFrame, pd.Series],
        inplace: Optional[bool] = False
) -> Union[pd.DataFrame, pd.Series, None]:
    if inplace:
        data.replace([-99.0, -77.0, -66.0, "-99", "-77", "-66"], np.nan, inplace=True)
    else:
        return data.replace([-99.0, -77.0, -66.0, "-99", "-77", "-66"], np.nan, inplace=False)


def to_idx(col_idxs: Union[np.array, Sequence[int]]) -> np.array:
    return np.array(col_idxs) - 1


def invert(data: Union[pd.DataFrame, pd.Series], score_range: Sequence[int],
           cols: Optional[Union[Sequence[int], Sequence[str]]] = None,
           inplace: Optional[bool] = False) -> Union[pd.DataFrame, pd.Series, None]:
    if inplace:
        if isinstance(data, pd.DataFrame):
            if cols is not None:
                if isinstance(cols[0], str):
                    data.loc[:, cols] = score_range[1] - data.loc[:, cols] + score_range[0]
                else:
                    data.iloc[:, cols] = score_range[1] - data.iloc[:, cols] + score_range[0]
            else:
                data.iloc[:, :] = score_range[1] - data.iloc[:, :] + score_range[0]
        elif isinstance(data, pd.Series):
            data.iloc[:] = score_range[1] - data.iloc[:] + score_range[0]
        else:
            raise ValueError("Only pd.DataFrame and pd.Series supported!")
    else:
        return score_range[1] - data + score_range[0]


def convert_scale(data: Union[pd.DataFrame, pd.Series], offset: int,
                  cols: Optional[Union[pd.DataFrame, pd.Series]] = None,
                  inplace: Optional[bool] = False) -> Union[pd.DataFrame, pd.Series, None]:
    if inplace:
        if isinstance(data, pd.DataFrame):
            if cols is None:
                data.iloc[:, :] = data.iloc[:, :] + offset
            else:
                if isinstance(cols[0], int):
                    data.iloc[:, cols] = data.iloc[:, cols] + offset
                elif isinstance(cols[0], str):
                    data.loc[:, cols] = data.loc[:, cols] + offset
        elif isinstance(data, pd.Series):
            data.iloc[:] = data.iloc[:] + offset
        else:
            raise ValueError("Only pd.DataFrame and pd.Series supported!")
    else:
        data = data.copy()
        if cols is not None:
            data[cols] = data[cols] + offset
            return data
        else:
            return data + offset


def crop_scale(data: Union[pd.DataFrame, pd.Series], score_scale: Sequence[int], inplace: Optional[bool] = True,
               set_nan: Optional[bool] = True) -> Union[pd.DataFrame, pd.Series, None]:
    if set_nan:
        if inplace:
            data.mask((data < score_scale[0]) | (data > score_scale[1]), inplace=True)
        else:
            return data.mask((data < score_scale[0]) | (data > score_scale[1]))
    else:
        if inplace:
            data.mask((data < score_scale[0]), other=score_scale[0], inplace=True)
            data.mask((data > score_scale[1]), other=score_scale[1], inplace=True)
        else:
            tmp = data.mask((data < score_scale[0]), other=score_scale[0])
            return tmp.mask((tmp > score_scale[1]), other=score_scale[1])


def bin_scale(data: Union[pd.DataFrame, pd.Series], bins: Sequence[float], col: Optional[Union[int, str]] = None,
              last_max: Optional[bool] = False, inplace: Optional[bool] = False, right: Optional[bool] = True) \
        -> Union[pd.Series, None]:
    if last_max:
        if isinstance(col, int):
            max_val = data.iloc[:, col].max()
        elif isinstance(col, str):
            max_val = data[col].max()
        else:
            max_val = data.max()

        if max_val > max(bins):
            bins = bins + [max_val + 1]

    if isinstance(data, pd.Series):
        c = pd.cut(data.iloc[:], bins=bins, labels=False, right=right)
        if inplace:
            data.iloc[:] = c
        else:
            return c

    elif isinstance(data, pd.DataFrame):
        if col is None:
            if len(data.columns) > 1:
                raise ValueError("Column must be specified when passing dataframe!")
            else:
                c = pd.cut(data.iloc[:, 0], bins=bins, labels=False, right=right)
                if inplace:
                    data.iloc[:, 0] = c
                else:
                    return c

        if isinstance(col, int):
            c = pd.cut(data.iloc[:, col], bins=bins, labels=False, right=right)
            if inplace:
                data.iloc[:, col] = c
            else:
                return c

        if isinstance(col, str):
            c = pd.cut(data.loc[:, col], bins=bins, labels=False, right=right)
            if inplace:
                data.loc[:, col] = c
            else:
                return c


def check_score_range(data: pd.DataFrame, score_range: Sequence[int]) -> bool:
    return np.nanmin(data) >= score_range[0] and np.nanmax(data) <= score_range[1]


def _check_score_range_exception(data: pd.DataFrame, score_range: Sequence[int]) -> None:
    if not check_score_range(data, score_range):
        raise ValueError(
            "This implementation expects values in the range {}! "
            "Please consider converting to the correct range using `biopsykit.utils.convert_scale`.".format(
                score_range))
