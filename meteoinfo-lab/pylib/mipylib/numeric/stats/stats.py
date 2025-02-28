# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-9
# Purpose: MeteoInfoLab stats module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.math.stats import StatsUtil
from org.meteoinfo.ndarray.math import ArrayMath
from org.meteoinfo.ndarray import Array

from ..core import numeric as np
from collections import namedtuple
import warnings

__all__ = [
    'chi2_contingency','chisquare','covariance','cov','pearsonr','spearmanr','kendalltau',
    'linregress','mlinregress','percentile','ttest_1samp', 'ttest_ind','ttest_rel','taylor_stats'
    ]

def _contains_nan(a, nan_policy='propagate'):
    policies = ['propagate', 'raise', 'omit']
    if nan_policy not in policies:
        raise ValueError("nan_policy must be one of {%s}" %
                         ', '.join("'%s'" % s for s in policies))
    try:
        # Calling np.sum to avoid creating a huge array into memory
        # e.g. np.isnan(a).any()
        contains_nan = a.contains_nan()
    except TypeError:
        # This can happen when attempting to sum things which are not
        # numbers (e.g. as in the function `mode`). Try an alternative method:
        try:
            contains_nan = np.nan in set(a.ravel())
        except TypeError:
            # Don't know what to do. Fall back to omitting nan values and
            # issue a warning.
            contains_nan = False
            nan_policy = 'omit'
            warnings.warn("The input array could not be properly "
                          "checked for nan values. nan values "
                          "will be ignored.", RuntimeWarning)

    if contains_nan and nan_policy == 'raise':
        raise ValueError("The input contains nan values")

    return contains_nan, nan_policy

def covariance(x, y, bias=False):
    '''
    Calculate covariance of two array.
    
    :param x: (*array_like*) A 1-D array containing multiple variables and observations.
    :param y: (*array_like*) An additional set of variables and observations. y has the same form as 
        that of x.
    :param bias: (*boolean*) Default normalization (False) is by (N - 1), where N is the number of observations 
        given (unbiased estimate). If bias is True, then normalization is by N.
        
    returns: Covariance
    '''
    if isinstance(x, (list, tuple)):
        x = np.array(x)
    if isinstance(y, (list, tuple)):
        y = np.array(y)
    r = StatsUtil.covariance(x.asarray(), y.asarray(), bias)
    return r
    
def cov(m, y=None, rowvar=True, bias=False):
    '''
    Estimate a covariance matrix.
    
    :param m: (*array_like*) A 1-D or 2-D array containing multiple variables and observations.
    :param y: (*array_like*) Optional. An additional set of variables and observations. y has the same form as 
        that of m.
    :param rowvar: (*boolean*) If ``rowvar`` is True (default), then each row represents a variable, with 
        observations in the columns. Otherwise, the relationship is transposed: each column represents a 
        variable, while the rows contain observations.
    :param bias: (*boolean*) Default normalization (False) is by (N - 1), where N is the number of observations 
        given (unbiased estimate). If bias is True, then normalization is by N.
    
    :returns: Covariance.
    '''
    if isinstance(m, list):
        m = np.array(m)
    if rowvar == True and m.ndim == 2:
        m = m.T
    if y is None:        
        r = StatsUtil.cov(m.asarray(), not bias)
        if isinstance(r, Array):
            return np.array(r)
        else:
            return r
    else:
        if isinstance(y, list):
            y = np.array(y)
        if rowvar == True and y.ndim == 2:
            y = y.T
        r = StatsUtil.cov(m.asarray(), y.asarray(), not bias)
        return np.array(r)
        
def pearsonr(x, y, axis=None):
    '''
    Calculates a Pearson correlation coefficient and the p-value for testing non-correlation.

    The Pearson correlation coefficient measures the linear relationship between two datasets. 
    Strictly speaking, Pearson’s correlation requires that each dataset be normally distributed, 
    and not necessarily zero-mean. Like other correlation coefficients, this one varies between 
    -1 and +1 with 0 implying no correlation. Correlations of -1 or +1 imply an exact linear 
    relationship. Positive correlations imply that as x increases, so does y. Negative 
    correlations imply that as x increases, y decreases.

    The p-value roughly indicates the probability of an uncorrelated system producing datasets 
    that have a Pearson correlation at least as extreme as the one computed from these datasets. 
    The p-values are not entirely reliable but are probably reasonable for datasets larger than 
    500 or so.
    
    :param x: (*array_like*) x data array.
    :param y: (*array_like*) y data array.
    :param axis: (*int*) By default, the index is into the flattened array, otherwise 
        along the specified axis.
    
    :returns: Pearson’s correlation coefficient and 2-tailed p-value.
    '''
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(y, list):
        y = np.array(y)
    if axis is None:
        r = StatsUtil.pearsonr(x.asarray(), y.asarray())
        return r[0], r[1]
    else:
        r = StatsUtil.pearsonr(x.asarray(), y.asarray(), axis)
        return np.array(r[0]), np.array(r[1])

KendalltauResult = namedtuple('KendalltauResult', ('correlation', 'pvalue'))

def kendalltau(x, y, nan_policy='propagate', method='auto', variant='b'):
    """
    Calculates Kendall's tau, a correlation measure for ordinal data.
    
    Kendall's tau is a measure of the correspondence between two rankings.
    Values close to 1 indicate strong agreement, values close to -1 indicate
    strong disagreement.  This is the 1945 "tau-b" version of Kendall's
    tau [2]_, which can account for ties and which reduces to the 1938 "tau-a"
    version [1]_ in absence of ties.
    
    :param x: (*array_like*) x data array.
    :param y: (*array_like*) y data array.
    :param non_policy: (*str*) {'auto', 'asymptotic', 'exact'}, optional
        Defines which method is used to calculate the p-value [5]_.
        The following options are available (default is 'auto'):
          * 'auto': selects the appropriate method based on a trade-off
            between speed and accuracy
          * 'asymptotic': uses a normal approximation valid for large samples
          * 'exact': computes the exact p-value, but can only be used if no ties
            are present. As the sample size increases, the 'exact' computation
            time may grow and the result may lose some precision.
    :param variant: (*str*) {'b', 'c'}, optional
        Defines which variant of Kendall's tau is returned. Default is 'b'.
    
    :returns: Correlation.
    
    Notes
    -----
    The definition of Kendall's tau that is used is [2]_::
      tau = (P - Q) / sqrt((P + Q + T) * (P + Q + U))
    where P is the number of concordant pairs, Q the number of discordant
    pairs, T the number of ties only in `x`, and U the number of ties only in
    `y`.  If a tie occurs for the same pair in both `x` and `y`, it is not
    added to either T or U.
    References
    ----------
    .. [1] Maurice G. Kendall, "A New Measure of Rank Correlation", Biometrika
           Vol. 30, No. 1/2, pp. 81-93, 1938.
    .. [2] Maurice G. Kendall, "The treatment of ties in ranking problems",
           Biometrika Vol. 33, No. 3, pp. 239-251. 1945.
    .. [3] Gottfried E. Noether, "Elements of Nonparametric Statistics", John
           Wiley & Sons, 1967.
    .. [4] Peter M. Fenwick, "A new data structure for cumulative frequency
           tables", Software: Practice and Experience, Vol. 24, No. 3,
           pp. 327-336, 1994.
    .. [5] Maurice G. Kendall, "Rank Correlation Methods" (4th Edition),
           Charles Griffin & Co., 1970.
    """
    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()

    # if x.size != y.size:
    #     raise ValueError("All inputs to `kendalltau` must be of the same "
    #                      f"size, found x-size {x.size} and y-size {y.size}")
    # elif not x.size or not y.size:
    #     # Return NaN if arrays are empty
    #     return KendalltauResult(np.nan, np.nan)
    #
    # # check both x and y
    # cnx, npx = _contains_nan(x, nan_policy)
    # cny, npy = _contains_nan(y, nan_policy)
    # contains_nan = cnx or cny
    # if npx == 'omit' or npy == 'omit':
    #     nan_policy = 'omit'
    # elif contains_nan and nan_policy == 'omit':
    #     x = ma.masked_invalid(x)
    #     y = ma.masked_invalid(y)
    #     if variant == 'b':
    #         return mstats_basic.kendalltau(x, y, method=method, use_ties=True)
    #     else:
    #         raise ValueError("Only variant 'b' is supported for masked arrays")
    #
    # if isinstance(x, list):
    #     x = np.array(x)
    # if isinstance(y, list):
    #     y = np.array(y)
    r = StatsUtil.kendalltau(x.asarray(), y.asarray())
    return r[0], r[1]

def spearmanr(m, y=None, axis=0):
    '''
    Calculates a Spearman rank-order correlation coefficient.
    
    The Spearman correlation is a nonparametric measure of the monotonicity of the relationship 
    between two datasets. Unlike the Pearson correlation, the Spearman correlation does not 
    assume that both datasets are normally distributed. Like other correlation coefficients, 
    this one varies between -1 and +1 with 0 implying no correlation. Correlations of -1 or +1 
    imply an exact monotonic relationship. Positive correlations imply that as x increases, so 
    does y. Negative correlations imply that as x increases, y decreases.
    
    :param m: (*array_like*) A 1-D or 2-D array containing multiple variables and observations.
    :param y: (*array_like*) Optional. An additional set of variables and observations. y has the same form as 
        that of m.
    :param axis: (*int*) If axis=0 (default), then each column represents a variable, with 
        observations in the rows. If axis=1, the relationship is transposed: each row represents 
        a variable, while the columns contain observations..
    
    :returns: Spearman correlation matrix.
    '''
    if isinstance(m, list):
        m = np.array(m)
    if axis == 1 and m.ndim == 2:
        m = m.T
    if y is None:        
        r = StatsUtil.spearmanr(m.asarray())
        if isinstance(r, Array):
            return np.array(r)
        else:
            return r
    else:
        if isinstance(y, list):
            y = np.array(y)
        if axis == 1 and y.ndim == 2:
            y = y.T
        r = StatsUtil.spearmanr(m.asarray(), y.asarray())
        return r[0], r[1]
        
def linregress(x, y, outvdn=False):
    '''
    Calculate a linear least-squares regression for two sets of measurements.
    
    :param x, y: (*array_like*) Two sets of measurements. Both arrays should have the same length.
    :param outvdn: (*boolean*) Output validate data number or not. Default is False.
    
    :returns: Result slope, intercept, relative coefficient, two-sided p-value for a hypothesis test 
        whose null hypothesis is that the slope is zero, standard error of the estimated gradient, 
        validate data number (remove NaN values).
    '''
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(y, list):
        y = np.array(y)
    r = ArrayMath.lineRegress(x.asarray(), y.asarray())
    if outvdn:
        return r[0], r[1], r[2], r[3], r[4], r[5]
    else:
        return r[0], r[1], r[2], r[3], r[4]
    
def mlinregress(y, x):
    '''
    Implements ordinary least squares (OLS) to estimate the parameters of a multiple linear 
    regression model.
    
    :param y: (*array_like*) Y sample data - one dimension array.
    :param x: (*array_like*) X sample data - two dimension array.
    
    :returns: Estimated regression parameters and residuals.
    '''
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(y, list):
        y = np.array(y)
    r = StatsUtil.multipleLineRegress_OLS(y.asarray(), x.asarray())
    return np.array(r[0]), np.array(r[1])
    
def percentile(a, q, axis=None):
    '''
    Compute the qth percentile of the data along the specified axis.
    
    :param a: (*array_like*) Input array.
    :param q: (*float*) float in range of [0,100].
        Percentile to compute, which must be between 0 and 100 inclusive.
    :param axis: (*int*) Axis or axes along which the percentiles are computed. The default is 
        to compute the percentile along a flattened version of the array.
    
    :returns: (*float*) qth percentile value.
    '''
    if isinstance(a, list):
        a = np.array(x)
    if axis is None:
        r = StatsUtil.percentile(a.asarray(), q)
    else:
        r = StatsUtil.percentile(a.asarray(), q, axis)
        r = np.array(r)
    return r
    
def ttest_1samp(a, popmean):
    '''
    Calculate the T-test for the mean of ONE group of scores.

    This is a two-sided test for the null hypothesis that the expected value (mean) of 
    a sample of independent observations a is equal to the given population mean, popmean.
    
    :param a: (*array_like*) Sample observation.
    :param popmean: (*float*) Expected value in null hypothesis.
    
    :returns: t-statistic and p-value
    '''
    if isinstance(a, list):
        a = np.array(x)
    r = StatsUtil.tTest(a.asarray(), popmean)
    return r[0], r[1]
    
def ttest_rel(a, b):
    '''
    Calculates the T-test on TWO RELATED samples of scores, a and b.

    This is a two-sided test for the null hypothesis that 2 related or repeated samples 
    have identical average (expected) values.
    
    :param a: (*array_like*) Sample data a.
    :param b: (*array_like*) Sample data b.
    
    :returns: t-statistic and p-value
    '''
    if isinstance(a, list):
        a = np.array(a)
    if isinstance(b, list):
        b = np.array(b)
    r = StatsUtil.pairedTTest(a.asarray(), b.asarray())
    return r[0], r[1]
    
def ttest_ind(a, b):
    '''
    Calculates the T-test for the means of TWO INDEPENDENT samples of scores.

    This is a two-sided test for the null hypothesis that 2 independent samples have 
    identical average (expected) values. This test assumes that the populations have 
    identical variances.
    
    :param a: (*array_like*) Sample data a.
    :param b: (*array_like*) Sample data b.
    
    :returns: t-statistic and p-value
    '''
    if isinstance(a, list):
        a = np.array(a)
    if isinstance(b, list):
        b = np.array(b)
    r = StatsUtil.tTest(a.asarray(), b.asarray())
    return r[0], r[1]
    
def chisquare(f_obs, f_exp=None):
    '''
    Calculates a one-way chi square test.

    The chi square test tests the null hypothesis that the categorical data has the 
    given frequencies.
    
    :param f_obs: (*array_like*) Observed frequencies in each category.
    :param f_exp: (*array_like*) Expected frequencies in each category. By default the categories 
        are assumed to be equally likely.
    
    :returns: Chi-square statistic and p-value
    '''
    if isinstance(f_obs, list):
        f_obs = np.array(f_obs)
    if f_exp is None:
        n = len(f_obs)
        f_exp = np.ones(n) / n * f_obs.sum()
    elif isinstance(f_exp, list):
        f_exp = np.array(f_exp)
    r = StatsUtil.chiSquareTest(f_exp.asarray(), f_obs.asarray())
    return r[0], r[1]
    
def chi2_contingency(observed):
    '''
    Chi-square test of independence of variables in a contingency table.

    This function computes the chi-square statistic and p-value for the hypothesis test of 
    independence of the observed frequencies in the contingency table observed.
    
    :param observed: (*array_like*) The contingency table. The table contains the observed 
        frequencies (i.e. number of occurrences) in each category. In the two-dimensional case, 
        the table is often described as an `R x C table`.
    
    :returns: Chi-square statistic and p-value
    '''
    if isinstance(observed, list):
        observed = np.array(observed)
    r = StatsUtil.chiSquareTest(observed.asarray())
    return r[0], r[1]

def taylor_stats(p, r):
    '''
    Calculates the statistics needed to create a Taylor diagram as
    described in Taylor (2001) using the data provided in the predicted
    field (PREDICTED) and the reference field (REFERENCE).

    The statistics are returned in the STATS dictionary.
    If a dictionary is provided for PREDICTED or REFERENCE, then
    the name of the field must be supplied in FIELD.

    The function currently supports dictionaries, lists, and np.ndarray,
    types for the PREDICTED and REFERENCE variables.

    Input:
    p : predicted field
    r : reference field
    NORM      : logical flag specifying statistics are to be normalized
                with respect to standard deviation of reference field
                = True,  statistics are normalized
                = False, statistics are not normalized

    Output:
    STATS          : dictionary containing statistics
    STATS['ccoef'] : correlation coefficients (R)
    STATS['crmsd'] : centered root-mean-square (RMS) differences (E')
    STATS['sdev']  : standard deviations

    Each of these outputs are one-dimensional with the same length.
    First index corresponds to the reference series for the diagram.
    For example SDEV[1] is the standard deviation of the reference
    series (sigma_r) and SDEV[2:N] are the standard deviations of the
    other (predicted) series.

    Reference:

    Taylor, K. E. (2001), Summarizing multiple aspects of model
      performance in a single diagram, J. Geophys. Res., 106(D7),
      7183-7192, doi:10.1029/2000JD900719.
    Author: Peter A. Rochford
        Symplectic, LLC
        www.thesymplectic.com
        prochford@thesymplectic.com
    Created on Dec 3, 2016
    '''
    # Check that dimensions of predicted and reference fields match
    pdims= p.shape
    rdims= r.shape
    if pdims != rdims:
        message = 'predicted and reference field dimensions do not' + \
                  ' match.\n' + \
                  'shape(predicted)= ' + str(pdims) + ', ' + \
                  'shape(reference)= ' + str(rdims) + \
                  '\npredicted type: ' + str(type(p))
        raise ValueError(message)

    # Calculate correlation coefficient
    ccoef = np.corrcoef(p, r)
    ccoef = ccoef[0]

    # Calculate centered root-mean-square (RMS) difference (E')^2
    # Calculate means
    pmean = np.mean(p)
    rmean = np.mean(r)

    # Calculate (E')^2
    crmsd = np.square((p - pmean) - (r - rmean))
    crmsd = np.sum(crmsd)/p.size
    crmsd = np.sqrt(crmsd)
    crmsd = [0.0, crmsd]

    # Calculate standard deviation of predicted field w.r.t N (sigma_p)
    sdevp = np.std(p)

    # Calculate standard deviation of reference field w.r.t N (sigma_r)
    sdevr = np.std(r)
    sdev = [sdevr, sdevp]

    # Store statistics in a dictionary
    stats = {'ccoef': ccoef, 'crmsd': crmsd, 'sdev': sdev}
    return stats