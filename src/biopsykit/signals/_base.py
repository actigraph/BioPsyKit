from typing import Optional, Union, Dict, Sequence

import pandas as pd
from biopsykit.utils.data_processing import split_data


class _BaseProcessor:
    def __init__(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        sampling_rate: Optional[float] = None,
        time_intervals: Optional[Union[pd.Series, Dict[str, Sequence[str]]]] = None,
        include_start: Optional[bool] = False,
    ):
        self.sampling_rate: float = sampling_rate
        """Sampling rate of recorded data."""

        if isinstance(data, dict):
            data_dict = data
        else:
            if time_intervals is not None:
                # split data into subphases if time_intervals are passed
                data_dict = split_data(
                    data=data,
                    time_intervals=time_intervals,
                    include_start=include_start,
                )
            else:
                data_dict = {"Data": data}

        self.data = data_dict
        """Dictionary with raw data, split into different phases.

        Each dataframe is expected to be a :class:`~pandas.DataFrame`.
        """

    @property
    def phases(self) -> Sequence[str]:
        """List of phases.

        Returns
        -------
        list
            phase names

        """
        return list(self.data.keys())
