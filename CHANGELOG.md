# Changelog

## Version 0.7.1 - November 30, 2022
### Bugfixes
- `bp.io.biopac`:wrong index name for dataframe export when setting parameter `"index = None"`

## Version 0.7.0 - November 22, 2022
### Added
- `biopsykit.io`: 
  - Added functions to directly load aTimeLogger files (`biopsykit.io.load_atimelogger_file`) and to 
    convert time log files into a dictionary with start/end times (`biopsykit.io.convert_time_log_dict`)
  - Added support for loading data acquired from the [Biopac](https://www.biopac.com/) system (`biopsykit.io.biopac`)
- `biopsykit.plotting`: Added function to conveniently plot feature pairs (`biopsykit.plotting.feature_pairplot`), 
  which is a wrapper function for `seaborn.pairplot`
### Improvements
- Adapted code to don't show pandas future warnings anymore
- `biopsykit.plotting.hr_ensemble_plot`: Added "is_relative" argument to style y-axis accordingly
- `biopsykit.stats.StatsPipeline`: Improved latex export for different effect sizes
- `biopsykit.io.nilspod`: Improved handling of loading NilsPods files
- `biopsykit.utils.data_processing`: Added support for data dicts with tuples instead of strings as keys
### Bugfixes
- some small bugfixes

## Version 0.6.1 - August 19, 2022
### Improvements
- `biopsykit.signals.ecg.EcgProcessor`: improved handling of errors occurring during ECG processing
- `biopsykit.plotting`: Improved boxplot behavior due to the use of the new light palettes of 
  [`fau-colors`](https://github.com/mad-lab-fau/fau_colors). 
  See the [`StatsPipeline & Plotting Example`](https://biopsykit.readthedocs.io/en/latest/examples/_notebooks/StatsPipeline_Plotting_Example.html)
  for further information.
### Bugfixes: 
- `biopsykit.signals.imu.ActivityCounts`: added timezone support ([PR 31](https://github.com/mad-lab-fau/BioPsyKit/pull/31))
- `biopsykit.signals.imu.RestPeriods`: fixed bug in computing resting periods 
  (old implementation could lead to classifying a long period of activity as the main rest period.) 
  ([PR 32](https://github.com/mad-lab-fau/BioPsyKit/pull/32))
- `biopsykit.signals.imu.ActivityCounts`: fixed bug(s) in computing activity counts 
  ([PR 33](https://github.com/mad-lab-fau/BioPsyKit/pull/33))
- `biopsykit.stats.StatsPipeline`: fixed bugs in LaTeX export of result tables

## Version 0.5.1 - May 24, 2022
### New Features
- `biopsykit.classification`: `SklearnPipelinePermuter` now supports regression
### Bugfixes
- further small bugfixes

## Version 0.5.0 - April 21, 2022
### New Features
- `biopsykit.stats`: Added new statistic features:
  - `biopsykit.stats.multicoll`: Functions to handle multicollinearity in data
  - `biopsykit.stats.regression`: Functions for performing more "complex" regression analysis 
    (currently: stepwise backward multiple linear regression)
- `biopsykit.classification`: `SklearnPipelinePermuter` instances can now be saved as pickle files and imported again
- 
### Bugfixes
_ `biopsykit.utils.time`: Renamed `time_to_datetime` to `time_to_timedelta` (wrong function name)

## Version 0.4.2 - March 18, 2022
### Bugfixes
- `biopsykit.stats.StatsPipeline`: Fixed bug of failing to generate significance brackets from within-subjects 
  stats data
- `biopsykit.protocols.plotting.saliva_plot`: Fixed wrong plot styling

### New Features
- `biopsykit.plotting.feature_boxplot`: Added `legend_title` parameter
- `biopsykit.classification.model_selection.nested_cv`: Train and test indices are now saved for each fold of the nested cv
- `biopsykit.classification.model_selection.SklearnPipelinePermuter`:
  - Updated "scoring" and "refit" behavior
  - Added confusion matrix, true labels, predicted labels, train and test indices per fold and flattened


## Version 0.4.1 - January 24, 2022
### Bugfixes
- `biopsykit.signals.imu.static_moment_detection`: Now returning an empty dataframe with correct column names when 
  detecting no static moments
- `biopsykit.classification.model_selection.SkleanPipelinePermuter`: Pipelines are now correctly sorted by their 
  mean test scores
- `biopsykit.protocols.plotting.saliva_plot`: Fixed bug when attempting to plot saliva data without sample times
_ `biopsykit.plotting.feature_boxplots`: Updated plotting color configuration: If an alpha value smaller than 1.0 is 
  passed, the saturation is by default set to 1.0 to still have a nice color shading despite the transparency
- `biopsykit.protocols.TSST`: Changed default TSST test time from 20 to 15 min

## Version 0.4.0 - January 05, 2022
### New Features
- `biopsykit.stats.StatsPipeline`:
  - added new functions `StatsPipeline.results_to_latex_table` and `StatsPipeline.stats_to_latex` 
    to convert statistical analysis results to LaTeX tables and to inline LaTeX code, respectively. 
  - changed argument `stats_type` to `stats_effect_type`.  
    **WARNING: This is a breaking change!** The use of `stats_type` is deprecated and will be removed in `0.5.0`!
- `biopsykit.colors`: Removed `biopsykit.colors` module and replaced it with colors from the new `fau_colors` package.  
  **WARNING: This is a breaking change!**
### Bugfixes
- `biopsykit.signals.imu.static_moment_detection`: end indices of static moments are inclusive instead of exclusive
### Misc
- `biopsykit.utils.array_handling`: if `overlap_percent` > 1 it is converted to a fraction [0.0, 1.0]

## Version 0.3.7 - December 03, 2021
### Misc
- Updated dependencies: now using scikit-learn `>=1.0`

## Version 0.3.6 - December 01, 2021
### New Features
- `biopsykit.io.ecg`: Added functions to write a dictionary of dataframes to a series of csv files (and vice versa).
- `biopsykit.classification.model_selection`: Model selection now also supports to perform randomized-search instead 
  of grid-search for hyperparameter optimization of machine learning pipelines 
### Bugfixes
- `biopsykit.questionnaires.psqi`: Fixed bug in computing Pittsburgh Sleep Quality Index (PSQI)

## Version 0.3.5 – November 05, 2021
### Bugfixes
- further bugfixes (incorrect handling of duplicate index values) for Sleep Analyzer import data using
  `biopsykit.io.sleep_analyzer.load_withings_sleep_analyzer_raw_file()`


## Version 0.3.4 – November 04, 2021
### New Features
- added function `biopsykit.utils.time.extract_time_from_filename()` that can parse time information from a filename
- added function `biopsykit.metadata.gender_counts()`
### Bugfixes
- fixed bug when importing Sleep Analyzer data using
  `biopsykit.io.sleep_analyzer.load_withings_sleep_analyzer_raw_file()`
- `biopsykit.io.load_time_log()`: time log dataframes imported using this function will now have "phase" as column name
### Misc
- updated the minimum version of the `pingouin` dependency to 0.5.0 because it's strongly recommended from the authors 
  of `pingouin` (https://pingouin-stats.org/changelog.html#v0-5-0-october-2021)
- switched from `doit` to `poethepoet` as task runner.

## Version 0.3.2 – October 12, 2021
- final version of BioPsyKit for submission to the [Journal of Open Source Software](https://joss.theoj.org/).
- improved documentation (e.g., included Example Gallery)

## Version 0.3.1 – October 5, 2021
- `biopsykit.utils.file_handling.get_subject_dirs()`: replaced `glob`-style matching of regex strings 
  by `re`-style matching. This allows more flexibility when filtering for directories that match a specific pattern. 
- `biopsykit.questionnaires`:
  - fixed wrong implementation of ASQ (`biopsykit.questionnaires.asq`)
  - added modified version of the ASQ (ASQ_MOD, `biopsykit.questionnaires.asq_mod`) according to (Kramer et al., 2019)
- implemented changes as result of JOSS submission, including:
  - improved handling of example data
  - improved interface for multi-test comparison in `StatsPipeline`
  - improved colormap handling
  - new function to load dataframes in long-format (`biopsykit.io.load_long_format_csv`)

## Version 0.3.0 – September 1, 2021
- initial commit
