"""Module for processing Respiration data."""
from typing import Optional, Union, Dict, Sequence

import neurokit2 as nk
import numpy as np
import pandas as pd
import scipy.signal as ss
from biopsykit.signals._base import _BaseProcessor
from biopsykit.utils.array_handling import sanitize_input_1d


class RspProcessor(_BaseProcessor):
    """Class for processing respiration data."""

    def __init__(
        self,
        data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
        sampling_rate: Optional[float] = None,
        time_intervals: Optional[Union[pd.Series, Dict[str, Sequence[str]]]] = None,
        include_start: Optional[bool] = False,
    ):
        super().__init__(
            data=data, sampling_rate=sampling_rate, time_intervals=time_intervals, include_start=include_start
        )

    @classmethod
    def rsp_compute_rate(cls, rsp_signal: pd.DataFrame, sampling_rate: Optional[float] = 256.0) -> float:
        """Compute respiration rate for given interval from respiration signal.

        Parameters
        ----------
        rsp_signal : pd.DataFrame
            raw respiration signal (1D). Can be a 'true' respiration signal (e.g. from bioimpedance or Radar)
            or an 'estimated' respiration signal (e.g. from ECG-derived respiration)
        sampling_rate : float, optional
            Sampling rate of recorded data


        Returns
        -------
        float
            Respiration rate during the given interval in bpm (breaths per minute)


        References
        ----------
        Schäfer, A., & Kratky, K. W. (2008). Estimation of Breathing Rate from Respiratory Sinus Arrhythmia:
        Comparison of Various Methods. *Annals of Biomedical Engineering*, 36(3), 476–485.
        https://doi.org/10.1007/s10439-007-9428-1


        Examples
        --------
        >>> from biopsykit.signals.ecg import EcgProcessor
        >>> # initialize EcgProcessor instance
        >>> ecg_processor = EcgProcessor(...)

        >>> # Extract respiration signal estimated from ECG using the 'peak_trough_diff' method
        >>> rsp_signal = ecg_processor.ecg_estimate_rsp(ecg_processor, key="Data", edr_type='peak_trough_diff')
        >>> # Compute respiration rate from respiration signal
        >>> rsp_rate = ecg_processor.rsp_compute_rate(rsp_signal)
        """

        # find peaks: minimal distance between peaks: 1 seconds
        rsp_signal = sanitize_input_1d(rsp_signal)
        edr_maxima = ss.find_peaks(rsp_signal, height=0, distance=sampling_rate)[0]
        edr_minima = ss.find_peaks(-1 * rsp_signal, height=0, distance=sampling_rate)[0]
        # threshold: 0.2 * Q3 (= 75th percentile)
        max_threshold = 0.2 * np.percentile(rsp_signal[edr_maxima], 75)
        # find all maxima that are above the threshold
        edr_maxima = edr_maxima[rsp_signal[edr_maxima] > max_threshold]

        # rearrange maxima into 2D array to that each row contains the start and end of one cycle
        rsp_cycles_start_end = np.vstack([edr_maxima[:-1], edr_maxima[1:]]).T

        # check for
        valid_resp_phases_mask = np.apply_along_axis(cls._check_contains_trough, 1, rsp_cycles_start_end, edr_minima)
        rsp_cycles_start_end = rsp_cycles_start_end[valid_resp_phases_mask]

        edr_signal_split: list = np.split(rsp_signal, rsp_cycles_start_end.flatten())[1::2]
        rsp_cycles_start_end = rsp_cycles_start_end.T
        rsp_peaks = rsp_cycles_start_end[0]
        rsp_troughs = np.array(list(map(lambda arr: np.argmin(arr), edr_signal_split))) + rsp_cycles_start_end[0]

        rsp_rate_peaks = cls._rsp_rate(rsp_peaks, int(sampling_rate), len(rsp_signal))
        rsp_rate_troughs = cls._rsp_rate(rsp_troughs, int(sampling_rate), len(rsp_signal))
        return np.concatenate([rsp_rate_peaks, rsp_rate_troughs]).mean()

    @classmethod
    def _check_contains_trough(cls, start_end: np.ndarray, minima: np.ndarray) -> bool:
        """
        Helper method to check whether exactly one minima is in the interval given by the array `start_end`: [start, end].

        Parameters
        ----------
        start_end : array_like
            array with start and end index
        minima : array_like
            array containing minima to be checked

        Returns
        -------
        bool
            True if exactly one minima is in the [start, end] interval, False otherwise
        """
        start, end = start_end
        return minima[(minima > start) & (minima < end)].shape[0] == 1

    @classmethod
    def _rsp_rate(cls, extrema: np.ndarray, sampling_rate: int, desired_length: int) -> np.array:
        """
        Computes the continuous respiration rate from extrema values.

        Parameters
        ----------
        extrema: array_like
            list of respiration extrema (peaks or troughs)
        sampling_rate : float
            Sampling rate of recorded data
        desired_length : int
            desired length of the output signal

        Returns
        -------
        array_like
            respiration rate array interpolated to desired length
        """
        rsp_rate_raw = (sampling_rate * 60) / np.ediff1d(extrema)
        # remove last sample
        x_old = extrema[:-1]
        x_new = np.linspace(x_old[0], x_old[-1], desired_length)
        return nk.signal_interpolate(x_old, rsp_rate_raw, x_new, method="linear")
