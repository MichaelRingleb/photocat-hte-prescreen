import math

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import least_squares


def find_nearest(array, values):
    """
    Find the indices of the nearest values in the array to a list of target values.

    Parameters:
        array (numpy.ndarray): The input array.
        values (numpy.ndarray or scalar): The target values.

    Returns:
        list: A list of indices of the nearest values in the array to the target values.

    Note:
        If the input array has more than one dimension, the function flattens the first dimension.
        The function uses the `numpy.searchsorted` function to find the indices of the target values in the array.
        The function then checks if the index is not the last index in the array and if the difference between the target value and the previous value in the array is less than the difference between the target value and the current value in the array. If both conditions are true, the index of the previous value is returned, otherwise the index of the current value is returned.
    """

    if array.ndim != 1:
        array_1d = array[:, 0]
    else:
        array_1d = array

    values = np.atleast_1d(values)
    hits = []

    for i in range(len(values)):
        idx = np.searchsorted(array_1d, values[i], side="left")
        if idx > 0 and (
            idx == len(array_1d)
            or math.fabs(values[i] - array_1d[idx - 1])
            < math.fabs(values[i] - array_1d[idx])
        ):
            hits.append(idx - 1)
        else:
            hits.append(idx)

    return hits


def poly(a, x):
    y = a[0] * x**0

    for i in range(1, len(a)):
        y += a[i] * x**i

    return y


def residual_generic(p, x, y, function):
    y_fit = function(p, x)
    res = y - y_fit

    return res


def pre_signal_fitting(data, start, end, order_poly, plotting=False, filename=None):
    """Pre-signal fitting for baseline correction"""

    idx = find_nearest(data, np.array([start, end]))
    x = data[:, 0][idx[0] : idx[1]]
    y = data[:, 1][idx[0] : idx[1]]

    p_guess = np.ones(order_poly + 1)
    p = least_squares(fun=residual_generic, x0=p_guess, args=(x, y, poly))
    p_solved = p.x

    y_baseline = poly(p_solved, data[:, 0])
    y_corrected = data[:, 1] - y_baseline

    if plotting:
        fig, ax = plt.subplots()
        ax.plot(x, y, ".", markersize=2.0)
        ax.plot(data[:, 0], y_baseline, linewidth=1.0)
        ax.plot(data[:, 0], y_corrected)
        if filename is not None:
            fig.savefig(filename, dpi=400)

    data_corr = np.c_[data[:, 0], y_corrected]

    return data_corr


def first_order_combined(p, t):
    return p[0] - (p[0] * np.exp(-p[1] * t))


def first_order_shift(p, t):
    """Function with value zero for t < p[2], first order for t > p[2]"""

    idx = find_nearest(t, p[2])[0]

    t_base = t[: idx + 1]
    t_feature = t[idx + 1 :]

    y_base = t_base * 0
    y_feature = first_order_combined(p[:2], (t_feature - p[2]))

    return np.r_[y_base, y_feature]


def first_order_fitting_without_normalization(
    p_guess, data, plotting=False, filename=None
):
    """Fitting first_order_shift function to data, which has not been normalized"""

    x = data[:, 0]
    y = data[:, 1]

    p = least_squares(fun=residual_generic, x0=p_guess, args=(x, y, first_order_shift))
    y_fit = first_order_shift(p.x, x)

    if plotting:
        fig, ax = plt.subplots()
        ax.plot(x, y, ".")
        ax.plot(x, y_fit, linewidth=1)
        if filename is not None:
            fig.savefig(filename, dpi=400)

    return p.x


def fit_data(data_df, filename=None):
    """Fit data to first order rate law"""

    # subset data to relevant statuses
    relevant_statuses = ["DEGASSING", "PREREATION-BASELINE", "REACTION"]
    data_subset = data_df[data_df["status"].isin(relevant_statuses)]

    # get relevant time and oxygen data
    time_data = data_subset["duration"].values
    oxygen_data = data_subset["uM_1"].values

    # get pre-reaction time range
    reaction_start_time = data_subset[data_subset["status"] == "REACTION"][
        "duration"
    ].values[0]
    pre_reaction_time_range = (data_subset["duration"].values[0], reaction_start_time)

    # correct baseline
    corrected_data = pre_signal_fitting(
        np.c_[time_data, oxygen_data], *pre_reaction_time_range, 2, plotting=False
    )

    # fit first order rate law
    rate_law_guess = np.array([10.0, 0.01, reaction_start_time])
    rate_law_fit = first_order_fitting_without_normalization(
        rate_law_guess, corrected_data, plotting=True, filename=filename
    )

    # print rate constant
    print(f"Rate constant k1 (s^-1): {rate_law_fit[1]:.3f}")

    return rate_law_fit[1]
