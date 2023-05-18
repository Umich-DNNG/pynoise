### script for analyzing .lmx files or .xml files using FAUST/lmx


# standard imports
import matplotlib.pyplot as plt
import glob
import sys
import csv
import numpy as np
import os
import copy
import shutil
from time import gmtime, strftime
from itertools import zip_longest
from scipy.optimize import curve_fit
from scipy.stats import poisson as poissiondist
from multiprocessing import Pool

###################### MODIFY THIS PATH! ############################
#sys.path.append(r"U:\++Data\codes\lab\FAUST")  # specify path to modules if not in system
sys.path.append(r"X:\Scratch\Hutchinson\FAUSTlmxModified\FAUST")  # specify path to modules if not in system

# local imports
from lmx.factory import readLMXFile
from lmx.Header import *
from lmx.ToEvents import *  # For interpreting various file types
from lmx.feynman.FeynmanHistogramCalculator import *  # Import feynman scripts
from lmx.feynman.FeynmanYAnalysis import *
from lmx.feynman.SequentialBinning import *
from lmx.feynman.json import *
from lmx.feynman.pickle import *
from lmx.rossi.RossiHistogramCalculator import *  # Import Rossi-alpha scripts
from lmx.rossi.RossiHistogram import *
from lmx.rossi.RossiBinning import *
from lmx.rossi.Plot import *
from plot_gatewidth import *
from rates import *
from multiplication import *
from channel_plot import *
from time_vs_events import *
from empty_lists import *
from ReadXML import *
from print_header import *
from script_backup import *
from input_paths import *
from output_paths import *
from histogram_sum import *
from compare_combine_sum import *
from combine_rates import *
from read_csv import *


################################################################################
# begin user specifications

# input path
#filepath = r'X:\Scratch\Hutchinson\FAUSTlmxModified\FAUST\lmx\scratch\input\SCRAP_bare\split'
filepath = ''
# output path will be in a subdirectory within the filepath
save_path = 'output'
# Put True if you want the output files to be in nested subdirectories by type
output_nested_subdirectories = True
# input type. currently supports .lmx, .xml, and .csv
input_type = '.xml'
#input_type = '.lmx'
#input_type = '.csv'
# this is a tuple used for plot legends. example below.
file_descriptions = ()
#file_descriptions = ('50 layers','60 layers','70 layers','80 layers','90 layers','100 layers','110 layers','120 layers')


# analysis types
# Allowed calculation types are: 'Multiplicity' or 'Cf'. Anything other than these will not do further calculations
calculation_type = ''
# Do you want to plot Feynman histograms
plot_histograms = False
# Do you want to plot individual files
plot_individual_files = False
# Do you want to plot all files together (files = series, x-axis = gate-width)
plot_all_files_vs_gw = False
# Do you want to plot all files together (x-axis = files)
plot_all_files_vs_con = False
# Do you want to plot the channels?
plot_channels = False
# Do you want to perform Rossi-alpha analysis
perform_Rossi = False
# Do you want to read in the header?
read_header = False


# options for combining results of multiple files
# these options should only be used if the files are "identical" (i.e. multiple files on the exact same configuration)
# Put True if you want to have Y2 rate results combined (used if all files are supposed to be equivalent)
combine_Y2_rate_results = False
# Put True if you want combined statistical plots
combine_statistical_plots = False
# Put True if you want to have Feynman histograms summed. Note that additional analysis will be performed on summed histograms depending upon the other user options.
sum_Feynman_histograms = False
# Put True to compare histogram sum results with the combine_Y2_rate_results
# Note: if compare_combine_Y2_rate_results_and_Feynman_sum is set to True and calculation_type is 'Multiplicity', then perform_Y2_single_fit, perform_Y2_double_fit, and use_user_specified_lifetime must match the setting used when creating the original rate .csv files.
compare_combine_Y2_rate_results_and_Feynman_sum = False
# If both combine_Y2_rate_results and sum_Feynman_histograms are set to True, then the paths below are NOT used, and the paths created during execution are used instead.
combine_Y2_rate_results_filepath = ''
#combine_Y2_rate_results_filepath = r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\0.0Ni_single file\output\Combined\Rates'
sum_histogram_filepath = ''
#sum_histogram_filepath = r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\split files\offset\0.0Ni_single file\output\Histogram_Sum\Rates'
# Put True to compare a single file, histogram sum results, and combine_Y2_rate_results
compare_individual_file_and_combine_Y2_rate_results_and_Feynman_sum = False
# This expects both a path AND a filename in the same string
#individual_filepath_and_filename = r'\\slip.lanl.gov\NCERC\Data\Hand-stacking Data\2019 03 05 NeSO\021. Np+0.0Ni - Benchmark (2 NoMADs)\output\Individual_Files\Rates\2019_03_07_162246-Sequential.xml.csv'
individual_filepath_and_filename = ''

# output options
# Do you want to print detailed results
print_results = False
# Do you want to output .csv files?
output_csv = True


# Feynman histogram options (used if plot_histograms is set to True)
# If plotting histograms, do you want to have them match axes?
histogram_match_axis = False
# Do you want to normalize the Feynman histograms (p_n instead of C_n)
histogram_normalize = False
# If sum_Feynman_histograms is True, put True if you want to plot both the individual and sum histograms. Default is False
plot_sum_and_individual_histogram = False

# Y2 options (used if plot_individual_files, plot_all_files_vs_gw, and/or plot_all_files_vs_con is set to True)
# Do you want to perform Y2 fits?
perform_Y2_single_fit = False
perform_Y2_double_fit = False


# desired gate-width
# note that gate-width lists are only supported for .lmx files. This is simpy ignored for .xml files
# units are nano-sec
# Default testing list
gatewidth_list = [256000, 512000, 1024000, 2048000]
# Power of 2 from 1 micro-sec to 2048 micro-sec
#gatewidth_list = [1000, 2000, 4000, 8000, 16000, 32000, 64000, 128000, 256000, 512000, 1024000, 2048000]
# Momentum defaults: every 4 micro-sec to 2048 micro-sec
#gatewidth_list = [4000, 8000, 12000, 16000, 20000, 24000, 28000, 32000, 36000, 40000, 44000, 48000, 52000, 56000, 60000, 64000, 68000, 72000, 76000, 80000, 84000, 88000, 92000, 96000, 100000, 104000, 108000, 112000, 116000, 120000, 124000, 128000, 132000, 136000, 140000, 144000, 148000, 152000, 156000, 160000, 164000, 168000, 172000, 176000, 180000, 184000, 188000, 192000, 196000, 200000, 204000, 208000, 212000, 216000, 220000, 224000, 228000, 232000, 236000, 240000, 244000, 248000, 252000, 256000, 260000, 264000, 268000, 272000, 276000, 280000, 284000, 288000, 292000, 296000, 300000, 304000, 308000, 312000, 316000, 320000, 324000, 328000, 332000, 336000, 340000, 344000, 348000, 352000, 356000, 360000, 364000, 368000, 372000, 376000, 380000, 384000, 388000, 392000, 396000, 400000, 404000, 408000, 412000, 416000, 420000, 424000, 428000, 432000, 436000, 440000, 444000, 448000, 452000, 456000, 460000, 464000, 468000, 472000, 476000, 480000, 484000, 488000, 492000, 496000, 500000, 504000, 508000, 512000, 516000, 520000, 524000, 528000, 532000, 536000, 540000, 544000, 548000, 552000, 556000, 560000, 564000, 568000, 572000, 576000, 580000, 584000, 588000, 592000, 596000, 600000, 604000, 608000, 612000, 616000, 620000, 624000, 628000, 632000, 636000, 640000, 644000, 648000, 652000, 656000, 660000, 664000, 668000, 672000, 676000, 680000, 684000, 688000, 692000, 696000, 700000, 704000, 708000, 712000, 716000, 720000, 724000, 728000, 732000, 736000, 740000, 744000, 748000, 752000, 756000, 760000, 764000, 768000, 772000, 776000, 780000, 784000, 788000, 792000, 796000, 800000, 804000, 808000, 812000, 816000, 820000, 824000, 828000, 832000, 836000, 840000, 844000, 848000, 852000, 856000, 860000, 864000, 868000, 872000, 876000, 880000, 884000, 888000, 892000, 896000, 900000, 904000, 908000, 912000, 916000, 920000, 924000, 928000, 932000, 936000, 940000, 944000, 948000, 952000, 956000, 960000, 964000, 968000, 972000, 976000, 980000, 984000, 988000, 992000, 996000, 1000000, 1004000, 1008000, 1012000, 1016000, 1020000, 1024000, 1028000, 1032000, 1036000, 1040000, 1044000, 1048000, 1052000, 1056000, 1060000, 1064000, 1068000, 1072000, 1076000, 1080000, 1084000, 1088000, 1092000, 1096000, 1100000, 1104000, 1108000, 1112000, 1116000, 1120000, 1124000, 1128000, 1132000, 1136000, 1140000, 1144000, 1148000, 1152000, 1156000, 1160000, 1164000, 1168000, 1172000, 1176000, 1180000, 1184000, 1188000, 1192000, 1196000, 1200000, 1204000, 1208000, 1212000, 1216000, 1220000, 1224000, 1228000, 1232000, 1236000, 1240000, 1244000, 1248000, 1252000, 1256000, 1260000, 1264000, 1268000, 1272000, 1276000, 1280000, 1284000, 1288000, 1292000, 1296000, 1300000, 1304000, 1308000, 1312000, 1316000, 1320000, 1324000, 1328000, 1332000, 1336000, 1340000, 1344000, 1348000, 1352000, 1356000, 1360000, 1364000, 1368000, 1372000, 1376000, 1380000, 1384000, 1388000, 1392000, 1396000, 1400000, 1404000, 1408000, 1412000, 1416000, 1420000, 1424000, 1428000, 1432000, 1436000, 1440000, 1444000, 1448000, 1452000, 1456000, 1460000, 1464000, 1468000, 1472000, 1476000, 1480000, 1484000, 1488000, 1492000, 1496000, 1500000, 1504000, 1508000, 1512000, 1516000, 1520000, 1524000, 1528000, 1532000, 1536000, 1540000, 1544000, 1548000, 1552000, 1556000, 1560000, 1564000, 1568000, 1572000, 1576000, 1580000, 1584000, 1588000, 1592000, 1596000, 1600000, 1604000, 1608000, 1612000, 1616000, 1620000, 1624000, 1628000, 1632000, 1636000, 1640000, 1644000, 1648000, 1652000, 1656000, 1660000, 1664000, 1668000, 1672000, 1676000, 1680000, 1684000, 1688000, 1692000, 1696000, 1700000, 1704000, 1708000, 1712000, 1716000, 1720000, 1724000, 1728000, 1732000, 1736000, 1740000, 1744000, 1748000, 1752000, 1756000, 1760000, 1764000, 1768000, 1772000, 1776000, 1780000, 1784000, 1788000, 1792000, 1796000, 1800000, 1804000, 1808000, 1812000, 1816000, 1820000, 1824000, 1828000, 1832000, 1836000, 1840000, 1844000, 1848000, 1852000, 1856000, 1860000, 1864000, 1868000, 1872000, 1876000, 1880000, 1884000, 1888000, 1892000, 1896000, 1900000, 1904000, 1908000, 1912000, 1916000, 1920000, 1924000, 1928000, 1932000, 1936000, 1940000, 1944000, 1948000, 1952000, 1956000, 1960000, 1964000, 1968000, 1972000, 1976000, 1980000, 1984000, 1988000, 1992000, 1996000, 2000000, 2004000, 2008000, 2012000, 2016000, 2020000, 2024000, 2028000, 2032000, 2036000, 2040000, 2044000, 2048000]
# IER-518 gate-widths: log spaced from ~1 usec to ~31 msec
# should be 7.5 for ~31 msec
#gatewidth_list = np.logspace(3,6,num=5)
#for i in range(0,len(gatewidth_list)):
#    if gatewidth_list[i]%100 != 0:
#        gatewidth_list[i] = int(gatewidth_list[i]/100)*100
# Reserved for a user list
#gatewidth_list = []
#gatewidth_list = []

# Put a True if you want the .xml file to use the user gate-width list instead of using all gate-widths in the .xml file
xml_user_gatewidths = False
# If plot_all_files_vs_con is set to True, the code may take a very long time to run
# Put a True if you want to use gatewidth_list above for plot_all_files_vs_con (instead of all available gate-widths)
user_gatewidths_plot_all_files_vs_con = True


# Rossi options (performed if perform_Rossi is set to True)
# Do you want to perform Rossi-alpha fits?
perform_Rossi_fits = False
Rossi_reset_time=1000000
Rossi_bin_num=100


# desired marker size for plots (default=2)
marker_size = 2
# Put True if you want the y-axis on a log scale
yaxis_log = False
# Do you want the filename in plot titles?
plot_titles = False

# channel plot options
# include a title: Y or N
use_title = True
title_prefix = 'NOMAD'

# Put a True to copy PlotWrapper to the output directory
backup_script = True

# Additional options for combine_statistical_plots, default is to leave all as True
include_stats_reduced_moments = True
include_stats_moments = True
include_stats_rates = True

# Put True if you want the script to exit if any FIFO losses are in the .lmx files. 
exit_on_FIFO = True


# Cf252 source strength for Cf calculation type
# SCRAP: N2-515 Dec 2016
#Cf252_Fs = 759336.12
#Cf252_dFs = 7593.36
# NeSO N2-515 Mar 2019
#Cf252_Fs = 422526.08
#Cf252_dFs = 4225.26

# Detector efficiency used in 'Multiplicity' calculation type
# SCRaP defaults: 2 NOMADS @ 47 cm
eff = 0.0221069760032387
deff = 0.000221090568520993
# user-specified
#eff = 0
#deff = 0


# Nuclear data specifications (used only for 'Cf' and 'Multiplicity' calculation type)
alpha = 0.033
beta_eff_Pu = 0.00202
# spontaneous fission
# Pu-240 (see LA-UR-16-20375 and benchmark measured spreadsheet for references)
nuS1_Pu240 = 2.154
dnuS1_Pu240 = 0.005
nuS2_Pu240 = 1.894
dnuS2_Pu240 = 0.015
# Cm-244 from Zucker+Holden
nuS1_Cm244 = 2.72
dnuS1_Cm244 = 0.03
nuS2_Cm244 = 5.9388/2
dnuS2_Cm244 = 0.0853/2
# Cf-252 (see LA-UR-16-20375 and benchmark measured spreadsheet for references)
nuS1_Cf252 = 3.757
dnuS1_Cf252 = 0.010
nuS2_Cf252 = 5.976
dnuS2_Cf252 = 0.009
# induced fission
# U-235 (see benchmark measured spreadsheet for references)
nuI1_U235_thermal = 2.414
dnuI1_U235_thermal = 0.007
nuI2_U235_thermal = 2.3191
dnuI2_U235_thermal = 0.01485
nuI1_U235_1MeV = 2.532706
dnuI1_U235_1MeV = 0.007344218
nuI2_U235_1MeV = 2.584463375
dnuI2_U235_1MeV = 0.016549214
nuI1_U235_2MeV = 2.653354
dnuI1_U235_2MeV = 0.007694067
nuI2_U235_2MeV = 2.8027576
dnuI2_U235_2MeV = 0.017947027
# Np-237 (see "237Np_nubar_CGMF111.txt")
nuI1_Np237_thermal = 2.67
dnuI1_Np237_thermal = 0.088
nuI2_Np237_thermal = 5.71/2
dnuI2_Np237_thermal = 0.48/2
nuI1_Np237_1MeV = 2.76
dnuI1_Np237_1MeV = 0.088
nuI2_Np237_1MeV = 6.12/2
dnuI2_Np237_1MeV = 0.49/2
nuI1_Np237_2MeV = 2.91
dnuI1_Np237_2MeV = 0.088
nuI2_Np237_2MeV = 6.78/2
dnuI2_Np237_2MeV = 0.50/2
# Np-237 from Momentum with assumed 3% (arbitrary) unc
nuI1_Np237_1MeV_mom = 2.672849
dnuI1_Np237_1MeV_mom = 2.672849*0.03
nuI2_Np237_1MeV_mom = 2.854994
dnuI2_Np237_1MeV_mom = 2.854994*0.03
nuI1_Np237_2MeV_mom = 2.810049
dnuI1_Np237_2MeV_mom = 2.810049*0.03
nuI2_Np237_2MeV_mom = 3.164270
dnuI2_Np237_2MeV_mom = 3.164270*0.03
# Pu-239 (see LA-UR-16-20375 and benchmark measured spreadsheet for references)
nuI1_Pu239 = 3.182
dnuI1_Pu239 = 0.010
nuI2_Pu239 = 4.098
dnuI2_Pu239 = 0.011

# assign nuclear data for the files to be analyzed
# Pu defaults
nuI1 = nuI1_Pu239
dnuI1 = dnuI1_Pu239
nuI2 = nuI2_Pu239
dnuI2 = dnuI2_Pu239
nuS1 = nuS1_Pu240
dnuS1 = dnuS1_Pu240
nuS2 = nuS2_Pu240
dnuS2 = dnuS2_Pu240
beta_eff = beta_eff_Pu
# NeSO defaults
#nuI1 = nuI1_Np237_1MeV
#dnuI1 = dnuI1_Np237_1MeV
#nuI2 = nuI2_Np237_1MeV
#dnuI2 = dnuI2_Np237_1MeV
#nuS1 = nuS1_Cm244
#dnuS1 = dnuS1_Cm244
#nuS2 = nuS2_Cm244
#dnuS2 = dnuS2_Cm244
# user-specified
#nuI1 = 
#dnuI1 = 
#nuI2 = 
#dnuI2 = 
#nuS1 =
#dnuS1 =
#nuS2 = 
#dnuS2 = 

# end currently-supported user specifications
################################################################################




# Future user specifications

# Do you want to plot time vs events? LEAVE ON FALSE, NOT FULLY SUPPORTED YET
plot_time_vs_events = False



# user-specified lifetime (units of sec)
use_user_specified_lifetime = False
user_lifetime = 40.8e-6
user_lifetime_unc = 0

# end user specifications





print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

# Do you want to output event .csv files? Note that these can be VERY large. Only used for trouble-shooting
output_event_csv = False

perform_Y2_double_fit_continue = False

combine_Y2_rate_results_old_method = False

default_dir = os.getcwd()
print('Directory of python script ',default_dir)
os.chdir(filepath)
print('Directory of input files ',filepath)

# input paths
files = input_paths(input_type,filepath)

# output paths
output_dir, save_path = output_paths(save_path,default_dir,plot_histograms, plot_individual_files, plot_channels, output_csv, files, combine_Y2_rate_results)
if backup_script == True:
    script_backup(save_path, os.path.basename(__file__), '_'+strftime("%Y_%m_%d_%H%M%S", gmtime()), '.py')    
os.chdir(default_dir)


# perform checks
# Note that some checks result in exiting the script, while others simply print notes
if plot_histograms == False and plot_individual_files == False and plot_all_files_vs_gw == False and plot_all_files_vs_con == False and plot_channels == False and perform_Rossi == False and read_header == False and compare_combine_Y2_rate_results_and_Feynman_sum == False and compare_individual_file_and_combine_Y2_rate_results_and_Feynman_sum == False:
    sys.exit('Exit: no calculations to perform. Either plot_histograms, plot_individual_files, plot_all_files_vs_gw, plot_all_files_vs_con, plot_channels, perform_Rossi, read_header, and/or compare_combine_Y2_rate_results_and_Feynman_sum must be set to True.')
if len(files) == 0:
    print('Note: No input files found for input type =',input_type)
if input_type == '.xml' and xml_user_gatewidths != True:
    print('Note: Input type is .xml and xml_user_gatewidths is not set to True. Note that user gate-widths are being ignored and the gate-widths in the .xml file are used.')
if input_type == '.csv' and len(gatewidth_list) > 0:
    print('Note: The user gate-widths are ignored when input_type is .csv. The gate-widths in the .csv file are used instead.')
if plot_histograms != True and histogram_match_axis == True:
    sys.exit('Exit: if histogram_match_axis is set to True, then plot_histograms must also be set to True.')
if plot_histograms != True and histogram_normalize == True:
    sys.exit('Exit: if histogram_normalize_axis is set to True, then plot_histograms must also be set to True.')
if calculation_type == 'Multiplicity' and perform_Y2_single_fit != True and perform_Y2_double_fit != True:
    if plot_individual_files == True or plot_all_files_vs_gw == True or plot_all_files_vs_con == True:
        sys.exit('Exit: calculation type "Multiplicity" requires perform_Y2_single_fit and/or perform_Y2_double_fit to be True.')
if perform_Y2_double_fit == True and perform_Y2_single_fit != True:
    sys.exit('Exit: to perform perform_Y2_double_fit, both perform_Y2_double_fit and perform_Y2_single_fit must be set to True.')
if input_type != '.xml' and input_type != '.lmx' and input_type != '.csv':
    sys.exit('Exit: input type must be .lmx, .xml, or .csv')
if perform_Rossi == True and input_type != '.lmx':
    sys.exit('Exit: input type must be .lmx for Rossi-alpha')
if combine_Y2_rate_results == True and len(files) < 2:
    sys.exit('Exit: if combine_Y2_rate_results is set to True, then at least two files are required.')
if combine_Y2_rate_results == True:
    if plot_histograms == False and plot_individual_files == False and plot_all_files_vs_gw == False and plot_all_files_vs_con == False:
        sys.exit('Exit: if combine_Y2_rate_results is set to True, then Y2 analysis must be performed (plot_histograms, plot_individual_files, plot_all_files_vs_gw, or plot_all_files_vs_con must be set to True).')    
if read_header == True and input_type != '.lmx':
    print('Note: read_header is only supported for .lmx files (input_type = ".lmx").')
if exit_on_FIFO == True and input_type != '.lmx':
    print('Note: FIFO losses can only be checked if input_type is ".lmx". Not checking for FIFO losses.')
elif exit_on_FIFO == True and read_header != True:
    sys.exit('Note: FIFO losses are only checked if exit_on_FIFO is True, input_type is ".lmx", and read_header is True.')
if sum_Feynman_histograms == True and len(files) < 2:
    sys.exit('Exit: if sum_Feynman_histograms is set to True, then at least two files are required.')
if combine_statistical_plots == True and combine_Y2_rate_results != True:
    sys.exit('Exit: if combine_statistical_plots is set to True, then combine_Y2_rate_results must also be set to True.')
if plot_all_files_vs_con == True and combine_statistical_plots == True:
    print('Note: combine_statistical_plots and plot_all_files_vs_con are both set to True. To reduce "plot overload", only plots with statistical results overlaid are saved.') 
if input_type == '.csv' and output_csv == True:
    sys.exit('Exit: if input_type is ".csv", then output_csv should be set to False.')
if user_gatewidths_plot_all_files_vs_con == True and len(gatewidth_list) == 0:
    print('Note: user_gatewidths_plot_all_files_vs_con was set to True but no user gate-widths were provided. Check gatewidth_list and ensure it is as intended.')



# function used for user-specified lifetimes (similar to log_one in FeynmanYAnalysis)
def log_one_user(tau_b, a):
    return a * (1 - ((1 - np.exp(-tau_b)) / (tau_b)))

plot_all_files_vs_con_gatewidth_list = gatewidth_list

if plot_histograms == True or plot_individual_files == True or plot_all_files_vs_gw == True or plot_all_files_vs_con == True or plot_channels == True or perform_Rossi == True or read_header == True:
    os.chdir(filepath)
    # outer loop over each of the files
    for i in range(0,len(files)):
        
        # current filename
        current_file = files[i]
        
        file_number.append(i+1)
        
        # establish file descriptions
        if len(file_descriptions) > 0:
            current_file_description = file_descriptions[i]
        else:
            current_file_description = None
        
        print('#################################################')
        
        if len(file_descriptions) > 0:
            print('File: ',current_file,'. Description: ',current_file_description,'. File number ',i+1,' of ',len(files))
        else:
            print('File: ',current_file,'. File number ',i+1,' of ',len(files))
        
        # this reads in header information
        if read_header == True:
            if input_type == '.lmx':
                # See Dec 2022 emails. There is currently an issue in readLMXFile, so readLMXFile_old is being used instead
                #lmxfile = readLMXFile(current_file)
                lmxfile = readLMXFile_old(current_file)
                header_tick_length, header_measurement_time, header_count_rate, header_SD, header_RD, header_FIFO, header_RR12, header_RR13, header_RR23 = print_header(lmxfile)
                header_measurement_time_all_files.append(header_measurement_time)
                if type(header_FIFO) == int and header_FIFO > 0:
                    if exit_on_FIFO == True:
                        sys.exit('Exit: the .lmx file ',current_file,' contains ',header_FIFO,' FIFO losses. Since exit_on_FIFO is set to True, the script has stopped.')
                    else:
                        print('WARNING: the .lmx file ',current_file,' contains ',header_FIFO,' FIFO losses.')
        else:
            header_measurement_time = 0
        
        # this plots the counts in each channel if set to True by the user
        if plot_channels == True:
            
            if input_type == '.lmx':
            
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Channels/', '', current_file, add_current_file=True, make_dirs=True)
                # See Dec 2022 emails. There is currently an issue in readLMXFile, so readLMXFile_old is being used instead
                #detector_ct_file = readLMXFile(current_file)
                detector_ct_file = readLMXFile_old(current_file)
                channel_plot(detector_ct_file,current_save_path, use_title, title_prefix)
                
            else: 
                print('Currently plot_channels is only support for input_type = .lmx')
        
        
        if input_type == '.lmx':
        
            # gets every event in the file and puts in a list
            events_list = []
            [events_list.extend(eventsFromLMX(current_file))]
            
            # splits that list by time and channel
            time_list = [event.time for event in events_list]
            channel_list = [event.detector for event in events_list]
            
            # this plots time vs number of events if set to True by the user
            if plot_time_vs_events == True:
                
                # start here 12/11/22. still troubleshooting this
                # need to zoom in and only take in 100 events at a time or so
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/TimeVsEvents/', '', current_file, add_current_file=True, make_dirs=True)
                plot_time(time_list,current_save_path)
            
            # this outputs a csv file with all events if set to True by the user
            if output_event_csv == True:        
        
                with open(save_path+current_file+'_time_list.csv', mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    for current_time in time_list:
                        writer.writerow([current_time])
                        
                with open(save_path+current_file+'_event_list.csv', mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    for i in range(0,len(time_list)):
                        current_time = time_list[i]
                        current_channel = channel_list[i]
                        writer.writerow([current_time,current_channel])
            
            
            # this runs the FeynmanHistogramCalculator
            if plot_histograms == True or plot_individual_files == True or plot_all_files_vs_gw == True or plot_all_files_vs_con == True or perform_Y2_single_fit == True or perform_Y2_double_fit == True:
                binning = SequentialBinning()
                feynman_calculator = FeynmanHistogramCalculator(events_list, binning=binning)
                print('Feynman Calculator Complete')
                print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
        
        # create empty lists that include data from a single file only
        histogram_x_list, histogram_y_list, histogram_P_list, first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list, first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list, single_feynman_mean_list, single_feynman_variance_list, single_variance_to_mean_list, Y1_list, dY1_list,  R1_list, dR1_list, dR1R2_list, Y2_list, dY2_list, Ym_list, dYm_list, calc_eff_kn_list, calc_eff_unc_kn_list, Rossi_times_list, Rossi_data_list, histogram_x_sum_list, histogram_y_sum_list, histogram_P_sum_list = ([] for i in range(30))
        
        # summary information and plots for each individual file
        if plot_individual_files == True or perform_Y2_single_fit == True or perform_Y2_double_fit == True:
            print('Plotting individual files start for file ',current_file)
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Rates/', '', current_file, add_current_file=True, make_dirs=True)
                
        # goes through and collects info for each individual gate 
        if plot_histograms == True or plot_individual_files == True or plot_all_files_vs_gw == True or plot_all_files_vs_con == True or perform_Y2_single_fit == True or perform_Y2_double_fit == True:
            print('Gate loop start')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))      
    
            if input_type == '.xml':
                # this will get various parameters from the xml file
                user_gatewidth_list = gatewidth_list
                gatewidth_list, feynman_data = readXML(current_file, xml_user_gatewidths, gatewidth_list)
                if xml_user_gatewidths == True:
                    for gatewidth in user_gatewidth_list:
                        if gatewidth not in gatewidth_list:
                            print('Note: xml_user_gatewidths was set to true, but the user-specified gatewidth ',gatewidth,' is not in the xml file. It cannot therefore be analyzed.')
                                                     
            for gatewidth in gatewidth_list:
                if input_type == '.lmx':
                    print('Gate-width = ',gatewidth)
                    # this gets various parameters for the specified file and gatewidth
                    single_feynman_histogram = feynman_calculator.calculate(gatewidth)
                    first_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(1)
                    first_reduced_factorial_moment_list.append(first_reduced_factorial_moment)
                    second_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(2)
                    second_reduced_factorial_moment_list.append(second_reduced_factorial_moment)
                    third_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(3)
                    third_reduced_factorial_moment_list.append(third_reduced_factorial_moment)
                    fourth_reduced_factorial_moment = single_feynman_histogram.reduced_factorial_moment(4)
                    fourth_reduced_factorial_moment_list.append(fourth_reduced_factorial_moment)
                    first_factorial_moment = single_feynman_histogram.factorial_moment(1)
                    first_factorial_moment_list.append(first_factorial_moment)
                    second_factorial_moment = single_feynman_histogram.factorial_moment(2)
                    second_factorial_moment_list.append(second_factorial_moment)
                    third_factorial_moment = single_feynman_histogram.factorial_moment(3)
                    third_factorial_moment_list.append(third_factorial_moment)
                    fourth_factorial_moment = single_feynman_histogram.factorial_moment(4)   
                    fourth_factorial_moment_list.append(fourth_factorial_moment)
                    
                    single_feynman_mean = single_feynman_histogram.mean
                    single_feynman_mean_list.append(single_feynman_mean)
                    single_feynman_variance = single_feynman_histogram.variance
                    single_feynman_variance_list.append(single_feynman_variance)
                    single_variance_to_mean = single_feynman_histogram.variance_to_mean
                    single_variance_to_mean_list.append(single_variance_to_mean)
                
                    Y1, dY1 = single_feynman_histogram.Y1
                    R1 = Y1
                    dR1 = dY1
                    Y1_list.append(Y1)
                    R1_list.append(R1)
                    dY1_list.append(dY1)
                    dR1_list.append(dR1)
                    Y2, dY2 = single_feynman_histogram.Y2
                    Y2_list.append(Y2)
                    dY2_list.append(dY2)
                    # Equation 18
                    Ym = ((second_factorial_moment-first_factorial_moment**2)/first_factorial_moment)-1
                    Ym_list.append(Ym)
                    # Equation 60 of LA-UR-15-21365
                    N = sum(single_feynman_histogram.frequency)
                    inside_numerator = (2*second_factorial_moment**2/first_factorial_moment**2)+(second_factorial_moment**3/first_factorial_moment**4)+second_factorial_moment-first_factorial_moment**2+(fourth_factorial_moment/first_factorial_moment**2)-(2*second_factorial_moment*third_factorial_moment)/first_factorial_moment**3-2*third_factorial_moment/first_factorial_moment
                    if inside_numerator > 0:
                        dYm = (inside_numerator/(N-1))**0.5
                    else:
                        dYm.append(0)
                        print('Note: dYm was requiring a negative square root. dYm has been set to 0 (but it is not correct).')
                    dYm_list.append(dYm)
                
                    # this will plot Feynman histograms for the specified file and gatewidth if set to True by the user
                    if plot_histograms == True or sum_Feynman_histograms == True:
                        
                        current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Histograms/', 'Histogram_', current_file, add_current_file=True, make_dirs=True)
                        if (plot_histograms == True and sum_Feynman_histograms != True) or (plot_histograms == True and sum_Feynman_histograms == True and plot_sum_and_individual_histogram == True):
                            single_feynman_figure, single_feynman_axis, x, y, distribution = single_feynman_histogram.plotHistogram(poisson=True, show=False, limit_step=True, save=current_save_path, log=True, xmin=False, xmax=False, ymin=False, ymax=False, normalize=histogram_normalize, title=str(gatewidth)+' nsec')
                        else:
                            single_feynman_figure, single_feynman_axis, x, y, distribution = single_feynman_histogram.plotHistogram(poisson=True, show=False, limit_step=True, save=False, log=True, xmin=False, xmax=False, ymin=False, ymax=False, normalize=histogram_normalize, title=str(gatewidth)+' nsec')
                        histogram_x_list.append(x)
                        histogram_y_list.append(y)
                        histogram_P_list.append(distribution)
                        if histogram_normalize == True:
                            y_normalize_no_zero = [[ele for ele in sub if ele != 0] for sub in histogram_y_list]
            
            if input_type == '.xml':
                
                first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list, n_list = reduced_factorial_moments(feynman_data)
                first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list = factorial_moments(feynman_data)
                single_feynman_mean_list = first_factorial_moment_list
                single_feynman_variance_list = second_factorial_moment_list
                single_variance_to_mean_list = feynman_histogram_v2m(single_feynman_mean_list,single_feynman_variance_list)
                gate_width_sec = [entry*1e-9 for entry in gatewidth_list]
                Y1_list, dY1_list, Y2_list, dY2_list = excess_variance_reduced(gate_width_sec, feynman_data, first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list)
                R1_list = Y1_list
                dR1_list = dY1_list
                Ym_list, dYm_list = excess_variance(gate_width_sec, feynman_data, first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list)
                            
                # this will plot Feynman histograms for the specified file and gatewidth if set to True by the user
                if plot_histograms == True or sum_Feynman_histograms == True:
                    
                    current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Histograms/', 'Histogram_', current_file, add_current_file=True, make_dirs=True)
                    for l in range(0,len(gatewidth_list)):
                        current_gatewidth = gatewidth_list[l]
                        print('Gate-width = ',current_gatewidth)
                        current_x = n_list[l]
                        current_y = feynman_data[l]
                        if histogram_normalize == True:
                            current_P = poissiondist.pmf(current_x, first_factorial_moment_list[l])
                        else:
                            current_P = sum(current_y)*poissiondist.pmf(current_x, first_factorial_moment_list[l])
                        if (plot_histograms == True and sum_Feynman_histograms != True) or (plot_histograms == True and sum_Feynman_histograms == True and plot_sum_and_individual_histogram == True):
                            plotHistogram_single(current_gatewidth, current_x, current_y, current_P, show=False, limit_step=True, save=current_save_path+str(current_gatewidth), log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
                        else:
                            plotHistogram_single(current_gatewidth, current_x, current_y, current_P, show=False, limit_step=True, save=False, log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
                        histogram_x_list.append(current_x)
                        histogram_y_list.append(current_y)
                        histogram_P_list.append(current_P)
            
            # this gets the total number of events
            total_events(gatewidth_list,histogram_x_list,histogram_y_list)
            
            # this runs the FeynmanYAnalysis.py script and extracts desired parameters
            if input_type == '.lmx':
                feynman_analysis = FeynmanYAnalysis()
                feynman_analysis.makeHistograms(FeynmanHistogramCalculator(events_list), gates_list=gatewidth_list)
                Y1_distribution = feynman_analysis.Y1Distribution()
                R1_distribution_value = Y1_distribution_value = Y1_distribution[0]
                R1_distribution_unc = Y1_distribution_unc = Y1_distribution[1]
                Y2_distribution = feynman_analysis.Y2Distribution()
                Y2_distribution_value = Y2_distribution[0]
                Y2_distribution_unc = Y2_distribution[1]
            elif input_type == '.xml':
                R1_distribution_value = Y1_distribution_value = tuple(Y1_list)
                R1_distribution_unc = Y1_distribution_unc = tuple(dY1_list)
                Y1_distribution = (Y1_distribution_value,Y1_distribution_unc)
                Y2_distribution_value = tuple(Y2_list)
                Y2_distribution_unc = tuple(dY2_list)
                Y2_distribution = (Y2_distribution_value,Y2_distribution_unc)
            
            if input_type != '.csv': 
                if (perform_Y2_single_fit == True or perform_Y2_double_fit == True) and len(gatewidth_list) < 6:
                    sys.exit('Exit: at least 6 gate-widths are required to peform a single Y2 fit.')
            
            # Y2 single log fit
            if input_type == '.lmx' or input_type == '.xml':
                if perform_Y2_single_fit == True:
                    if input_type == '.lmx':
                        fit1log = feynman_analysis.fit1Log()
                    elif input_type == '.xml':
                        fit1log = fit1Log_xml(gatewidth_list, Y2_distribution_value, Y2_distribution_unc, guess=None)
                    fit1log_temp = fit1log[0]
                    fit1log_A = fit1log_temp[0]
                    fit1log_B = fit1log_temp[1]
                    fit1log_det_lifetime = 1/fit1log_B
                    fit1log_temp = fit1log[1]
                    fit1log_temp2 = fit1log_temp[0]
                    fit1log_A_unc = np.sqrt(fit1log_temp2[0])
                    fit1log_temp2 = fit1log_temp[1]
                    fit1log_B_unc = np.sqrt(fit1log_temp2[1])
                    fit1log_det_lifetime_unc = fit1log_det_lifetime*fit1log_B_unc/fit1log_B
                    print('Fit with 1 log. A = ',fit1log_A,' +/- ',fit1log_A_unc,'. B = ',fit1log_B,' +/- ',fit1log_B_unc,'. lifetime (1/B) = ',fit1log_det_lifetime,' +/- ',fit1log_det_lifetime_unc)
                    fit_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                    fit1_detailed_dis = []
                    for fit_gatewidth in fit_gatewidths:
                        fit1_detailed_dis.append(fit1log_A * (1 - (1 - np.exp(-fit1log_B * fit_gatewidth)) / (fit1log_B* fit_gatewidth)))
                    fit1_results = []
                    fit1_results.append(fit_gatewidths)
                    fit1_results.append(fit1_detailed_dis)
                    if input_type == '.lmx':
                        fit1LogDistribution = feynman_analysis.fit1LogDistribution()
                    elif input_type == '.xml':  
                        fit1LogDistribution = []
                        for gatewidth in gatewidth_list:
                            fit1LogDistribution.append(log_one(gatewidth, fit1log_A, fit1log_B))
                    omega2_single_results = omega2_single(fit1log_B,gatewidth_list)
                    R2_single_Y2_decay = R2_calc_rate(Y2_distribution_value,omega2_single_results)
                    R2_unc_single_Y2_decay = R2_unc_calc(gatewidth_list,R2_single_Y2_decay, omega2_single_results, Y2_distribution_unc, fit1log_B, fit1log_B_unc)
                    
                # Y2 double log fit    
                if perform_Y2_double_fit == True:
                    perform_Y2_double_fit_continue = True
                    if input_type == '.lmx':
                        fit2log = feynman_analysis.fit2Log(guess=[fit1log_A,fit1log_B,fit1log_A,fit1log_B])
                    elif input_type == '.xml':
                        fit2log = fit2Log_xml(gatewidth_list, Y2_distribution_value, Y2_distribution_unc, guess=None)
                    fit2log_temp = fit2log[0]
                    fit2log_A = fit2log_temp[0]
                    fit2log_B = fit2log_temp[1]
                    fit2log_C = fit2log_temp[2]
                    fit2log_D = fit2log_temp[3]
                    fit2log_det_lifetime1 = 1/fit2log_B
                    fit2log_det_lifetime2 = 1/fit2log_D
                    fit2log_amp = fit2log_A+fit2log_C
                    fit2logA_percent = fit2log_A/(fit2log_A+fit2log_C)
                    fit2logC_percent = fit2log_C/(fit2log_A+fit2log_C)
                    
                    if np.abs(fit2log_D/fit2log_B) >= 0.99 and np.abs(fit2log_D/fit2log_B) <= 1.01:
                        print('A double Y2 fit is not appropriate as it results in the same values for both parameters. A double fit will not be plotted/used.')
                        print('Fit with 2 log. A = ',fit2log_A,'. B = ',fit2log_B,'. C = ',fit2log_C,'. D = ',fit2log_D,'. lifetime1 (1/B) = ',fit2log_det_lifetime1,'. lifetime2 (1/D) = ',fit2log_det_lifetime2)
                        omega2_double1_results = R2_double1_Y2_decay = R2_unc_double1_Y2_decay = omega2_double2_results = R2_double2_Y2_decay = R2_unc_double2_Y2_decay = ['N/A' for entry in gatewidth_list]
                        perform_Y2_double_fit_continue = False
                    if perform_Y2_double_fit_continue == True:    
                        fit2log_temp = fit2log[1]
                        fit2log_temp2 = fit2log_temp[0]
                        fit2log_A_unc = np.sqrt(fit2log_temp2[0])
                        fit2log_temp2 = fit2log_temp[1]
                        fit2log_B_unc = np.sqrt(fit2log_temp2[1])
                        # Note there is NOT a sqrt here. I think that is correct. See: https://en.wikipedia.org/wiki/Propagation_of_uncertainty
                        fit2log_B_D = fit2log_temp2[3]
                        fit2log_temp2 = fit2log_temp[2]
                        fit2log_C_unc = np.sqrt(fit2log_temp2[2])
                        fit2log_temp2 = fit2log_temp[3]
                        fit2log_D_unc = np.sqrt(fit2log_temp2[3])
                        fit2log_det_lifetime1_unc = fit2log_det_lifetime1*fit2log_B_unc/fit2log_B
                        fit2log_det_lifetime2_unc = fit2log_det_lifetime2*fit2log_D_unc/fit2log_D
                        
                        # forces B to be > D. if it is not, then A and C are swapped (and B and D are swapped)
                        if fit2log_B < fit2log_D:
                            print('Switching first and second terms from fit to force B to be > D.')
                            temp = fit2log_A
                            temp2 = fit2log_C
                            fit2log_A = temp2
                            fit2log_C = temp
                            temp = fit2logA_percent
                            temp2 = fit2logC_percent
                            fit2logA_percent = temp2
                            fit2logC_percent = temp
                            temp = fit2log_A_unc
                            temp2 = fit2log_C_unc
                            fit2log_A_unc = temp2
                            fit2log_C_unc = temp
                            temp = fit2log_B
                            temp2 = fit2log_D
                            fit2log_B = temp2
                            fit2log_D = temp
                            temp = fit2log_B_unc
                            temp2 = fit2log_D_unc
                            fit2log_B_unc = temp2
                            fit2log_D_unc = temp
                            temp = fit2log_det_lifetime1
                            temp2 = fit2log_det_lifetime2
                            fit2log_det_lifetime1 = temp2
                            fit2log_det_lifetime2 = temp
                            temp = fit2log_det_lifetime1_unc
                            temp2 = fit2log_det_lifetime2_unc
                            fit2log_det_lifetime1_unc = temp2
                            fit2log_det_lifetime2_unc = temp
                        
                        print('Fit with 2 log. A = ',fit2log_A,' +/- ',fit2log_A_unc,'. B = ',fit2log_B,' +/- ',fit2log_B_unc,'. C = ',fit2log_C,' +/- ',fit2log_C_unc,'. D = ',fit2log_D,' +/- ',fit2log_D_unc,'. lifetime1 (1/B) = ',fit2log_det_lifetime1,' +/- ',fit2log_det_lifetime1_unc,'. lifetime2 (1/D) = ',fit2log_det_lifetime2,' +/- ',fit2log_det_lifetime2_unc)
                        fit2_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                        fit2_detailed_dis = []
                        for fit2_gatewidth in fit2_gatewidths:
                            fit2_detailed_dis.append((fit2log_A * (1 - (1 - np.exp(-fit2log_B * fit2_gatewidth)) / (fit2log_B* fit2_gatewidth)))+(fit2log_C * (1 - (1 - np.exp(-fit2log_D * fit2_gatewidth)) / (fit2log_D* fit2_gatewidth))))
                        fit2_results = []
                        fit2_results.append(fit2_gatewidths)
                        fit2_results.append(fit2_detailed_dis)
                        if input_type == '.lmx':
                            fit2LogDistribution = feynman_analysis.fit2LogDistribution()
                        elif input_type == '.xml':  
                            fit2LogDistribution = []
                            for gatewidth in gatewidth_list:
                                fit2LogDistribution.append(log_two(gatewidth, fit2log_A, fit2log_B, fit2log_C, fit2log_D))
                        omega2_double1_results = omega2_single(fit2log_B,gatewidth_list)
                        R2_double1_Y2_decay = R2_calc_rate(Y2_distribution_value,omega2_double1_results)
                        R2_unc_double1_Y2_decay = R2_unc_calc(gatewidth_list,R2_double1_Y2_decay, omega2_double1_results, Y2_distribution_unc, fit2log_B, fit2log_B_unc)
                        omega2_double2_results = omega2_single(fit2log_D,gatewidth_list)
                        R2_double2_Y2_decay = R2_calc_rate(Y2_distribution_value,omega2_double2_results)
                        R2_unc_double2_Y2_decay = R2_unc_calc(gatewidth_list,R2_double2_Y2_decay, omega2_double2_results, Y2_distribution_unc, fit2log_D, fit2log_D_unc)
                        # This uses both terms, see unc equation in EUCLID subcritical paper
                        omega2_double_both_results = omega2_double(fit2logA_percent,fit2log_B,fit2logC_percent,fit2log_D,gatewidth_list)
                        R2_double_both_Y2_decay = R2_calc_rate(Y2_distribution_value,omega2_double_both_results)
                        R2_unc_double_both_Y2_decay = R2_double_unc_calc(gatewidth_list,R2_double_both_Y2_decay, omega2_double_both_results, Y2_distribution_unc, fit2logA_percent, fit2log_B, fit2log_B_unc, fit2logC_percent, fit2log_D, fit2log_D_unc, fit2log_B_D)
                        # in the future could these be combined similar to Michael Hua's work?    
            
            # User-specified lifetime
            if input_type == '.lmx' or input_type == '.xml':
                if use_user_specified_lifetime == True:
                    
                    gate_width_sec = [entry*1e-9 for entry in gatewidth_list]
                    gate_width_sec_b = [entry*1e-9/user_lifetime for entry in gatewidth_list]
            
                    user_fit_results = curve_fit(log_one_user, gate_width_sec_b, Y2_list, method="lm")
                    temp = user_fit_results[0]
                    user_A = temp[0]
                    temp = user_fit_results[1]
                    temp = temp[0]
                    user_A_unc = np.sqrt(temp[0])
            
                    print('Fit with user-specified lifetime. A = ',user_A,' +/- ',user_A_unc,'. lifetime (1/B) = ',user_lifetime,' +/- ',user_lifetime_unc)
                    fit_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                    fit_gatewidths_b = [entry*1e-9/user_lifetime for entry in fit_gatewidths]
                    
                    fit_Y2 = []
                    for gate in fit_gatewidths_b:
                        fit_Y2.append(log_one_user(gate, user_A))
                    
                    fit_lifetime_user_results = []
                    fit_lifetime_user_results.append(fit_gatewidths)
                    fit_lifetime_user_results.append(fit_Y2)
                    omega2_lifetime_user_results = omega2_single(1/user_lifetime,gate_width_sec)
                    R2_user_lifetime = R2_calc_rate(Y2_distribution_value,omega2_lifetime_user_results)
                    R2_unc_user_lifetime = R2_unc_calc(gatewidth_list,R2_user_lifetime, omega2_lifetime_user_results, Y2_distribution_unc, 1/user_lifetime, user_lifetime_unc/user_lifetime**2)
            
            
            # plots from FeynmanYAnalysis.py
            if plot_individual_files == True:      
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Rates/', 'FeynmanYan_Y2_', current_file, add_current_file=True, make_dirs=False)
                if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                    if input_type == '.lmx':
                        feynman_analysis.plotY2(fits=True,show=False,save=current_save_path)
                    elif input_type == '.xml':  
                        plotY2_xml(gatewidth_list, Y2_distribution_value, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, residuals=False, gaussianBins=50, show=False, save=current_save_path)
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Rates/', 'FeynmanYan_Y2_residuals_', current_file, add_current_file=True, make_dirs=False)
                if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                    if input_type == '.lmx':
                        feynman_analysis.plotResiduals(show=False,save=current_save_path)
                    elif input_type == '.xml':  
                        plotResiduals_xml(gatewidth_list, Y2_distribution_value, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, gaussianBins=100, show=False, save=current_save_path)
        
            if input_type == '.lmx' or input_type == '.xml':
                # calculates efficiency for Cf252 data
                if calculation_type == 'Cf':
                    calc_eff_kn_list, calc_eff_unc_kn_list = eff_from_Cf(gatewidth_list, Y1_list, dY1_list, nuS1_Cf252, Cf252_Fs, Cf252_dFs)
                 # calculates multiplication parameters
                elif calculation_type == 'Multiplicity':
                    # will revisit this in the future, currently cov between R1 and R2 is set to 0
                    dR1R2_list = [0 for i in range(0,len(gatewidth_list))]
                    if perform_Y2_single_fit == True:
                        Ml_list_Y2_single, a1_list_Y2_single, a2_list_Y2_single, a3_list_Y2_single, a4_list_Y2_single = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_single_Y2_decay, eff)
                        dMl_list_Y2_single, dMldR1_list_Y2_single, dMldR2_list_Y2_single, dMldeff_list_Y2_single = calc_dMl(gatewidth_list, a3_list_Y2_single, a4_list_Y2_single, R1_list, dR1_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, dR1R2_list, eff, deff)
                        Fs_list_Y2_single, a5_list_Y2_single, a6_list_Y2_single, a7_list_Y2_single = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_single_Y2_decay, eff)
                        dFs_list_Y2_single, dFsdR1_list_Y2_single, dFsdR2_list_Y2_single, dFsdeff_list_Y2_single = calc_dFs(gatewidth_list, a5_list_Y2_single, a6_list_Y2_single, a7_list_Y2_single, R1_list, dR1_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, dR1R2_list, eff, deff)
                        Mt_list_Y2_single = calc_Mt(gatewidth_list, Ml_list_Y2_single, nuI1, alpha)
                        dMt_list_Y2_single = calc_dMt(gatewidth_list, nuI1, alpha, dMl_list_Y2_single)
                        kp_list_Y2_single = calc_kp(gatewidth_list, Mt_list_Y2_single)
                        dkp_list_Y2_single = calc_dkp(gatewidth_list, Mt_list_Y2_single, dMt_list_Y2_single)
                        keff_list_Y2_single = calc_keff(gatewidth_list, kp_list_Y2_single, beta_eff)
                        dkeff_list_Y2_single = calc_dkeff(gatewidth_list, dkp_list_Y2_single, beta_eff)
                    if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                        Ml_list_Y2_double1, a1_list_Y2_double1, a2_list_Y2_double1, a3_list_Y2_double1, a4_list_Y2_double1 = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_double1_Y2_decay, eff)
                        dMl_list_Y2_double1, dMldR1_list_Y2_double1, dMldR2_list_Y2_double1, dMldeff_list_Y2_double1 = calc_dMl(gatewidth_list, a3_list_Y2_double1, a4_list_Y2_double1, R1_list, dR1_list, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, dR1R2_list, eff, deff)
                        Fs_list_Y2_double1, a5_list_Y2_double1, a6_list_Y2_double1, a7_list_Y2_double1 = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_double1_Y2_decay, eff)
                        dFs_list_Y2_double1, dFsdR1_list_Y2_double1, dFsdR2_list_Y2_double1, dFsdeff_list_Y2_double1 = calc_dFs(gatewidth_list, a5_list_Y2_double1, a6_list_Y2_double1, a7_list_Y2_double1, R1_list, dR1_list, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, dR1R2_list, eff, deff)
                        Mt_list_Y2_double1 = calc_Mt(gatewidth_list, Ml_list_Y2_double1, nuI1, alpha)
                        dMt_list_Y2_double1 = calc_dMt(gatewidth_list, nuI1, alpha, dMl_list_Y2_double1)
                        kp_list_Y2_double1 = calc_kp(gatewidth_list, Mt_list_Y2_double1)
                        dkp_list_Y2_double1 = calc_dkp(gatewidth_list, Mt_list_Y2_double1, dMt_list_Y2_double1)
                        keff_list_Y2_double1 = calc_keff(gatewidth_list, kp_list_Y2_double1, beta_eff)
                        dkeff_list_Y2_double1 = calc_dkeff(gatewidth_list, dkp_list_Y2_double1, beta_eff)
                        Ml_list_Y2_double2, a1_list_Y2_double2, a2_list_Y2_double2, a3_list_Y2_double2, a4_list_Y2_double2 = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_double2_Y2_decay, eff)
                        dMl_list_Y2_double2, dMldR1_list_Y2_double2, dMldR2_list_Y2_double2, dMldeff_list_Y2_double2 = calc_dMl(gatewidth_list, a3_list_Y2_double2, a4_list_Y2_double2, R1_list, dR1_list, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, dR1R2_list, eff, deff)
                        Fs_list_Y2_double2, a5_list_Y2_double2, a6_list_Y2_double2, a7_list_Y2_double2 = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_double2_Y2_decay, eff)
                        dFs_list_Y2_double2, dFsdR1_list_Y2_double2, dFsdR2_list_Y2_double2, dFsdeff_list_Y2_double2 = calc_dFs(gatewidth_list, a5_list_Y2_double2, a6_list_Y2_double2, a7_list_Y2_double2, R1_list, dR1_list, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, dR1R2_list, eff, deff)
                        Mt_list_Y2_double2 = calc_Mt(gatewidth_list, Ml_list_Y2_double2, nuI1, alpha)
                        dMt_list_Y2_double2 = calc_dMt(gatewidth_list, nuI1, alpha, dMl_list_Y2_double2)
                        kp_list_Y2_double2 = calc_kp(gatewidth_list, Mt_list_Y2_double2)
                        dkp_list_Y2_double2 = calc_dkp(gatewidth_list, Mt_list_Y2_double2, dMt_list_Y2_double2)
                        keff_list_Y2_double2 = calc_keff(gatewidth_list, kp_list_Y2_double2, beta_eff)
                        dkeff_list_Y2_double2 = calc_dkeff(gatewidth_list, dkp_list_Y2_double2, beta_eff)
                        Ml_list_Y2_double_both, a1_list_Y2_double_both, a2_list_Y2_double_both, a3_list_Y2_double_both, a4_list_Y2_double_both = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_double_both_Y2_decay, eff)
                        dMl_list_Y2_double_both, dMldR1_list_Y2_double_both, dMldR2_list_Y2_double_both, dMldeff_list_Y2_double_both = calc_dMl(gatewidth_list, a3_list_Y2_double_both, a4_list_Y2_double_both, R1_list, dR1_list, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, dR1R2_list, eff, deff)
                        Fs_list_Y2_double_both, a5_list_Y2_double_both, a6_list_Y2_double_both, a7_list_Y2_double_both = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_double_both_Y2_decay, eff)
                        dFs_list_Y2_double_both, dFsdR1_list_Y2_double_both, dFsdR2_list_Y2_double_both, dFsdeff_list_Y2_double_both = calc_dFs(gatewidth_list, a5_list_Y2_double_both, a6_list_Y2_double_both, a7_list_Y2_double_both, R1_list, dR1_list, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, dR1R2_list, eff, deff)
                        Mt_list_Y2_double_both = calc_Mt(gatewidth_list, Ml_list_Y2_double_both, nuI1, alpha)
                        dMt_list_Y2_double_both = calc_dMt(gatewidth_list, nuI1, alpha, dMl_list_Y2_double_both)
                        kp_list_Y2_double_both = calc_kp(gatewidth_list, Mt_list_Y2_double_both)
                        dkp_list_Y2_double_both = calc_dkp(gatewidth_list, Mt_list_Y2_double_both, dMt_list_Y2_double_both)
                        keff_list_Y2_double_both = calc_keff(gatewidth_list, kp_list_Y2_double_both, beta_eff)
                        dkeff_list_Y2_double_both = calc_dkeff(gatewidth_list, dkp_list_Y2_double_both, beta_eff)
                    if use_user_specified_lifetime == True:
                        Ml_list_Y2_user_lifetime, a1_list_Y2_user_lifetime, a2_list_Y2_user_lifetime, a3_list_Y2_user_lifetime, a4_list_Y2_user_lifetime = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_user_lifetime_Y2_decay, eff)
                        dMl_list_Y2_user_lifetime, dMldR1_list_Y2_user_lifetime, dMldR2_list_Y2_user_lifetime, dMldeff_list_Y2_user_lifetime = calc_dMl(gatewidth_list, a3_list_Y2_user_lifetime, a4_list_Y2_user_lifetime, R1_list, dR1_list, R2_user_lifetime_Y2_decay, R2_unc_user_lifetime_Y2_decay, dR1R2_list, eff, deff)
                        Fs_list_Y2_user_lifetime, a5_list_Y2_user_lifetime, a6_list_Y2_user_lifetime, a7_list_Y2_user_lifetime = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_list, R2_user_lifetime_Y2_decay, eff)
                        dFs_list_Y2_user_lifetime, dFsdR1_list_Y2_user_lifetime, dFsdR2_list_Y2_user_lifetime, dFsdeff_list_Y2_user_lifetime = calc_dFs(gatewidth_list, a5_list_Y2_user_lifetime, a6_list_Y2_user_lifetime, a7_list_Y2_user_lifetime, R1_list, dR1_list, R2_user_lifetime_Y2_decay, R2_unc_user_lifetime_Y2_decay, dR1R2_list, eff, deff)
                        Mt_list_Y2_user_lifetime = calc_Mt(gatewidth_list, Ml_list_Y2_user_lifetime, nuI1, alpha)
                        dMt_list_Y2_user_lifetime = calc_dMt(gatewidth_list, nuI1, alpha, dMl_list_Y2_user_lifetime)
                        kp_list_Y2_user_lifetime = calc_kp(gatewidth_list, Mt_list_Y2_user_lifetime)
                        dkp_list_Y2_user_lifetime = calc_dkp(gatewidth_list, Mt_list_Y2_user_lifetime, dMt_list_Y2_user_lifetime)
                        keff_list_Y2_user_lifetime = calc_keff(gatewidth_list, kp_list_Y2_user_lifetime, beta_eff)
                        dkeff_list_Y2_user_lifetime = calc_dkeff(gatewidth_list, dkp_list_Y2_user_lifetime, beta_eff)
        
        # perform Rossi-alpha analysis
        if perform_Rossi == True:
            
            print('Rossi calculator start.')
            
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Rossi/', '', current_file, add_current_file=True, make_dirs=True)
            
            binning = RossiBinningTypeI()  # Type I,II, III and TimeIntervalAnalysis binning methods included in RossiBinning
            rossi_calculator = RossiHistogramCalculator(event_list=events_list, binning=binning)
            raw_histogram = rossi_calculator.calculate(reset_time=Rossi_reset_time, bin_num=Rossi_bin_num)
            rossi_figure, rossi_axis = Plot(raw_histogram, fits=perform_Rossi_fits, residuals=perform_Rossi_fits, res_bins=Rossi_bin_num, show=False, save=current_save_path)
            Rossi_times_list = raw_histogram.bins
            Rossi_data_list = raw_histogram.frequency
            fit1, fit2 = raw_histogram.FitDistributions()
            # fit values for 1 exp
            one_exp_alpha, one_exp_sigma = raw_histogram.calculate1exp()
            Rossi_1exp_A = one_exp_alpha[0]
            Rossi_1exp_B = one_exp_alpha[1]
            Rossi_1exp_C = one_exp_alpha[2]
            fit1exp_temp = one_exp_sigma[0]
            Rossi_1exp_A_unc = np.sqrt(fit1exp_temp[0])
            fit1exp_temp = one_exp_sigma[1]
            Rossi_1exp_B_unc = np.sqrt(fit1exp_temp[1])
            fit1exp_temp = one_exp_sigma[2]
            Rossi_1exp_C_unc = np.sqrt(fit1exp_temp[2])
            print('Rossi fit with 1 exp. A*exp(-Bx) + C. A = ',Rossi_1exp_A,' +/- ',Rossi_1exp_A_unc,'. B(alpha) = ',Rossi_1exp_B,' +/- ',Rossi_1exp_B_unc,'. C = ',Rossi_1exp_C,' +/- ',Rossi_1exp_C_unc,'. 1/B = ',1/Rossi_1exp_B,' +/- ',Rossi_1exp_B_unc/Rossi_1exp_B**2)
            # fit values for 2 exp
            two_exp_alpha, two_exp_sigma = raw_histogram.calculate2exp()
            Rossi_2exp_A = two_exp_alpha[0]
            Rossi_2exp_B = two_exp_alpha[1]
            Rossi_2exp_C = two_exp_alpha[2]
            Rossi_2exp_D = two_exp_alpha[3]
            Rossi_2exp_E = two_exp_alpha[4]
            fit2exp_temp = two_exp_sigma[0]
            Rossi_2exp_A_unc = np.sqrt(fit2exp_temp[0])
            fit2exp_temp = two_exp_sigma[1]
            Rossi_2exp_B_unc = np.sqrt(fit2exp_temp[1])
            fit2exp_temp = two_exp_sigma[2]
            Rossi_2exp_C_unc = np.sqrt(fit2exp_temp[2])
            fit2exp_temp = two_exp_sigma[3]
            Rossi_2exp_D_unc = np.sqrt(fit2exp_temp[3])
            fit2exp_temp = two_exp_sigma[4]
            Rossi_2exp_E_unc = np.sqrt(fit2exp_temp[4])
            
            # forces B to be < D. If it is not, then B and D are swapped (A and C are also swapped)
            if Rossi_2exp_B < Rossi_2exp_D:
                print('Rossi fit with 2 exp. A*exp(-Bx) + C*exp(-Dx) + E. A = ',Rossi_2exp_A,' +/- ',Rossi_2exp_A_unc,'. B(alpha1) = ',Rossi_2exp_B,' +/- ',Rossi_2exp_B_unc,'. C = ',Rossi_2exp_C,' +/- ',Rossi_2exp_C_unc,'. D(alpha2) = ',Rossi_2exp_D,' +/- ',Rossi_2exp_D_unc,'. E = ',Rossi_2exp_E,' +/- ',Rossi_2exp_E_unc,'. 1/B = ',1/Rossi_2exp_B,' +/- ',Rossi_2exp_B_unc/Rossi_2exp_B**2,'. 1/D = ',1/Rossi_2exp_D,' +/- ',Rossi_2exp_D_unc/Rossi_2exp_D**2) 
                print('Switching first and second terms from fit to force B to be > D.')
                temp = Rossi_2exp_A
                temp2 = Rossi_2exp_C
                Rossi_2exp_A = temp2
                Rossi_2exp_C = temp
                temp = Rossi_2exp_A_unc
                temp2 = Rossi_2exp_C_unc
                Rossi_2exp_A_unc = temp2
                Rossi_2exp_C_unc = temp
                temp = Rossi_2exp_B
                temp2 = Rossi_2exp_D
                Rossi_2exp_B = temp2
                Rossi_2exp_D = temp
                temp = Rossi_2exp_B_unc
                temp2 = Rossi_2exp_D_unc
                Rossi_2exp_B_unc = temp2
                Rossi_2exp_D_unc = temp
            
            print('Rossi fit with 2 exp. A*exp(-Bx) + C*exp(-Dx) + E. A = ',Rossi_2exp_A,' +/- ',Rossi_2exp_A_unc,'. B(alpha1) = ',Rossi_2exp_B,' +/- ',Rossi_2exp_B_unc,'. C = ',Rossi_2exp_C,' +/- ',Rossi_2exp_C_unc,'. D(alpha2) = ',Rossi_2exp_D,' +/- ',Rossi_2exp_D_unc,'. E = ',Rossi_2exp_E,' +/- ',Rossi_2exp_E_unc,'. 1/B = ',1/Rossi_2exp_B,' +/- ',Rossi_2exp_B_unc/Rossi_2exp_B**2,'. 1/D = ',1/Rossi_2exp_D,' +/- ',Rossi_2exp_D_unc/Rossi_2exp_D**2) 
            # Hua method ANS Winter 2018
            Rossi_2exp_combine_r1 = -Rossi_2exp_B
            Rossi_2exp_combine_r2 = -Rossi_2exp_D
            temp_a = (Rossi_2exp_C*(Rossi_2exp_combine_r1+Rossi_2exp_combine_r2))/Rossi_2exp_combine_r1 - 2*Rossi_2exp_C + 2*Rossi_2exp_A - (Rossi_2exp_A*(Rossi_2exp_combine_r1+Rossi_2exp_combine_r2))/Rossi_2exp_combine_r2
            temp_b = 2*Rossi_2exp_C -(2*Rossi_2exp_C*(Rossi_2exp_combine_r1+Rossi_2exp_combine_r2))/Rossi_2exp_combine_r1 -2*Rossi_2exp_A
            temp_c = Rossi_2exp_C*(Rossi_2exp_combine_r1+Rossi_2exp_combine_r2)/Rossi_2exp_combine_r1
            temp_Rp = (-temp_b + (temp_b**2-4*temp_a*temp_c)**0.5)/(2*temp_a)
            temp_Rm = (-temp_b - (temp_b**2-4*temp_a*temp_c)**0.5)/(2*temp_a)
            if temp_Rp >= 0 and temp_Rp <= 1:
                Rossi_2exp_combine_R = temp_Rp
            elif temp_Rm >= 0 and temp_Rm <= 1:
                Rossi_2exp_combine_R = temp_Rm
            else:
                sys.exit('Exit: R roots are outside expected range.')
            # Hua method ANS Winter 2018 Eq 21
            Rossi_2exp_combine_alpha = Rossi_2exp_combine_r1*(1-Rossi_2exp_combine_R) + Rossi_2exp_combine_r2*Rossi_2exp_combine_R
            
            plot_scatter_gatewidth(current_file_description, 'Rossi', 'micro-sec', Rossi_times_list, Rossi_data_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            if perform_Rossi_fits == True:
                fit1_info = [Rossi_times_list,fit1]
                fit2_info = [Rossi_times_list,fit2]
                plot_scatter_gatewidth(current_file_description, 'Rossi', 'micro-sec', Rossi_times_list, Rossi_data_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, fit1=fit1_info, fit2=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'Rossi', 'micro-sec', Rossi_times_list, Rossi_data_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_fit', mult_files=False, fit1=False, fit2=fit2_info, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'Rossi', 'micro-sec', Rossi_times_list, Rossi_data_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single+double_fit', mult_files=False, fit1=fit1_info, fit2=fit2_info, yaxis_log=yaxis_log)
            
            print('Rossi calculator complete.')
    
        
        # if desired to have historgrams with the same y-axis, this then finds the correct axis values and replots
        if histogram_match_axis == True:
            print('Creating histograms with matching axes.')
        
            final_xmin = 0
            final_xmax = 0
            for x in histogram_x_list:
                x_min = np.min(x)
                x_max = np.max(x)
                if x_min < final_xmin:
                    final_xmin = x
                if x_max >= final_xmax:
                    final_xmax = 1.2*x_max
            
            y_no_zero = [[ele for ele in sub if ele !=0] for sub in histogram_y_list]
            final_ymin = 1e5
            for current_y in y_no_zero:
                final_ymin = np.min([final_ymin,np.min(current_y)])
                   
            final_ymax = 0
            for i in range(0,len(histogram_y_list)):
                temp1 = np.max(histogram_y_list[i])
                temp2 = np.max(histogram_P_list[i])
                y_max = np.max([temp1,temp2])
                if y_max >= final_ymax:
                    final_ymax = 1.2*y_max
    
            
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Histograms_axis_match/', 'Histogram_am_', current_file, add_current_file=True, make_dirs=True)
            
            for l in range(0,len(gatewidth_list)):
                if input_type == '.lmx':
                    print('Gate-width = ',gatewidth_list[l])
                    single_feynman_histogram = feynman_calculator.calculate(gatewidth_list[l])
                    single_feynman_histogram.plotHistogram(poisson=True, show=False, limit_step=True, save=current_save_path, log=True, xmin=final_xmin, xmax=final_xmax, ymin=final_ymin, ymax=final_ymax, normalize=histogram_normalize, title=str(gatewidth)+' nsec')
                elif input_type == '.xml':
                    current_gatewidth = gatewidth_list[l]
                    print('Gate-width = ',current_gatewidth)
                    current_x = n_list[l]
                    current_y = feynman_data[l]
                    current_P = sum(current_y)*poissiondist.pmf(current_x, first_factorial_moment_list[l])
                    plotHistogram_single(current_gatewidth, current_x, current_y, current_P, show=False, limit_step=True, save=current_save_path+str(current_gatewidth), log=True, xmin=final_xmin, xmax=final_xmax, ymin=final_ymin, ymax=final_ymax, title=str(current_gatewidth)+' nsec')        
        
        if input_type == '.csv':
            gatewidth_list, first_reduced_factorial_moment_list, second_reduced_factorial_moment_list, third_reduced_factorial_moment_list, fourth_reduced_factorial_moment_list, first_factorial_moment_list, second_factorial_moment_list, third_factorial_moment_list, fourth_factorial_moment_list, Y1_list, dY1_list, Y2_list, dY2_list, R1_list, dR1_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, R2_user_lifetime, R2_unc_user_lifetime, Ym_list, dYm_list, Ml_list_Y2_single, dMl_list_Y2_single, Fs_list_Y2_single, dFs_list_Y2_single, Mt_list_Y2_single, dMt_list_Y2_single, kp_list_Y2_single, dkp_list_Y2_single, keff_list_Y2_single, dkeff_list_Y2_single, Ml_list_Y2_double1, dMl_list_Y2_double1, Fs_list_Y2_double1, dFs_list_Y2_double1, Mt_list_Y2_double1, dMt_list_Y2_double1, kp_list_Y2_double1, dkp_list_Y2_double1, keff_list_Y2_double1, dkeff_list_Y2_double1, Ml_list_Y2_double2, dMl_list_Y2_double2, Fs_list_Y2_double2, dFs_list_Y2_double2, Mt_list_Y2_double2, dMt_list_Y2_double2, kp_list_Y2_double2, dkp_list_Y2_double2, keff_list_Y2_double2, dkeff_list_Y2_double2, Ml_list_Y2_double_both, dMl_list_Y2_double_both, Fs_list_Y2_double_both, dFs_list_Y2_double_both, Mt_list_Y2_double_both, dMt_list_Y2_double_both, kp_list_Y2_double_both, dkp_list_Y2_double_both, keff_list_Y2_double_both, dkeff_list_Y2_double_both, Ml_list_Y2_user_lifetime, dMl_list_Y2_user_lifetime, Fs_list_Y2_user_lifetime, dFs_list_Y2_user_lifetime, Mt_list_Y2_user_lifetime, dMt_list_Y2_user_lifetime, kp_list_Y2_user_lifetime, dkp_list_Y2_user_lifetime, keff_list_Y2_user_lifetime, dkeff_list_Y2_user_lifetime, calc_eff_kn_list, calc_eff_unc_kn_list = read_csv(current_file)
            if perform_Y2_double_fit:
                perform_Y2_double_fit_continue = True
        
        if print_results == True:
            print('Summary output')
            print('Gate-width = ',gatewidth)
            print('Mean = ',single_feynman_mean)
            print('Variance = ',single_feynman_variance)
            print('V/M = ',single_variance_to_mean)
            print('Y1 = ',Y1,' +/- ',dY1)
            print('Y2 = ',Y2,' +/- ',dY2)
            print('Ym = ',Ym,' +/- ',dYm)
            print('Moments')
            print('C1 = ',first_factorial_moment)
            print('C2 = ',second_factorial_moment)
            print('C3 = ',third_factorial_moment)
            print('C4 = ',fourth_factorial_moment)
            print('Reduced factorial moments')
            print('m1 = ',first_reduced_factorial_moment)
            print('m2 = ',second_reduced_factorial_moment)
            print('m3 = ',third_reduced_factorial_moment)
            print('m4 = ',fourth_reduced_factorial_moment)
            print('R1 = ',R1,' +/- ',dR1)
            print('R2 = ',R2,' +/- ',dR2)
            #print('R1 and R2 cov = ',dR1R2)
            
        
        print('Gate loop end')
        print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
        
        if plot_individual_files == True:
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Rates/', '', current_file, add_current_file=True, make_dirs=False)    
            
            # plots of each parameter vs gatewidth for individual files
            plot_scatter_gatewidth(current_file_description, 'm1', 'micro-sec', gatewidth_list, first_reduced_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'm2', 'micro-sec', gatewidth_list, second_reduced_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'm3', 'micro-sec', gatewidth_list, third_reduced_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'm4', 'micro-sec', gatewidth_list, fourth_reduced_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C1', 'micro-sec', gatewidth_list, first_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C2', 'micro-sec', gatewidth_list, second_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C3', 'micro-sec', gatewidth_list, third_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C4', 'micro-sec', gatewidth_list, fourth_factorial_moment_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'Y1', 'micro-sec', gatewidth_list, Y1_list, marker_size, plot_titles, current_file[:-4], y_unc=dY1_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dY1', 'micro-sec', gatewidth_list, dY1_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'R1', 'micro-sec', gatewidth_list, R1_list, marker_size, plot_titles, current_file[:-4], y_unc=dR1_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dR1', 'micro-sec', gatewidth_list, dR1_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dY2', 'micro-sec', gatewidth_list, dY2_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'Ym', 'micro-sec', gatewidth_list, Ym_list, marker_size, plot_titles, current_file[:-4], y_unc=dYm_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dYm', 'micro-sec', gatewidth_list, dYm_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_single_fit == True:
                if input_type != '.csv':
                    plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_list, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, fit1=fit1_results, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_single_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_single_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_single_Y2_decay, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_single_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                if input_type != '.csv':
                    plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_list, x_div=1000, show=False, save=current_save_path+'_fit2', mult_files=False, fit1=False, fit2=fit2_results, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_double1_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_double1_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double1_Y2_decay, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_double1_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_double2_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_double2_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double2_Y2_decay, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_double2_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_double_both_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double_both_Y2_decay, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_double_both_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_single_fit == True and perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_list, x_div=1000, show=False, save=current_save_path+'_fit1+fit2', mult_files=False, fit1=fit1_results, fit2=fit2_results, yaxis_log=yaxis_log)
            if use_user_specified_lifetime == True:
                plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_list, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, fit1=fit_lifetime_user_results, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_lifetime_user_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log) 
            if calculation_type == 'Cf':
                plot_scatter_gatewidth(current_file_description, 'Efficiency', 'micro-sec', gatewidth_list, calc_eff_kn_list, marker_size, plot_titles, current_file[:-4], y_unc=calc_eff_unc_kn_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dEfficiency', 'micro-sec', gatewidth_list, calc_eff_unc_kn_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            elif calculation_type == 'Multiplicity':
                if perform_Y2_single_fit == True:
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dMl_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dFs_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dMt_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dkp_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dMl_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dFs_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dMt_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dkp_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dMl_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dFs_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dMt_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dkp_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dMl_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dFs_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dMt_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dkp_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                if use_user_specified_lifetime == True:
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dMl_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dFs_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dMt_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dkp_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    
            print('Plotting individual files end for file ',current_file)
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
        
        
        # set N/A to lists if fits were not performed
        if perform_Y2_single_fit != True:
            fit1log_A = fit1log_A_unc = fit1log_B = fit1log_B_unc = fit1log_det_lifetime = fit1log_det_lifetime_unc = 'N/A'   
            omega2_single_results = R2_single_Y2_decay = R2_unc_single_Y2_decay = ['N/A' for i in range(0,len(gatewidth_list))]
        if perform_Y2_double_fit != True or perform_Y2_double_fit_continue != True:
            fit2log_A = fit2log_A_unc = fit2log_B = fit2log_B_unc = fit2log_C = fit2log_C_unc = fit2log_D = fit2log_D_unc = fit2log_det_lifetime1 = fit2log_det_lifetime1_unc = fit2log_det_lifetime2 = fit2log_det_lifetime2_unc = 'N/A'
            omega2_double1_results = R2_double1_Y2_decay = R2_unc_double1_Y2_decay = omega2_double2_results = R2_double2_Y2_decay = R2_unc_double2_Y2_decay = R2_double_both_Y2_decay = R2_unc_double_both_Y2_decay = ['N/A' for i in range(0,len(gatewidth_list))]
        if use_user_specified_lifetime != True:
            omega2_lifetime_user_results = R2_user_lifetime = R2_unc_user_lifetime = ['N/A' for i in range(0,len(gatewidth_list))]
        
        # output a single csv file for each file and gives results vs gatewidth if set to True by the user
        if output_csv == True:
            if plot_histograms == True or plot_individual_files == True or plot_all_files_vs_gw == True or plot_all_files_vs_con == True or perform_Y2_single_fit == True or perform_Y2_double_fit == True:
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Individual_Files/Rates/', '', current_file, add_current_file=True, make_dirs=True)    
                
                if len(file_descriptions) > 0:
                    csv_name = current_save_path+current_file_description+'_.csv'
                else:
                    csv_name = current_save_path+'.csv'
                
                ################# START HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE 2/26/23
                # Continuing to work towards implementing calculation_type 'Multiplicity'
                # Note how csv was done for Cf and do something similar
                
                with open(csv_name, mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    header_row = ['Gate-width','m1','m2','m3','m4','C1','C2','C3','C4','Y1','dY1','Y2','dY2','R1','dR1','fit1log_A','fit1log_A_unc','fit1log_B','fit1log_B_unc','fit1log_det_lifetime','fit1log_det_lifetime_unc','omega2_single_results','R2_single_Y2_decay','R2_unc_single_Y2_decay','fit2log_A','fit2log_A_unc','fit2log_B','fit2log_B_unc','fit2log_C','fit2log_C_unc','fit2log_D','fit2log_D_unc','fit2log_det_lifetime1','fit2log_det_lifetime1_unc','fit2log_det_lifetime2','fit2log_det_lifetime2_unc','omega2_double1_results','R2_double1_Y2_decay','R2_unc_double1_Y2_decay','omega2_double2_results','R2_double2_Y2_decay','R2_unc_double2_Y2_decay','R2_double_both_Y2_decay','R2_unc_double_both_Y2_decay','omega2_lifetime_user_results','R2_user_lifetime','R2_unc_user_lifetime','Ym','dYm']
                    if calculation_type == 'Cf':
                        header_row.append('eff from Cf')
                        header_row.append('deff from Cf')
                    elif calculation_type == 'Multiplicity':
                        if perform_Y2_single_fit == True:
                            header_row.append('Ml (Y2 single)')
                            header_row.append('dMl (Y2 single)')
                            header_row.append('Fs (Y2 single)')
                            header_row.append('dFs (Y2 single)')
                            header_row.append('Mt (Y2 single)')
                            header_row.append('dMt (Y2 single)')
                            header_row.append('kp (Y2 single)')
                            header_row.append('dkp (Y2 single)')
                            header_row.append('keff (Y2 single)')
                            header_row.append('dkeff (Y2 single)')
                        if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                            header_row.append('Ml (Y2_double1)')
                            header_row.append('dMl (Y2 double1)')
                            header_row.append('Fs (Y2 double1)')
                            header_row.append('dFs (Y2 double1)')
                            header_row.append('Mt (Y2 double1)')
                            header_row.append('dMt (Y2 double1)')
                            header_row.append('kp (Y2 double1)')
                            header_row.append('dkp (Y2 double1)')
                            header_row.append('keff (Y2 double1)')
                            header_row.append('dkeff (Y2 double1)')
                            header_row.append('Ml (Y2_double2)')
                            header_row.append('dMl (Y2 double2)')
                            header_row.append('Fs (Y2 double2)')
                            header_row.append('dFs (Y2 double2)')
                            header_row.append('Mt (Y2 double2)')
                            header_row.append('dMt (Y2 double2)')
                            header_row.append('kp (Y2 double2)')
                            header_row.append('dkp (Y2 double2)')
                            header_row.append('keff (Y2 double2)')
                            header_row.append('dkeff (Y2 double2)')
                            header_row.append('Ml (Y2_double_both)')
                            header_row.append('dMl (Y2 double_both)')
                            header_row.append('Fs (Y2 double_both)')
                            header_row.append('dFs (Y2 double_both)')
                            header_row.append('Mt (Y2 double_both)')
                            header_row.append('dMt (Y2 double_both)')
                            header_row.append('kp (Y2 double_both)')
                            header_row.append('dkp (Y2 double_both)')
                            header_row.append('keff (Y2 double_both)')
                            header_row.append('dkeff (Y2 double_both)')
                        if use_user_specified_lifetime == True:
                            header_row.append('Ml (Y2_user_lifetime)')
                            header_row.append('dMl (Y2 user_lifetime)')
                            header_row.append('Fs (Y2 user_lifetime)')
                            header_row.append('dFs (Y2 user_lifetime)')
                            header_row.append('Mt (Y2 user_lifetime)')
                            header_row.append('dMt (Y2 user_lifetime)')
                            header_row.append('kp (Y2 user_lifetime)')
                            header_row.append('dkp (Y2 user_lifetime)')
                            header_row.append('keff (Y2 user_lifetime)')
                            header_row.append('dkeff (Y2 user_lifetime)')
                              
                    writer.writerow(header_row)
                    for value in range(len(gatewidth_list)):
                        data_row = [gatewidth_list[value], first_reduced_factorial_moment_list[value], second_reduced_factorial_moment_list[value], third_reduced_factorial_moment_list[value], fourth_reduced_factorial_moment_list[value], first_factorial_moment_list[value], second_factorial_moment_list[value], third_factorial_moment_list[value], fourth_factorial_moment_list[value], Y1_list[value], dY1_list[value], Y2_list[value], dY2_list[value], R1_list[value], dR1_list[value], fit1log_A,fit1log_A_unc,fit1log_B,fit1log_B_unc,fit1log_det_lifetime,fit1log_det_lifetime_unc,omega2_single_results[value],R2_single_Y2_decay[value],R2_unc_single_Y2_decay[value],fit2log_A,fit2log_A_unc,fit2log_B,fit2log_B_unc,fit2log_C,fit2log_C_unc,fit2log_D,fit2log_D_unc,fit2log_det_lifetime1,fit2log_det_lifetime1_unc,fit2log_det_lifetime2,fit2log_det_lifetime2_unc,omega2_double1_results[value],R2_double1_Y2_decay[value],R2_unc_double1_Y2_decay[value],omega2_double2_results[value],R2_double2_Y2_decay[value],R2_unc_double2_Y2_decay[value],R2_double_both_Y2_decay[value],R2_unc_double_both_Y2_decay[value],omega2_lifetime_user_results[value],R2_user_lifetime[value],R2_unc_user_lifetime[value], Ym_list[value], dYm_list[value]]
                        if calculation_type == 'Cf':
                            data_row.append(calc_eff_kn_list[value])
                            data_row.append(calc_eff_unc_kn_list[value])
                        elif calculation_type == 'Multiplicity':
                            if perform_Y2_single_fit == True:
                                data_row.append(Ml_list_Y2_single[value])
                                data_row.append(dMl_list_Y2_single[value])
                                data_row.append(Fs_list_Y2_single[value])
                                data_row.append(dFs_list_Y2_single[value])
                                data_row.append(Mt_list_Y2_single[value])
                                data_row.append(dMt_list_Y2_single[value])
                                data_row.append(kp_list_Y2_single[value])
                                data_row.append(dkp_list_Y2_single[value])
                                data_row.append(keff_list_Y2_single[value])
                                data_row.append(dkeff_list_Y2_single[value])
                            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                data_row.append(Ml_list_Y2_double1[value])
                                data_row.append(dMl_list_Y2_double1[value])
                                data_row.append(Fs_list_Y2_double1[value])
                                data_row.append(dFs_list_Y2_double1[value])
                                data_row.append(Mt_list_Y2_double1[value])
                                data_row.append(dMt_list_Y2_double1[value])
                                data_row.append(kp_list_Y2_double1[value])
                                data_row.append(dkp_list_Y2_double1[value])
                                data_row.append(keff_list_Y2_double1[value])
                                data_row.append(dkeff_list_Y2_double1[value])
                                data_row.append(Ml_list_Y2_double2[value])
                                data_row.append(dMl_list_Y2_double2[value])
                                data_row.append(Fs_list_Y2_double2[value])
                                data_row.append(dFs_list_Y2_double2[value])
                                data_row.append(Mt_list_Y2_double2[value])
                                data_row.append(dMt_list_Y2_double2[value])
                                data_row.append(kp_list_Y2_double2[value])
                                data_row.append(dkp_list_Y2_double2[value])
                                data_row.append(keff_list_Y2_double2[value])
                                data_row.append(dkeff_list_Y2_double2[value])
                                data_row.append(Ml_list_Y2_double_both[value])
                                data_row.append(dMl_list_Y2_double_both[value])
                                data_row.append(Fs_list_Y2_double_both[value])
                                data_row.append(dFs_list_Y2_double_both[value])
                                data_row.append(Mt_list_Y2_double_both[value])
                                data_row.append(dMt_list_Y2_double_both[value])
                                data_row.append(kp_list_Y2_double_both[value])
                                data_row.append(dkp_list_Y2_double_both[value])
                                data_row.append(keff_list_Y2_double_both[value])
                                data_row.append(dkeff_list_Y2_double_both[value])
                            if use_user_specified_lifetime == True:
                                data_row.append(Ml_list_Y2_user_lifetime[value])
                                data_row.append(dMl_list_Y2_user_lifetime[value])
                                data_row.append(Fs_list_Y2_user_lifetime[value])
                                data_row.append(dFs_list_Y2_user_lifetime[value])
                                data_row.append(Mt_list_Y2_user_lifetime[value])
                                data_row.append(dMt_list_Y2_user_lifetime[value])
                                data_row.append(kp_list_Y2_user_lifetime[value])
                                data_row.append(dkp_list_Y2_user_lifetime[value])
                                data_row.append(keff_list_Y2_user_lifetime[value])
                                data_row.append(dkeff_list_Y2_user_lifetime[value])      
                        writer.writerow(data_row)
        
            
        # appends the individual file lists to lists containing all files
        gatewidth_all_files.append(gatewidth_list)
        first_reduced_factorial_moment_all_files.append(first_reduced_factorial_moment_list)
        second_reduced_factorial_moment_all_files.append(second_reduced_factorial_moment_list)
        third_reduced_factorial_moment_all_files.append(third_reduced_factorial_moment_list)
        fourth_reduced_factorial_moment_all_files.append(fourth_reduced_factorial_moment_list)
        first_factorial_moment_all_files.append(first_factorial_moment_list)
        second_factorial_moment_all_files.append(second_factorial_moment_list)
        third_factorial_moment_all_files.append(third_factorial_moment_list)
        fourth_factorial_moment_all_files.append(fourth_factorial_moment_list)
        single_feynman_mean_all_files.append(single_feynman_mean_list)
        single_feynman_variance_all_files.append(single_feynman_variance_list)
        single_variance_to_mean_all_files.append(single_variance_to_mean_list)
        Y1_all_files.append(Y1_list)
        dY1_all_files.append(dY1_list) 
        R1_all_files.append(Y1_list)
        dR1_all_files.append(dY1_list) 
        Y2_all_files.append(Y2_list)
        dY2_all_files.append(dY2_list)
        Ym_all_files.append(Ym_list)
        dYm_all_files.append(dYm_list)
        R2_single_Y2_decay_all_files.append(R2_single_Y2_decay)
        R2_unc_single_Y2_decay_all_files.append(R2_unc_single_Y2_decay)
        R2_double1_Y2_decay_all_files.append(R2_double1_Y2_decay)
        R2_unc_double1_Y2_decay_all_files.append(R2_unc_double1_Y2_decay)
        R2_double2_Y2_decay_all_files.append(R2_double2_Y2_decay)
        R2_unc_double2_Y2_decay_all_files.append(R2_unc_double2_Y2_decay)
        R2_double_both_Y2_decay_all_files.append(R2_double_both_Y2_decay)
        R2_unc_double_both_Y2_decay_all_files.append(R2_unc_double_both_Y2_decay)
        R2_user_lifetime_all_files.append(R2_user_lifetime)
        R2_unc_user_lifetime_all_files.append(R2_unc_user_lifetime)
        if calculation_type == 'Cf':
            calc_eff_kn_all_files.append(calc_eff_kn_list)
            calc_eff_unc_kn_all_files.append(calc_eff_unc_kn_list)
        elif calculation_type == 'Multiplicity':
            if perform_Y2_single_fit == True:
                Ml_single_all_files.append(Ml_list_Y2_single)
                dMl_single_all_files.append(dMl_list_Y2_single)
                Mt_single_all_files.append(Mt_list_Y2_single)
                dMt_single_all_files.append(dMt_list_Y2_single)
                Fs_single_all_files.append(Fs_list_Y2_single)
                dFs_single_all_files.append(dFs_list_Y2_single)
                kp_single_all_files.append(kp_list_Y2_single)
                dkp_single_all_files.append(dkp_list_Y2_single)
                keff_single_all_files.append(keff_list_Y2_single)
                dkeff_single_all_files.append(dkeff_list_Y2_single)
            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                Ml_double1_all_files.append(Ml_list_Y2_double1)
                dMl_double1_all_files.append(dMl_list_Y2_double1)
                Mt_double1_all_files.append(Mt_list_Y2_double1)
                dMt_double1_all_files.append(dMt_list_Y2_double1)
                Fs_double1_all_files.append(Fs_list_Y2_double1)
                dFs_double1_all_files.append(dFs_list_Y2_double1)
                kp_double1_all_files.append(kp_list_Y2_double1)
                dkp_double1_all_files.append(dkp_list_Y2_double1)
                keff_double1_all_files.append(keff_list_Y2_double1)
                dkeff_double1_all_files.append(dkeff_list_Y2_double1)
                Ml_double2_all_files.append(Ml_list_Y2_double2)
                dMl_double2_all_files.append(dMl_list_Y2_double2)
                Mt_double2_all_files.append(Mt_list_Y2_double2)
                dMt_double2_all_files.append(dMt_list_Y2_double2)
                Fs_double2_all_files.append(Fs_list_Y2_double2)
                dFs_double2_all_files.append(dFs_list_Y2_double2)
                kp_double2_all_files.append(kp_list_Y2_double2)
                dkp_double2_all_files.append(dkp_list_Y2_double2)
                keff_double2_all_files.append(keff_list_Y2_double2)
                dkeff_double2_all_files.append(dkeff_list_Y2_double2)
                Ml_double_both_all_files.append(Ml_list_Y2_double_both)
                dMl_double_both_all_files.append(dMl_list_Y2_double_both)
                Mt_double_both_all_files.append(Mt_list_Y2_double_both)
                dMt_double_both_all_files.append(dMt_list_Y2_double_both)
                Fs_double_both_all_files.append(Fs_list_Y2_double_both)
                dFs_double_both_all_files.append(dFs_list_Y2_double_both)
                kp_double_both_all_files.append(kp_list_Y2_double_both)
                dkp_double_both_all_files.append(dkp_list_Y2_double_both)
                keff_double_both_all_files.append(keff_list_Y2_double_both)
                dkeff_double_both_all_files.append(dkeff_list_Y2_double_both)
            if use_user_specified_lifetime == True:
                Ml_user_lifetime_all_files.append(Ml_list_Y2_user_lifetime)
                dMl_user_lifetime_all_files.append(dMl_list_Y2_user_lifetime)
                Mt_user_lifetime_all_files.append(Mt_list_Y2_user_lifetime)
                dMt_user_lifetime_all_files.append(dMt_list_Y2_user_lifetime)
                Fs_user_lifetime_all_files.append(Fs_list_Y2_user_lifetime)
                dFs_user_lifetime_all_files.append(dFs_list_Y2_user_lifetime)
                kp_user_lifetime_all_files.append(kp_list_Y2_user_lifetime)
                dkp_user_lifetime_all_files.append(dkp_list_Y2_user_lifetime)
                keff_user_lifetime_all_files.append(keff_list_Y2_user_lifetime)
                dkeff_user_lifetime_all_files.append(dkeff_list_Y2_user_lifetime) 
        if input_type != '.csv':
            histogram_x_all_files.append(histogram_x_list)
            histogram_y_all_files.append(histogram_y_list)
            histogram_P_all_files.append(histogram_P_list)
            fit1log_A_all_files.append(fit1log_A)
            fit1log_A_unc_all_files.append(fit1log_A_unc)
            fit1log_B_all_files.append(fit1log_B)
            fit1log_B_unc_all_files.append(fit1log_B_unc)
            fit1log_det_lifetime_all_files.append(fit1log_det_lifetime)
            fit1log_det_lifetime_unc_all_files.append(fit1log_det_lifetime_unc)   
            omega2_single_results_all_files.append(omega2_single_results)
            fit2log_A_all_files.append(fit2log_A)
            fit2log_A_unc_all_files.append(fit2log_A_unc)
            fit2log_B_all_files.append(fit2log_B)
            fit2log_B_unc_all_files.append(fit2log_B_unc)
            fit2log_C_all_files.append(fit2log_C)
            fit2log_C_unc_all_files.append(fit2log_C_unc)
            fit2log_D_all_files.append(fit2log_D)
            fit2log_D_unc_all_files.append(fit2log_D_unc)
            fit2log_det_lifetime1_all_files.append(fit2log_det_lifetime1)
            fit2log_det_lifetime1_unc_all_files.append(fit2log_det_lifetime1_unc)
            fit2log_det_lifetime2_all_files.append(fit2log_det_lifetime2)
            fit2log_det_lifetime2_unc_all_files.append(fit2log_det_lifetime2_unc)
            omega2_double1_results_all_files.append(omega2_double1_results)
            omega2_double2_results_all_files.append(omega2_double2_results)
            omega2_lifetime_user_results_all_files.append(omega2_lifetime_user_results)
            if perform_Y2_single_fit == True:
                fit1_results_all_files.append(fit1_results)
            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                fit2_results_all_files.append(fit2_results)
            if use_user_specified_lifetime == True:
                fit_lifetime_user_results_all_files.append(fit_lifetime_user_results)
            if perform_Rossi == True and perform_Rossi_fits == True:
                Rossi_fit1_results_all_files.append(fit1_info)
                Rossi_fit2_results_all_files.append(fit2_info)
                Rossi_times_all_files.append(Rossi_times_list)
                Rossi_data_all_files.append(Rossi_data_list)
                Rossi_1exp_A_all_files.append(Rossi_1exp_A)
                Rossi_1exp_B_all_files.append(Rossi_1exp_B)
                Rossi_1exp_C_all_files.append(Rossi_1exp_C)
                Rossi_1exp_A_unc_all_files.append(Rossi_1exp_A_unc)
                Rossi_1exp_B_unc_all_files.append(Rossi_1exp_B_unc)
                Rossi_1exp_C_unc_all_files.append(Rossi_1exp_C_unc)
                Rossi_2exp_A_all_files.append(Rossi_2exp_A)
                Rossi_2exp_B_all_files.append(Rossi_2exp_B)
                Rossi_2exp_C_all_files.append(Rossi_2exp_C)
                Rossi_2exp_D_all_files.append(Rossi_2exp_D)
                Rossi_2exp_E_all_files.append(Rossi_2exp_E)
                Rossi_2exp_A_unc_all_files.append(Rossi_2exp_A_unc)
                Rossi_2exp_B_unc_all_files.append(Rossi_2exp_B_unc)
                Rossi_2exp_C_unc_all_files.append(Rossi_2exp_C_unc)
                Rossi_2exp_D_unc_all_files.append(Rossi_2exp_D_unc)
                Rossi_2exp_E_unc_all_files.append(Rossi_2exp_E_unc)
            if calculation_type == 'Multiplicity':
                dR1R2_all_files.append(dR1R2_list)
                if perform_Y2_single_fit == True:
                    a1_single_all_files.append(a1_list_Y2_single)
                    a2_single_all_files.append(a2_list_Y2_single)
                    a3_single_all_files.append(a3_list_Y2_single)
                    a4_single_all_files.append(a4_list_Y2_single)
                    a5_single_all_files.append(a5_list_Y2_single)
                    a6_single_all_files.append(a6_list_Y2_single)
                    a7_single_all_files.append(a7_list_Y2_single)
                    dMldR1_single_all_files.append(dMldR1_list_Y2_single)
                    dMldR2_single_all_files.append(dMldR2_list_Y2_single)
                    dMldeff_single_all_files.append(dMldeff_list_Y2_single)
                    dFsdR1_single_all_files.append(dFsdR1_list_Y2_single)
                    dFsdR2_single_all_files.append(dFsdR2_list_Y2_single)
                    dFsdeff_single_all_files.append(dFsdeff_list_Y2_single)
                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                    a1_double1_all_files.append(a1_list_Y2_double1)
                    a2_double1_all_files.append(a2_list_Y2_double1)
                    a3_double1_all_files.append(a3_list_Y2_double1)
                    a4_double1_all_files.append(a4_list_Y2_double1)
                    a5_double1_all_files.append(a5_list_Y2_double1)
                    a6_double1_all_files.append(a6_list_Y2_double1)
                    a7_double1_all_files.append(a7_list_Y2_double1)
                    dMldR1_double1_all_files.append(dMldR1_list_Y2_double1)
                    dMldR2_double1_all_files.append(dMldR2_list_Y2_double1)
                    dMldeff_double1_all_files.append(dMldeff_list_Y2_double1)
                    dFsdR1_double1_all_files.append(dFsdR1_list_Y2_double1)
                    dFsdR2_double1_all_files.append(dFsdR2_list_Y2_double1)
                    dFsdeff_double1_all_files.append(dFsdeff_list_Y2_double1)
                    a1_double2_all_files.append(a1_list_Y2_double2)
                    a2_double2_all_files.append(a2_list_Y2_double2)
                    a3_double2_all_files.append(a3_list_Y2_double2)
                    a4_double2_all_files.append(a4_list_Y2_double2)
                    a5_double2_all_files.append(a5_list_Y2_double2)
                    a6_double2_all_files.append(a6_list_Y2_double2)
                    a7_double2_all_files.append(a7_list_Y2_double2)
                    dMldR1_double2_all_files.append(dMldR1_list_Y2_double2)
                    dMldR2_double2_all_files.append(dMldR2_list_Y2_double2)
                    dMldeff_double2_all_files.append(dMldeff_list_Y2_double2)
                    dFsdR1_double2_all_files.append(dFsdR1_list_Y2_double2)
                    dFsdR2_double2_all_files.append(dFsdR2_list_Y2_double2)
                    dFsdeff_double2_all_files.append(dFsdeff_list_Y2_double2)
                    a1_double_both_all_files.append(a1_list_Y2_double_both)
                    a2_double_both_all_files.append(a2_list_Y2_double_both)
                    a3_double_both_all_files.append(a3_list_Y2_double_both)
                    a4_double_both_all_files.append(a4_list_Y2_double_both)
                    a5_double_both_all_files.append(a5_list_Y2_double_both)
                    a6_double_both_all_files.append(a6_list_Y2_double_both)
                    a7_double_both_all_files.append(a7_list_Y2_double_both)
                    dMldR1_double_both_all_files.append(dMldR1_list_Y2_double_both)
                    dMldR2_double_both_all_files.append(dMldR2_list_Y2_double_both)
                    dMldeff_double_both_all_files.append(dMldeff_list_Y2_double_both)
                    dFsdR1_double_both_all_files.append(dFsdR1_list_Y2_double_both)
                    dFsdR2_double_both_all_files.append(dFsdR2_list_Y2_double_both)
                    dFsdeff_double_both_all_files.append(dFsdeff_list_Y2_double_both)
                if use_user_specified_lifetime == True:
                    a1_user_lifetime_all_files.append(a1_list_Y2_user_lifetime)
                    a2_user_lifetime_all_files.append(a2_list_Y2_user_lifetime)
                    a3_user_lifetime_all_files.append(a3_list_Y2_user_lifetime)
                    a4_user_lifetime_all_files.append(a4_list_Y2_user_lifetime)
                    a5_user_lifetime_all_files.append(a5_list_Y2_user_lifetime)
                    a6_user_lifetime_all_files.append(a6_list_Y2_user_lifetime)
                    a7_user_lifetime_all_files.append(a7_list_Y2_user_lifetime)
                    dMldR1_user_lifetime_all_files.append(dMldR1_list_Y2_user_lifetime)
                    dMldR2_user_lifetime_all_files.append(dMldR2_list_Y2_user_lifetime)
                    dMldeff_user_lifetime_all_files.append(dMldeff_list_Y2_user_lifetime)
                    dFsdR1_user_lifetime_all_files.append(dFsdR1_list_Y2_user_lifetime)
                    dFsdR2_user_lifetime_all_files.append(dFsdR2_list_Y2_user_lifetime)
                    dFsdeff_user_lifetime_all_files.append(dFsdeff_list_Y2_user_lifetime)
                
    if len(files) > 1:
        
        # analysis for more than one file
        print('#################################################')
              
        # plot all files together (files = series, x-axis = gate-width)
        if plot_all_files_vs_gw == True:
            print('Plotting all files together (files = series, x-axis = gate-width) start')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'All_Files/Rates/', '', current_file, add_current_file=False, make_dirs=True)
                
            plot_scatter_gatewidth(file_descriptions,'m1', 'micro-sec', gatewidth_all_files, first_reduced_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'m2', 'micro-sec', gatewidth_all_files, second_reduced_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'m3', 'micro-sec', gatewidth_all_files, third_reduced_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'m4', 'micro-sec', gatewidth_all_files, fourth_reduced_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'C1', 'micro-sec', gatewidth_all_files, first_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'C2', 'micro-sec', gatewidth_all_files, second_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'C3', 'micro-sec', gatewidth_all_files, third_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'C4', 'micro-sec', gatewidth_all_files, fourth_factorial_moment_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'Y1', 'micro-sec', gatewidth_all_files, Y1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dY1_all_files, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'dY1', 'micro-sec', gatewidth_all_files, dY1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions, 'R1', 'micro-sec', gatewidth_all_files, R1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dR1_all_files, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions, 'dR1', 'micro-sec', gatewidth_all_files, dR1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'Y2', 'micro-sec', gatewidth_all_files, Y2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dY2_all_files, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'dY2', 'micro-sec', gatewidth_all_files, dY2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'Ym', 'micro-sec', gatewidth_all_files, Ym_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dYm_all_files, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(file_descriptions,'dYm', 'micro-sec', gatewidth_all_files, dYm_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            if perform_Y2_single_fit == True:
                if input_type != '.csv':
                    plot_scatter_gatewidth(file_descriptions,'Y2', 'micro-sec', gatewidth_all_files, Y2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dY2_all_files, x_div=1000, show=False, save=current_save_path+'_fit1', mult_files=True, fit1=fit1_results_all_files, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'omega2', 'micro-sec', gatewidth_all_files, omega2_single_results_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_all_files, R2_single_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_single_Y2_decay_all_files, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_all_files, R2_unc_single_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                if input_type != '.csv':
                    plot_scatter_gatewidth(file_descriptions,'Y2', 'micro-sec', gatewidth_all_files, Y2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dY2_all_files, x_div=1000, show=False, save=current_save_path+'_fit2', mult_files=True, fit1=False, fit2=fit2_results_all_files, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'omega2', 'micro-sec', gatewidth_all_files, omega2_double1_results_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'omega2', 'micro-sec', gatewidth_all_files, omega2_double2_results_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_all_files, R2_double1_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double1_Y2_decay_all_files, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_all_files, R2_unc_double1_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_all_files, R2_double2_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double2_Y2_decay_all_files, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_all_files, R2_unc_double2_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_all_files, R2_double_both_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double_both_Y2_decay_all_files, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_all_files, R2_unc_double_both_Y2_decay_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
            if perform_Y2_single_fit == True and perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True and input_type != '.csv':
                plot_scatter_gatewidth(file_descriptions,'Y2', 'micro-sec', gatewidth_all_files, Y2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dY2_all_files, x_div=1000, show=False, save=current_save_path+'_fit1+fit2', mult_files=True, fit1=fit1_results_all_files, fit2=fit2_results_all_files, yaxis_log=yaxis_log)
            if use_user_specified_lifetime == True:
                if input_type != '.csv':
                    plot_scatter_gatewidth(file_descriptions,'Y2', 'micro-sec', gatewidth_all_files, Y2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dY2_all_files, x_div=1000, show=False, save=current_save_path+'_fituser', mult_files=True, fit1=fit_lifetime_user_results_all_files, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'omega2', 'micro-sec', gatewidth_all_files, omega2_lifetime_user_results_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_all_files, R2_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_user_lifetime_all_files, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_all_files, R2_unc_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
            if calculation_type == 'Cf':
                plot_scatter_gatewidth(file_descriptions,'Efficiency', 'micro-sec', gatewidth_all_files, calc_eff_kn_all_files, marker_size, plot_titles, current_file[:-4], y_unc=calc_eff_unc_kn_all_files, x_div=1000, show=False, save=current_save_path, mult_files=True)
                plot_scatter_gatewidth(file_descriptions,'dEfficiency', 'micro-sec', gatewidth_all_files, calc_eff_unc_kn_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True)
            elif calculation_type == 'Multiplicity':
                if perform_Y2_single_fit == True:
                    plot_scatter_gatewidth(file_descriptions, 'Ml', 'micro-sec', gatewidth_all_files, Ml_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMl_single_all_files, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMl', 'micro-sec', gatewidth_all_files, dMl_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Fs', 'micro-sec', gatewidth_all_files, Fs_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dFs_single_all_files, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dFs', 'micro-sec', gatewidth_all_files, dFs_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Mt', 'micro-sec', gatewidth_all_files, Mt_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMt_single_all_files, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMt', 'micro-sec', gatewidth_all_files, dMt_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'kp', 'micro-sec', gatewidth_all_files, kp_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkp_single_all_files, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkp', 'micro-sec', gatewidth_all_files, dkp_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'keff', 'micro-sec', gatewidth_all_files, keff_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_single_all_files, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkeff', 'micro-sec', gatewidth_all_files, dkeff_single_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                    plot_scatter_gatewidth(file_descriptions, 'Ml', 'micro-sec', gatewidth_all_files, Ml_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMl_double1_all_files, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMl', 'micro-sec', gatewidth_all_files, dMl_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Fs', 'micro-sec', gatewidth_all_files, Fs_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dFs_double1_all_files, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dFs', 'micro-sec', gatewidth_all_files, dFs_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Mt', 'micro-sec', gatewidth_all_files, Mt_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMt_double1_all_files, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMt', 'micro-sec', gatewidth_all_files, dMt_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'kp', 'micro-sec', gatewidth_all_files, kp_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkp_double1_all_files, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkp', 'micro-sec', gatewidth_all_files, dkp_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'keff', 'micro-sec', gatewidth_all_files, keff_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_double1_all_files, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkeff', 'micro-sec', gatewidth_all_files, dkeff_double1_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Ml', 'micro-sec', gatewidth_all_files, Ml_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMl_double2_all_files, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMl', 'micro-sec', gatewidth_all_files, dMl_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Fs', 'micro-sec', gatewidth_all_files, Fs_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dFs_double2_all_files, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dFs', 'micro-sec', gatewidth_all_files, dFs_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Mt', 'micro-sec', gatewidth_all_files, Mt_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMt_double2_all_files, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMt', 'micro-sec', gatewidth_all_files, dMt_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'kp', 'micro-sec', gatewidth_all_files, kp_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkp_double2_all_files, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkp', 'micro-sec', gatewidth_all_files, dkp_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'keff', 'micro-sec', gatewidth_all_files, keff_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_double2_all_files, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkeff', 'micro-sec', gatewidth_all_files, dkeff_double2_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Ml', 'micro-sec', gatewidth_all_files, Ml_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMl_double_both_all_files, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMl', 'micro-sec', gatewidth_all_files, dMl_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Fs', 'micro-sec', gatewidth_all_files, Fs_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dFs_double_both_all_files, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dFs', 'micro-sec', gatewidth_all_files, dFs_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Mt', 'micro-sec', gatewidth_all_files, Mt_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMt_double_both_all_files, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMt', 'micro-sec', gatewidth_all_files, dMt_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'kp', 'micro-sec', gatewidth_all_files, kp_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkp_double_both_all_files, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkp', 'micro-sec', gatewidth_all_files, dkp_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'keff', 'micro-sec', gatewidth_all_files, keff_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_double_both_all_files, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkeff', 'micro-sec', gatewidth_all_files, dkeff_double_both_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
                if use_user_specified_lifetime == True:
                    plot_scatter_gatewidth(file_descriptions, 'Ml', 'micro-sec', gatewidth_all_files, Ml_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMl_user_lifetime_all_files, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMl', 'micro-sec', gatewidth_all_files, dMl_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Fs', 'micro-sec', gatewidth_all_files, Fs_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dFs_user_lifetime_all_files, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dFs', 'micro-sec', gatewidth_all_files, dFs_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'Mt', 'micro-sec', gatewidth_all_files, Mt_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dMt_user_lifetime_all_files, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dMt', 'micro-sec', gatewidth_all_files, dMt_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'kp', 'micro-sec', gatewidth_all_files, kp_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkp_user_lifetime_all_files, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkp', 'micro-sec', gatewidth_all_files, dkp_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'keff', 'micro-sec', gatewidth_all_files, keff_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_user_lifetime_all_files, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(file_descriptions, 'dkeff', 'micro-sec', gatewidth_all_files, dkeff_user_lifetime_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=True, yaxis_log=yaxis_log)
        
            #Y2 fits list
            if output_csv == True:
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'All_Files/Rates/', '', current_file, add_current_file=False, make_dirs=False)
                
                if perform_Y2_single_fit == True or perform_Y2_double_fit == True:
                    csv_name = current_save_path+'Y2_fits.csv'
                    
                    with open(csv_name, mode='w', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(['Configuration #','File','File Description','Single fit: A','Single fit: A unc','Single fit: B','Single fit: B unc','Single fit: Lifetime','Single fit: Lifetime unc','Double fit: A','Double fit: A unc','Double fit: B','Double fit: B unc','Double fit: C','Double fit: C unc','Double fit: D','Double fit: D unc','Double fit: Lifetime1','Double fit: Lifetime1 unc','Double fit: Lifetime2','Double fit: Lifetime2 unc'])
                        for value in range(len(files)):
                            if len(file_descriptions) > 0:
                                writer.writerow([file_number[value], files[value], file_descriptions[value],fit1log_A_all_files[value],fit1log_A_unc_all_files[value],fit1log_B_all_files[value],fit1log_B_unc_all_files[value],fit1log_det_lifetime_all_files[value],fit1log_det_lifetime_unc_all_files[value],fit2log_A_all_files[value],fit2log_A_unc_all_files[value],fit2log_B_all_files[value],fit2log_B_unc_all_files[value],fit2log_C_all_files[value],fit2log_C_unc_all_files[value],fit2log_D_all_files[value],fit2log_D_unc_all_files[value],fit2log_det_lifetime1_all_files[value],fit2log_det_lifetime1_unc_all_files[value],fit2log_det_lifetime2_all_files[value],fit2log_det_lifetime2_unc_all_files[value]])        
                            else:
                                writer.writerow([file_number[value], files[value], '',fit1log_A_all_files[value],fit1log_A_unc_all_files[value],fit1log_B_all_files[value],fit1log_B_unc_all_files[value],fit1log_det_lifetime_all_files[value],fit1log_det_lifetime_unc_all_files[value],fit2log_A_all_files[value],fit2log_A_unc_all_files[value],fit2log_B_all_files[value],fit2log_B_unc_all_files[value],fit2log_C_all_files[value],fit2log_C_unc_all_files[value],fit2log_D_all_files[value],fit2log_D_unc_all_files[value],fit2log_det_lifetime1_all_files[value],fit2log_det_lifetime1_unc_all_files[value],fit2log_det_lifetime2_all_files[value],fit2log_det_lifetime2_unc_all_files[value]])        
        
            print('Plotting all files together (files = series, x-axis = gate-width) end')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
        
        # Plots histograms from multiple files together
        if plot_histograms == True or sum_Feynman_histograms == True:
            print('Plotting all files histograms start')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            if output_nested_subdirectories == True:
                if not os.path.exists(save_path+'All_Files/Histograms/'):
                    os.makedirs(save_path+'All_Files/Histograms/')
            histogram_x_transposed = np.array(histogram_x_all_files).T.tolist()
            histogram_y_transposed = np.array(histogram_y_all_files).T.tolist()
            histogram_P_transposed = np.array(histogram_P_all_files).T.tolist()
            for l in range(0,len(gatewidth_list)):
                current_gatewidth = gatewidth_list[l]
                print('Plotting all files histograms. Gate-width = ',current_gatewidth)
                current_x = histogram_x_transposed[l]
                current_y = histogram_y_transposed[l]
                current_P = histogram_P_transposed[l]
                if output_nested_subdirectories == True:
                    if plot_histograms == True:
                        plotHistogram_multi(file_descriptions, current_gatewidth, current_x, current_y, current_P, show=False, save=save_path+'All_Files\Histograms\Histogram_all_files_'+str(current_gatewidth), log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
                    else:
                        plotHistogram_multi(file_descriptions, current_gatewidth, current_x, current_y, current_P, show=False, save=False, log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
                else:
                    if plot_histograms == True:
                        plotHistogram_multi(file_descriptions, current_gatewidth, current_x, current_y, current_P, show=False, save=save_path+'Histogram_all_files_'+str(current_gatewidth), log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
                    else:
                        plotHistogram_multi(file_descriptions, current_gatewidth, current_x, current_y, current_P, show=False, save=False, log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
            print('Plotting all files histograms end')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
        
        # Plot Rossi from multiple files together
        if perform_Rossi == True:
            print('Plotting all Rossi files together (files = series, x-axis = Rossi time) start')
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'All_Files/Rossi/', '', current_file, add_current_file=False, make_dirs=True)
            
            plot_scatter_gatewidth(file_descriptions, 'Rossi', 'micro-sec', Rossi_times_all_files, Rossi_data_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
            if perform_Rossi_fits == True:
                plot_scatter_gatewidth(file_descriptions, 'Rossi', 'micro-sec', Rossi_times_all_files, Rossi_data_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, fit1=Rossi_fit1_results_all_files, fit2=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'Rossi', 'micro-sec', Rossi_times_all_files, Rossi_data_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_fit', mult_files=True, fit1=False, fit2=Rossi_fit2_results_all_files, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(file_descriptions, 'Rossi', 'micro-sec', Rossi_times_all_files, Rossi_data_all_files, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single+double_fit', mult_files=True, fit1=Rossi_fit1_results_all_files, fit2=Rossi_fit2_results_all_files, yaxis_log=yaxis_log)
        
                fit1lambda1 = [1/element for element in Rossi_1exp_B_all_files]
                fit1lambda1_unc = []
                for i in range(0,len(Rossi_1exp_B_unc_all_files)):
                    fit1lambda1_unc.append(Rossi_1exp_B_unc_all_files[i]/Rossi_1exp_B_all_files[i]**2)
                fit2lambda1 = [1/element for element in Rossi_2exp_B_all_files]
                fit2lambda1_unc = []
                for i in range(0,len(Rossi_2exp_B_unc_all_files)):
                    fit2lambda1_unc.append(Rossi_2exp_B_unc_all_files[i]/Rossi_2exp_B_all_files[i]**2)
                fit2lambda2 = [1/element for element in Rossi_2exp_D_all_files]
                fit2lambda2_unc = []
                for i in range(0,len(Rossi_2exp_D_unc_all_files)):
                    fit2lambda2_unc.append(Rossi_2exp_D_unc_all_files[i]/Rossi_2exp_D_all_files[i]**2)
                for k in range(0,len(file_number)):
                    plot_scatter('Configuration', 'A', file_number, Rossi_1exp_A_all_files, marker_size, y_unc=Rossi_1exp_A_unc_all_files, show=False, save=current_save_path+'_Rossi_fit1_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'B (alpha)', file_number, Rossi_1exp_B_all_files, marker_size, y_unc=Rossi_1exp_B_unc_all_files, show=False, save=current_save_path+'_Rossi_fit1_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'Inverse B (lambda)', file_number, fit1lambda1, marker_size, y_unc=fit1lambda1_unc, show=False, save=current_save_path+'_Rossi_fit1_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'C', file_number, Rossi_1exp_C_all_files, marker_size, y_unc=Rossi_1exp_C_unc_all_files, show=False, save=current_save_path+'_Rossi_fit1_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'A', file_number, Rossi_2exp_A_all_files, marker_size, y_unc=Rossi_2exp_A_unc_all_files, show=False, save=current_save_path+'_Rossi_fit2_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'B (alpha1)', file_number, Rossi_2exp_B_all_files, marker_size, y_unc=Rossi_2exp_B_unc_all_files, show=False, save=current_save_path+'_Rossi_fit2_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'Inverse B (lambda1)', file_number, fit2lambda1, marker_size, y_unc=fit2lambda1_unc, show=False, save=current_save_path+'_Rossi_fit2_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'C', file_number, Rossi_2exp_C_all_files, marker_size, y_unc=Rossi_2exp_C_unc_all_files, show=False, save=current_save_path+'_Rossi_fit2_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'D (alpha2)', file_number, Rossi_2exp_B_all_files, marker_size, y_unc=Rossi_2exp_B_unc_all_files, show=False, save=current_save_path+'_Rossi_fit2_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'Inverse D (lambda2)', file_number, fit2lambda2, marker_size, y_unc=fit2lambda2_unc, show=False, save=current_save_path+'_Rossi_fit2_', yaxis_log=yaxis_log)
                    plot_scatter('Configuration', 'E', file_number, Rossi_2exp_C_all_files, marker_size, y_unc=Rossi_2exp_C_unc_all_files, show=False, save=current_save_path+'_Rossi_fit2_', yaxis_log=yaxis_log)
                
                
                if output_csv == True:
                    
                    current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'All_Files/Rossi/', '', current_file, add_current_file=False, make_dirs=False)
                    
                    # Rossi data csv file
                    Rossi_header_row = ['Time (nsec)']
                    for fname in files:
                        Rossi_header_row.append(fname)
                    
                    Rossi_times_combined = Rossi_times_all_files[0]
                    temp = copy.copy(Rossi_data_all_files)
                    combined_columns = [Rossi_times_combined] + temp
                    
                    columns_data = zip_longest(*combined_columns)
                
                    with open(current_save_path+'Rossi_data.csv', mode='w', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(Rossi_header_row)
                        writer.writerows(columns_data)
                    
                    # Rossi fit csv file
                    with open(current_save_path+'Rossi_fits.csv', mode='w', newline='') as csv_file:
                        writer = csv.writer(csv_file)
                        writer.writerow(['Configuration #','File','File Description','1exp A','1exp A unc','1exp B','1exp B unc','1exp lambda (1/B)','1exp lambda unc','1exp C','1exp C unc','2exp A','2exp A unc','2exp B','2exp B unc','2exp lambda1 (1/B)','2exp lambda1 unc','2exp C','2exp C unc','2exp D','2exp D unc','2exp lambda2 (1/D)','2exp lambda2 unc','2exp E','2exp E unc'])
                        for value in range(len(file_number)):
                            if len(file_descriptions) > 0:
                                writer.writerow([file_number[value], files[value], file_descriptions[value], Rossi_1exp_A_all_files[value], Rossi_1exp_A_unc_all_files[value], Rossi_1exp_B_all_files[value], Rossi_1exp_B_unc_all_files[value], fit1lambda1[value], fit1lambda1_unc[value], Rossi_1exp_C_all_files[value], Rossi_1exp_C_unc_all_files[value], Rossi_2exp_A_all_files[value], Rossi_2exp_A_unc_all_files[value], Rossi_2exp_B_all_files[value], Rossi_2exp_B_unc_all_files[value], fit2lambda1[value], fit2lambda1_unc[value], Rossi_2exp_C_all_files[value], Rossi_2exp_C_unc_all_files[value], Rossi_2exp_D_all_files[value], Rossi_2exp_D_unc_all_files[value], fit2lambda2[value], fit2lambda2_unc[value], Rossi_2exp_E_all_files[value], Rossi_2exp_E_unc_all_files[value]])
                            else:
                                writer.writerow([file_number[value], files[value], '', Rossi_1exp_A_all_files[value], Rossi_1exp_A_unc_all_files[value], Rossi_1exp_B_all_files[value], Rossi_1exp_B_unc_all_files[value], fit1lambda1[value], fit1lambda1_unc[value], Rossi_1exp_C_all_files[value], Rossi_1exp_C_unc_all_files[value], Rossi_2exp_A_all_files[value], Rossi_2exp_A_unc_all_files[value], Rossi_2exp_B_all_files[value], Rossi_2exp_B_unc_all_files[value], fit2lambda1[value], fit2lambda1_unc[value], Rossi_2exp_C_all_files[value], Rossi_2exp_C_unc_all_files[value], Rossi_2exp_D_all_files[value], Rossi_2exp_D_unc_all_files[value], fit2lambda2[value], fit2lambda2_unc[value], Rossi_2exp_E_all_files[value], Rossi_2exp_E_unc_all_files[value]])
            
                
            print('Plotting all Rossi files together (files = series, x-axis = Rossi time) start')
         
        # plot all files together (x-axis = files)
        if plot_all_files_vs_con == True:
            print('Plotting all files together (x-axis = files) start')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'All_Files/Configurations/', '', current_file, add_current_file=False, make_dirs=True)
            
            gatewidth_transposed = np.array(gatewidth_all_files).T.tolist()
            m1_transposed = np.array(first_reduced_factorial_moment_all_files).T.tolist()
            m2_transposed = np.array(second_reduced_factorial_moment_all_files).T.tolist()
            m3_transposed = np.array(third_reduced_factorial_moment_all_files).T.tolist()
            m4_transposed = np.array(fourth_reduced_factorial_moment_all_files).T.tolist()
            C1_transposed = np.array(first_factorial_moment_all_files).T.tolist()
            C2_transposed = np.array(second_factorial_moment_all_files).T.tolist()
            C3_transposed = np.array(third_factorial_moment_all_files).T.tolist()
            C4_transposed = np.array(fourth_factorial_moment_all_files).T.tolist()
            Y1_transposed = np.array(Y1_all_files).T.tolist()
            dY1_transposed = np.array(dY1_all_files).T.tolist()
            R1_transposed = Y1_transposed
            dR1_transposed = dY1_transposed
            Y2_transposed = np.array(Y2_all_files).T.tolist()
            dY2_transposed = np.array(dY2_all_files).T.tolist()
            Ym_transposed = np.array(Ym_all_files).T.tolist()
            dYm_transposed = np.array(dYm_all_files).T.tolist()
            omega2_single_results_transposed = np.array(omega2_single_results_all_files).T.tolist()
            R2_single_Y2_decay_transposed = np.array(R2_single_Y2_decay_all_files).T.tolist()
            R2_unc_single_Y2_decay_transposed = np.array(R2_unc_single_Y2_decay_all_files).T.tolist()
            omega2_double1_results_transposed = np.array(omega2_double1_results_all_files).T.tolist()
            R2_double1_Y2_decay_transposed = np.array(R2_double1_Y2_decay_all_files).T.tolist()
            R2_unc_double1_Y2_decay_transposed = np.array(R2_unc_double1_Y2_decay_all_files).T.tolist()
            omega2_double2_results_transposed = np.array(omega2_double2_results_all_files).T.tolist()
            R2_double2_Y2_decay_transposed = np.array(R2_double2_Y2_decay_all_files).T.tolist()
            R2_unc_double2_Y2_decay_transposed = np.array(R2_unc_double2_Y2_decay_all_files).T.tolist()
            R2_double_both_Y2_decay_transposed = np.array(R2_double_both_Y2_decay_all_files).T.tolist()
            R2_unc_double_both_Y2_decay_transposed = np.array(R2_unc_double_both_Y2_decay_all_files).T.tolist()
            omega2_lifetime_user_results_transposed = np.array(omega2_lifetime_user_results_all_files).T.tolist()
            R2_user_lifetime_transposed = np.array(R2_user_lifetime_all_files).T.tolist()
            R2_unc_user_lifetime_transposed = np.array(R2_unc_user_lifetime_all_files).T.tolist()
            if calculation_type == 'Cf':
                calc_eff_kn_transposed = np.array(calc_eff_kn_all_files).T.tolist()
                calc_eff_unc_kn_transposed = np.array(calc_eff_unc_kn_all_files).T.tolist()
            elif calculation_type == 'Multiplicity':
                dR1R2_transposed = np.array(dR1R2_all_files).T.tolist()
                if perform_Y2_single_fit == True:
                    a1_single_transposed = np.array(a1_single_all_files).T.tolist()
                    a2_single_transposed = np.array(a2_single_all_files).T.tolist()
                    a3_single_transposed = np.array(a3_single_all_files).T.tolist()
                    a4_single_transposed = np.array(a4_single_all_files).T.tolist()
                    a5_single_transposed = np.array(a5_single_all_files).T.tolist()
                    a6_single_transposed = np.array(a6_single_all_files).T.tolist()
                    a7_single_transposed = np.array(a7_single_all_files).T.tolist()
                    Ml_single_transposed = np.array(Ml_single_all_files).T.tolist()
                    dMl_single_transposed = np.array(dMl_single_all_files).T.tolist()
                    dMldR1_single_transposed = np.array(dMldR1_single_all_files).T.tolist()
                    dMldR2_single_transposed = np.array(dMldR2_single_all_files).T.tolist()
                    dMldeff_single_transposed = np.array(dMldeff_single_all_files).T.tolist()
                    Mt_single_transposed = np.array(Mt_single_all_files).T.tolist()
                    dMt_single_transposed = np.array(dMt_single_all_files).T.tolist()
                    Fs_single_transposed = np.array(Fs_single_all_files).T.tolist()
                    dFs_single_transposed = np.array(dFs_single_all_files).T.tolist()
                    dFsdR1_single_transposed = np.array(dFsdR1_single_all_files).T.tolist()
                    dFsdR2_single_transposed = np.array(dFsdR2_single_all_files).T.tolist()
                    dFsdeff_single_transposed = np.array(dFsdeff_single_all_files).T.tolist()
                    kp_single_transposed = np.array(kp_single_all_files).T.tolist()
                    dkp_single_transposed = np.array(dkp_single_all_files).T.tolist()
                    keff_single_transposed = np.array(keff_single_all_files).T.tolist()
                    dkeff_single_transposed = np.array(dkeff_single_all_files).T.tolist()
                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                    a1_double1_transposed = np.array(a1_double1_all_files).T.tolist()
                    a2_double1_transposed = np.array(a2_double1_all_files).T.tolist()
                    a3_double1_transposed = np.array(a3_double1_all_files).T.tolist()
                    a4_double1_transposed = np.array(a4_double1_all_files).T.tolist()
                    a5_double1_transposed = np.array(a5_double1_all_files).T.tolist()
                    a6_double1_transposed = np.array(a6_double1_all_files).T.tolist()
                    a7_double1_transposed = np.array(a7_double1_all_files).T.tolist()
                    Ml_double1_transposed = np.array(Ml_double1_all_files).T.tolist()
                    dMl_double1_transposed = np.array(dMl_double1_all_files).T.tolist()
                    dMldR1_double1_transposed = np.array(dMldR1_double1_all_files).T.tolist()
                    dMldR2_double1_transposed = np.array(dMldR2_double1_all_files).T.tolist()
                    dMldeff_double1_transposed = np.array(dMldeff_double1_all_files).T.tolist()
                    Mt_double1_transposed = np.array(Mt_double1_all_files).T.tolist()
                    dMt_double1_transposed = np.array(dMt_double1_all_files).T.tolist()
                    Fs_double1_transposed = np.array(Fs_double1_all_files).T.tolist()
                    dFs_double1_transposed = np.array(dFs_double1_all_files).T.tolist()
                    dFsdR1_double1_transposed = np.array(dFsdR1_double1_all_files).T.tolist()
                    dFsdR2_double1_transposed = np.array(dFsdR2_double1_all_files).T.tolist()
                    dFsdeff_double1_transposed = np.array(dFsdeff_double1_all_files).T.tolist()
                    kp_double1_transposed = np.array(kp_double1_all_files).T.tolist()
                    dkp_double1_transposed = np.array(dkp_double1_all_files).T.tolist()
                    keff_double1_transposed = np.array(keff_double1_all_files).T.tolist()
                    dkeff_double1_transposed = np.array(dkeff_double1_all_files).T.tolist()
                    a1_double2_transposed = np.array(a1_double2_all_files).T.tolist()
                    a2_double2_transposed = np.array(a2_double2_all_files).T.tolist()
                    a3_double2_transposed = np.array(a3_double2_all_files).T.tolist()
                    a4_double2_transposed = np.array(a4_double2_all_files).T.tolist()
                    a5_double2_transposed = np.array(a5_double2_all_files).T.tolist()
                    a6_double2_transposed = np.array(a6_double2_all_files).T.tolist()
                    a7_double2_transposed = np.array(a7_double2_all_files).T.tolist()
                    Ml_double2_transposed = np.array(Ml_double2_all_files).T.tolist()
                    dMl_double2_transposed = np.array(dMl_double2_all_files).T.tolist()
                    dMldR1_double2_transposed = np.array(dMldR1_double2_all_files).T.tolist()
                    dMldR2_double2_transposed = np.array(dMldR2_double2_all_files).T.tolist()
                    dMldeff_double2_transposed = np.array(dMldeff_double2_all_files).T.tolist()
                    Mt_double2_transposed = np.array(Mt_double2_all_files).T.tolist()
                    dMt_double2_transposed = np.array(dMt_double2_all_files).T.tolist()
                    Fs_double2_transposed = np.array(Fs_double2_all_files).T.tolist()
                    dFs_double2_transposed = np.array(dFs_double2_all_files).T.tolist()
                    dFsdR1_double2_transposed = np.array(dFsdR1_double2_all_files).T.tolist()
                    dFsdR2_double2_transposed = np.array(dFsdR2_double2_all_files).T.tolist()
                    dFsdeff_double2_transposed = np.array(dFsdeff_double2_all_files).T.tolist()
                    kp_double2_transposed = np.array(kp_double2_all_files).T.tolist()
                    dkp_double2_transposed = np.array(dkp_double2_all_files).T.tolist()
                    keff_double2_transposed = np.array(keff_double2_all_files).T.tolist()
                    dkeff_double2_transposed = np.array(dkeff_double2_all_files).T.tolist()
                    a1_double_both_transposed = np.array(a1_double_both_all_files).T.tolist()
                    a2_double_both_transposed = np.array(a2_double_both_all_files).T.tolist()
                    a3_double_both_transposed = np.array(a3_double_both_all_files).T.tolist()
                    a4_double_both_transposed = np.array(a4_double_both_all_files).T.tolist()
                    a5_double_both_transposed = np.array(a5_double_both_all_files).T.tolist()
                    a6_double_both_transposed = np.array(a6_double_both_all_files).T.tolist()
                    a7_double_both_transposed = np.array(a7_double_both_all_files).T.tolist()
                    Ml_double_both_transposed = np.array(Ml_double_both_all_files).T.tolist()
                    dMl_double_both_transposed = np.array(dMl_double_both_all_files).T.tolist()
                    dMldR1_double_both_transposed = np.array(dMldR1_double_both_all_files).T.tolist()
                    dMldR2_double_both_transposed = np.array(dMldR2_double_both_all_files).T.tolist()
                    dMldeff_double_both_transposed = np.array(dMldeff_double_both_all_files).T.tolist()
                    Mt_double_both_transposed = np.array(Mt_double_both_all_files).T.tolist()
                    dMt_double_both_transposed = np.array(dMt_double_both_all_files).T.tolist()
                    Fs_double_both_transposed = np.array(Fs_double_both_all_files).T.tolist()
                    dFs_double_both_transposed = np.array(dFs_double_both_all_files).T.tolist()
                    dFsdR1_double_both_transposed = np.array(dFsdR1_double_both_all_files).T.tolist()
                    dFsdR2_double_both_transposed = np.array(dFsdR2_double_both_all_files).T.tolist()
                    dFsdeff_double_both_transposed = np.array(dFsdeff_double_both_all_files).T.tolist()
                    kp_double_both_transposed = np.array(kp_double_both_all_files).T.tolist()
                    dkp_double_both_transposed = np.array(dkp_double_both_all_files).T.tolist()
                    keff_double_both_transposed = np.array(keff_double_both_all_files).T.tolist()
                    dkeff_double_both_transposed = np.array(dkeff_double_both_all_files).T.tolist()
                if use_user_specified_lifetime == True:
                    a1_user_lifetime_transposed = np.array(a1_user_lifetime_all_files).T.tolist()
                    a2_user_lifetime_transposed = np.array(a2_user_lifetime_all_files).T.tolist()
                    a3_user_lifetime_transposed = np.array(a3_user_lifetime_all_files).T.tolist()
                    a4_user_lifetime_transposed = np.array(a4_user_lifetime_all_files).T.tolist()
                    a5_user_lifetime_transposed = np.array(a5_user_lifetime_all_files).T.tolist()
                    a6_user_lifetime_transposed = np.array(a6_user_lifetime_all_files).T.tolist()
                    a7_user_lifetime_transposed = np.array(a7_user_lifetime_all_files).T.tolist()
                    Ml_user_lifetime_transposed = np.array(Ml_user_lifetime_all_files).T.tolist()
                    dMl_user_lifetime_transposed = np.array(dMl_user_lifetime_all_files).T.tolist()
                    dMldR1_user_lifetime_transposed = np.array(dMldR1_user_lifetime_all_files).T.tolist()
                    dMldR2_user_lifetime_transposed = np.array(dMldR2_user_lifetime_all_files).T.tolist()
                    dMldeff_user_lifetime_transposed = np.array(dMldeff_user_lifetime_all_files).T.tolist()
                    Mt_user_lifetime_transposed = np.array(Mt_user_lifetime_all_files).T.tolist()
                    dMt_user_lifetime_transposed = np.array(dMt_user_lifetime_all_files).T.tolist()
                    Fs_user_lifetime_transposed = np.array(Fs_user_lifetime_all_files).T.tolist()
                    dFs_user_lifetime_transposed = np.array(dFs_user_lifetime_all_files).T.tolist()
                    dFsdR1_user_lifetime_transposed = np.array(dFsdR1_user_lifetime_all_files).T.tolist()
                    dFsdR2_user_lifetime_transposed = np.array(dFsdR2_user_lifetime_all_files).T.tolist()
                    dFsdeff_user_lifetime_transposed = np.array(dFsdeff_user_lifetime_all_files).T.tolist()
                    kp_user_lifetime_transposed = np.array(kp_user_lifetime_all_files).T.tolist()
                    dkp_user_lifetime_transposed = np.array(dkp_user_lifetime_all_files).T.tolist()
                    keff_user_lifetime_transposed = np.array(keff_user_lifetime_all_files).T.tolist()
                    dkeff_user_lifetime_transposed = np.array(dkeff_user_lifetime_all_files).T.tolist()
            
            for k in range(0,len(gatewidth_transposed)):
                current_gatewidth = gatewidth_transposed[k]
                print('Plotting all files together (x-axis = files). Gate-width = ',current_gatewidth)
                current_m1 = m1_transposed[k]
                current_m2 = m2_transposed[k]
                current_m3 = m3_transposed[k]
                current_m4 = m4_transposed[k]
                current_C1 = C1_transposed[k]
                current_C2 = C2_transposed[k]
                current_C3 = C3_transposed[k]
                current_C4 = C4_transposed[k]
                current_Y1 = Y1_transposed[k]
                current_dY1 = dY1_transposed[k]
                current_R1 = R1_transposed[k]
                current_dR1 = dR1_transposed[k]
                current_Y2 = Y2_transposed[k]
                current_dY2 = dY2_transposed[k]
                current_Ym = Ym_transposed[k]
                current_dYm = dYm_transposed[k]
                current_R2_single_Y2_decay = R2_single_Y2_decay_transposed[k]
                current_R2_unc_single_Y2_decay = R2_unc_single_Y2_decay_transposed[k]
                current_R2_double1_Y2_decay = R2_double1_Y2_decay_transposed[k]
                current_R2_unc_double1_Y2_decay = R2_unc_double1_Y2_decay_transposed[k]
                current_R2_double2_Y2_decay = R2_double2_Y2_decay_transposed[k]
                current_R2_unc_double2_Y2_decay = R2_unc_double2_Y2_decay_transposed[k]
                current_R2_double_both_Y2_decay = R2_double_both_Y2_decay_transposed[k]
                current_R2_unc_double_both_Y2_decay = R2_unc_double_both_Y2_decay_transposed[k]
                current_R2_user_lifetime = R2_user_lifetime_transposed[k]
                current_R2_unc_user_lifetime = R2_unc_user_lifetime_transposed[k]
                if input_type != '.csv':
                    current_omega2_single = omega2_single_results_transposed[k]
                    current_omega2_double1 = omega2_double1_results_transposed[k]
                    current_omega2_double2 = omega2_double2_results_transposed[k]
                    current_omega2_lifetime_user = omega2_lifetime_user_results_transposed[k]
                if calculation_type == 'Cf':
                    current_calc_eff_kn = calc_eff_kn_transposed[k]
                    current_calc_eff_unc_kn = calc_eff_unc_kn_transposed[k]
                elif calculation_type == 'Multiplicity':
                    if perform_Y2_single_fit == True:
                        current_Ml_single = Ml_single_transposed[k]
                        current_dMl_single = dMl_single_transposed[k]
                        current_Mt_single = Mt_single_transposed[k]
                        current_dMt_single = dMt_single_transposed[k]
                        current_Fs_single = Fs_single_transposed[k]
                        current_dFs_single = dFs_single_transposed[k]
                        current_kp_single = kp_single_transposed[k]
                        current_dkp_single = dkp_single_transposed[k]
                        current_keff_single = keff_single_transposed[k]
                        current_dkeff_single = dkeff_single_transposed[k]
                    if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                        current_Ml_double1 = Ml_double1_transposed[k]
                        current_dMl_double1 = dMl_double1_transposed[k]
                        current_Mt_double1 = Mt_double1_transposed[k]
                        current_dMt_double1 = dMt_double1_transposed[k]
                        current_Fs_double1 = Fs_double1_transposed[k]
                        current_dFs_double1 = dFs_double1_transposed[k]
                        current_kp_double1 = kp_double1_transposed[k]
                        current_dkp_double1 = dkp_double1_transposed[k]
                        current_keff_double1 = keff_double1_transposed[k]
                        current_dkeff_double1 = dkeff_double1_transposed[k]
                        current_Ml_double2 = Ml_double2_transposed[k]
                        current_dMl_double2 = dMl_double2_transposed[k]
                        current_Mt_double2 = Mt_double2_transposed[k]
                        current_dMt_double2 = dMt_double2_transposed[k]
                        current_Fs_double2 = Fs_double2_transposed[k]
                        current_dFs_double2 = dFs_double2_transposed[k]
                        current_kp_double2 = kp_double2_transposed[k]
                        current_dkp_double2 = dkp_double2_transposed[k]
                        current_keff_double2 = keff_double2_transposed[k]
                        current_dkeff_double2 = dkeff_double2_transposed[k]
                        current_Ml_double_both = Ml_double_both_transposed[k]
                        current_dMl_double_both = dMl_double_both_transposed[k]
                        current_Mt_double_both = Mt_double_both_transposed[k]
                        current_dMt_double_both = dMt_double_both_transposed[k]
                        current_Fs_double_both = Fs_double_both_transposed[k]
                        current_dFs_double_both = dFs_double_both_transposed[k]
                        current_kp_double_both = kp_double_both_transposed[k]
                        current_dkp_double_both = dkp_double_both_transposed[k]
                        current_keff_double_both = keff_double_both_transposed[k]
                        current_dkeff_double_both = dkeff_double_both_transposed[k]
                    if use_user_specified_lifetime == True:
                        current_Ml_user_lifetime = Ml_user_lifetime_transposed[k]
                        current_dMl_user_lifetime = dMl_user_lifetime_transposed[k]
                        current_Mt_user_lifetime = Mt_user_lifetime_transposed[k]
                        current_dMt_user_lifetime = dMt_user_lifetime_transposed[k]
                        current_Fs_user_lifetime = Fs_user_lifetime_transposed[k]
                        current_dFs_user_lifetime = dFs_user_lifetime_transposed[k]
                        current_kp_user_lifetime = kp_user_lifetime_transposed[k]
                        current_dkp_user_lifetime = dkp_user_lifetime_transposed[k]
                        current_keff_user_lifetime = keff_user_lifetime_transposed[k]
                        current_dkeff_user_lifetime = dkeff_user_lifetime_transposed[k]
        
                if combine_statistical_plots != True:
                    if user_gatewidths_plot_all_files_vs_con != True or (user_gatewidths_plot_all_files_vs_con == True and current_gatewidth[0] in plot_all_files_vs_con_gatewidth_list):
                        plot_scatter('Configuration', 'm1', file_number, current_m1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'm2', file_number, current_m2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'm3', file_number, current_m3, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'm4', file_number, current_m4, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'C1', file_number, current_C1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'C2', file_number, current_C2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'C3', file_number, current_C3, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'C4', file_number, current_C4, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'Y1', file_number, current_Y1, marker_size, y_unc=current_dY1, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'dY1', file_number, current_dY1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'R1', file_number, current_R1, marker_size, y_unc=current_dR1, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'dR1', file_number, current_dR1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'Y2', file_number, current_Y2, marker_size, y_unc=current_dY2, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'dY2', file_number, current_dY2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'Ym', file_number, current_Ym, marker_size, y_unc=current_dYm, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'dYm', file_number, current_dYm, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        if perform_Y2_single_fit == True:
                            if input_type != '.csv':
                                plot_scatter('Configuration', 'omega2', file_number, current_omega2_single, marker_size, y_unc=None, show=False, save=current_save_path+'_single'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'R2', file_number, current_R2_single_Y2_decay, marker_size, y_unc=current_R2_unc_single_Y2_decay, show=False, save=current_save_path+'_single'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'dR2', file_number, current_R2_unc_single_Y2_decay, marker_size, y_unc=None, show=False, save=current_save_path+'_single'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                            if input_type != '.csv':
                                plot_scatter('Configuration', 'omega2', file_number, current_omega2_double1, marker_size, y_unc=None, show=False, save=current_save_path+'_double1'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                                plot_scatter('Configuration', 'omega2', file_number, current_omega2_double2, marker_size, y_unc=None, show=False, save=current_save_path+'_double2'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'R2', file_number, current_R2_double1_Y2_decay, marker_size, y_unc=current_R2_unc_double1_Y2_decay, show=False, save=current_save_path+'_double1'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'dR2', file_number, current_R2_unc_double1_Y2_decay, marker_size, y_unc=None, show=False, save=current_save_path+'_double1'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'R2', file_number, current_R2_double2_Y2_decay, marker_size, y_unc=current_R2_unc_double2_Y2_decay, show=False, save=current_save_path+'_double2'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'dR2', file_number, current_R2_unc_double2_Y2_decay, marker_size, y_unc=None, show=False, save=current_save_path+'_double2'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'R2', file_number, current_R2_double_both_Y2_decay, marker_size, y_unc=current_R2_unc_double_both_Y2_decay, show=False, save=current_save_path+'_double_both'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'dR2', file_number, current_R2_unc_double_both_Y2_decay, marker_size, y_unc=None, show=False, save=current_save_path+'_double_both'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                        if use_user_specified_lifetime == True:
                            if input_type != '.csv':
                                plot_scatter('Configuration', 'omega2', file_number, current_omega2_lifetime_user, marker_size, y_unc=None, show=False, save=current_save_path+'_user_lifetime'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'R2', file_number, current_R2_user_lifetime, marker_size, y_unc=current_R2_unc_user_lifetime, show=False, save=current_save_path+'_user_lifetime'+str(current_gatewidth[0]), yaxis_log=yaxis_log)
                            plot_scatter('Configuration', 'dR2', file_number, current_R2_unc_user_lifetime, marker_size, y_unc=None, show=False, save=current_save_path+'_user_lifetime'+str(current_gatewidth[0]), yaxis_log=yaxis_log)  
                        if calculation_type == 'Cf':
                            plot_scatter('Configuration', 'Efficiency', file_number, current_calc_eff_kn, marker_size, y_unc=current_calc_eff_unc_kn, show=False, save=current_save_path+str(current_gatewidth[0]))
                            plot_scatter('Configuration', 'dEfficiency', file_number, current_calc_eff_unc_kn, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0]))
                        elif calculation_type == 'Multiplicity':
                            if perform_Y2_single_fit == True:
                                plot_scatter('Configuration', 'Ml', file_number, current_Ml_single, marker_size, y_unc=current_dMl_single, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'dMl', file_number, current_dMl_single, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'Fs', file_number, current_Fs_single, marker_size, y_unc=current_dFs_single, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'dFs', file_number, current_dFs_single, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'Mt', file_number, current_Mt_single, marker_size, y_unc=current_dMt_single, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'dMt', file_number, current_dMt_single, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'kp', file_number, current_kp_single, marker_size, y_unc=current_dkp_single, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'dkp', file_number, current_dkp_single, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'keff', file_number, current_keff_single, marker_size, y_unc=current_dkeff_single, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                                plot_scatter('Configuration', 'dkeff', file_number, current_dkeff_single, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_single_fit')
                            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                plot_scatter('Configuration', 'Ml', file_number, current_Ml_double1, marker_size, y_unc=current_dMl_double1, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'dMl', file_number, current_dMl_double1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'Fs', file_number, current_Fs_double1, marker_size, y_unc=current_dFs_double1, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'dFs', file_number, current_dFs_double1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'Mt', file_number, current_Mt_double1, marker_size, y_unc=current_dMt_double1, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'dMt', file_number, current_dMt_double1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'kp', file_number, current_kp_double1, marker_size, y_unc=current_dkp_double1, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'dkp', file_number, current_dkp_double1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'keff', file_number, current_keff_double1, marker_size, y_unc=current_dkeff_double1, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'dkeff', file_number, current_dkeff_double1, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double1_fit')
                                plot_scatter('Configuration', 'Ml', file_number, current_Ml_double2, marker_size, y_unc=current_dMl_double2, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'dMl', file_number, current_dMl_double2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'Fs', file_number, current_Fs_double2, marker_size, y_unc=current_dFs_double2, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'dFs', file_number, current_dFs_double2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'Mt', file_number, current_Mt_double2, marker_size, y_unc=current_dMt_double2, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'dMt', file_number, current_dMt_double2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'kp', file_number, current_kp_double2, marker_size, y_unc=current_dkp_double2, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'dkp', file_number, current_dkp_double2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'keff', file_number, current_keff_double2, marker_size, y_unc=current_dkeff_double2, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'dkeff', file_number, current_dkeff_double2, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double2_fit')
                                plot_scatter('Configuration', 'Ml', file_number, current_Ml_double_both, marker_size, y_unc=current_dMl_double_both, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'dMl', file_number, current_dMl_double_both, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'Fs', file_number, current_Fs_double_both, marker_size, y_unc=current_dFs_double_both, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'dFs', file_number, current_dFs_double_both, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'Mt', file_number, current_Mt_double_both, marker_size, y_unc=current_dMt_double_both, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'dMt', file_number, current_dMt_double_both, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'kp', file_number, current_kp_double_both, marker_size, y_unc=current_dkp_double_both, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'dkp', file_number, current_dkp_double_both, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'keff', file_number, current_keff_double_both, marker_size, y_unc=current_dkeff_double_both, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')
                                plot_scatter('Configuration', 'dkeff', file_number, current_dkeff_double_both, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_double_both_fit')                      
                            if use_user_specified_lifetime == True:
                                plot_scatter('Configuration', 'Ml', file_number, current_Ml_user_lifetime, marker_size, y_unc=current_dMl_user_lifetime, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'dMl', file_number, current_dMl_user_lifetime, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'Fs', file_number, current_Fs_user_lifetime, marker_size, y_unc=current_dFs_user_lifetime, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'dFs', file_number, current_dFs_user_lifetime, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'Mt', file_number, current_Mt_user_lifetime, marker_size, y_unc=current_dMt_user_lifetime, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'dMt', file_number, current_dMt_user_lifetime, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'kp', file_number, current_kp_user_lifetime, marker_size, y_unc=current_dkp_user_lifetime, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'dkp', file_number, current_dkp_user_lifetime, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'keff', file_number, current_keff_user_lifetime, marker_size, y_unc=current_dkeff_user_lifetime, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                plot_scatter('Configuration', 'dkeff', file_number, current_dkeff_user_lifetime, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth[0])+'_user_lifetime_fit')
                                
                        if output_csv == True:
                            
                            # set N/A to lists if fits were not performed
                            if perform_Y2_single_fit != True:
                                current_omega2_single = current_R2_single_Y2_decay = current_R2_unc_single_Y2_decay = ['N/A' for i in range(0,len(file_number))]
                            if perform_Y2_double_fit != True or perform_Y2_double_fit_continue != True:
                                current_omega2_double1 = current_R2_double1_Y2_decay = current_R2_unc_double1_Y2_decay = current_omega2_double2 = current_R2_double2_Y2_decay = current_R2_unc_double2_Y2_decay = current_R2_double_both_Y2_decay = current_R2_unc_double_both_Y2_decay = ['N/A' for i in range(0,len(file_number))]
                            if use_user_specified_lifetime != True:
                                current_omega2_lifetime_user = current_R2_user_lifetime = current_R2_unc_user_lifetime = ['N/A' for i in range(0,len(file_number))]
                            
                            with open(current_save_path+str(current_gatewidth[0])+'.csv', mode='w', newline='') as csv_file:
                                writer = csv.writer(csv_file)
                                header_row = ['Configuration #','File','File Description','m1','m2','m3','m4','C1','C2','C3','C4','Y1','dY1','Y2','dY2','R1','dR1','omega2_single_results','R2_single_Y2_decay','R2_unc_single_Y2_decay','omega2_double1_results','R2_double1_Y2_decay','R2_unc_double1_Y2_decay','omega2_double2_results','R2_double2_Y2_decay','R2_unc_double2_Y2_decay','R2_double_both_Y2_decay','R2_unc_double_both_Y2_decay','omega2_lifetime_user','R2_user_lifetime','R2_unc_user_lifetime','Ym','dYm']
                                if calculation_type == 'Cf':
                                    header_row.append('eff from Cf')
                                    header_row.append('deff from Cf')
                                elif calculation_type == 'Multiplicity':
                                    if perform_Y2_single_fit == True:
                                        header_row.append('Ml_single')
                                        header_row.append('dMl_single')
                                        header_row.append('Mt_single')
                                        header_row.append('dMt_single')
                                        header_row.append('Fs_single')
                                        header_row.append('dFs_single')
                                        header_row.append('kp_single')
                                        header_row.append('dkp_single')
                                        header_row.append('keff_single')
                                        header_row.append('dkeff_single')
                                    if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                        header_row.append('Ml_double1')
                                        header_row.append('dMl_double1')
                                        header_row.append('Mt_double1')
                                        header_row.append('dMt_double1')
                                        header_row.append('Fs_double1')
                                        header_row.append('dFs_double1')
                                        header_row.append('kp_double1')
                                        header_row.append('dkp_double1')
                                        header_row.append('keff_double1')
                                        header_row.append('dkeff_double1')
                                        header_row.append('Ml_double2')
                                        header_row.append('dMl_double2')
                                        header_row.append('Mt_double2')
                                        header_row.append('dMt_double2')
                                        header_row.append('Fs_double2')
                                        header_row.append('dFs_double2')
                                        header_row.append('kp_double2')
                                        header_row.append('dkp_double2')
                                        header_row.append('keff_double2')
                                        header_row.append('dkeff_double2')
                                        header_row.append('Ml_double_both')
                                        header_row.append('dMl_double_both')
                                        header_row.append('Mt_double_both')
                                        header_row.append('dMt_double_both')
                                        header_row.append('Fs_double_both')
                                        header_row.append('dFs_double_both')
                                        header_row.append('kp_double_both')
                                        header_row.append('dkp_double_both')
                                        header_row.append('keff_double_both')
                                        header_row.append('dkeff_double_both')
                                    if use_user_specified_lifetime == True:
                                        header_row.append('Ml_user_lifetime')
                                        header_row.append('dMl_user_lifetime')
                                        header_row.append('Mt_user_lifetime')
                                        header_row.append('dMt_user_lifetime')
                                        header_row.append('Fs_user_lifetime')
                                        header_row.append('dFs_user_lifetime')
                                        header_row.append('kp_user_lifetime')
                                        header_row.append('dkp_user_lifetime')
                                        header_row.append('keff_user_lifetime')
                                        header_row.append('dkeff_user_lifetime')
                                    
                                writer.writerow(header_row)
                                for value in range(len(file_number)):
                                    if len(file_descriptions) > 0:
                                        data_row = [file_number[value], files[value], file_descriptions[value], current_m1[value], current_m2[value], current_m3[value], current_m4[value], current_C1[value], current_C2[value], current_C3[value], current_C4[value], current_Y1[value], current_dY1[value], current_Y2[value], current_dY2[value], current_R1[value], current_dR1[value], current_omega2_single[value], current_R2_single_Y2_decay[value], current_R2_unc_single_Y2_decay[value], current_omega2_double1[value], current_R2_double1_Y2_decay[value], current_R2_unc_double1_Y2_decay[value], current_omega2_double2[value], current_R2_double2_Y2_decay[value], current_R2_unc_double2_Y2_decay[value], current_R2_double_both_Y2_decay[value], current_R2_unc_double_both_Y2_decay[value], current_omega2_lifetime_user[value], current_R2_user_lifetime[value], current_R2_unc_user_lifetime[value], current_Ym[value], current_dYm[value]]
                                    else:
                                        data_row = [file_number[value], files[value], '', current_m1[value], current_m2[value], current_m3[value], current_m4[value], current_C1[value], current_C2[value], current_C3[value], current_C4[value], current_Y1[value], current_dY1[value], current_Y2[value], current_dY2[value], current_R1[value], current_dR1[value], current_omega2_single[value], current_R2_single_Y2_decay[value], current_R2_unc_single_Y2_decay[value], current_omega2_double1[value], current_R2_double1_Y2_decay[value], current_R2_unc_double1_Y2_decay[value], current_omega2_double2[value], current_R2_double2_Y2_decay[value], current_R2_unc_double2_Y2_decay[value], current_R2_double_both_Y2_decay[value], current_R2_unc_double_both_Y2_decay[value], current_omega2_lifetime_user[value], current_R2_user_lifetime[value], current_R2_unc_user_lifetime[value], current_Ym[value], current_dYm[value]]
                                    if calculation_type == 'Cf':
                                        data_row.append(current_calc_eff_kn[value])
                                        data_row.append(current_calc_eff_unc_kn[value])
                                    
                                    elif calculation_type == 'Multiplicity':
                                        if perform_Y2_single_fit == True:
                                            data_row.append(current_Ml_single[value])
                                            data_row.append(current_dMl_single[value])
                                            data_row.append(current_Mt_single[value])
                                            data_row.append(current_dMt_single[value])
                                            data_row.append(current_Fs_single[value])
                                            data_row.append(current_dFs_single[value])
                                            data_row.append(current_kp_single[value])
                                            data_row.append(current_dkp_single[value])
                                            data_row.append(current_keff_single[value])
                                            data_row.append(current_dkeff_single[value])
                                        if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                            data_row.append(current_Ml_double1[value])
                                            data_row.append(current_dMl_double1[value])
                                            data_row.append(current_Mt_double1[value])
                                            data_row.append(current_dMt_double1[value])
                                            data_row.append(current_Fs_double1[value])
                                            data_row.append(current_dFs_double1[value])
                                            data_row.append(current_kp_double1[value])
                                            data_row.append(current_dkp_double1[value])
                                            data_row.append(current_keff_double1[value])
                                            data_row.append(current_dkeff_double1[value])
                                            data_row.append(current_Ml_double2[value])
                                            data_row.append(current_dMl_double2[value])
                                            data_row.append(current_Mt_double2[value])
                                            data_row.append(current_dMt_double2[value])
                                            data_row.append(current_Fs_double2[value])
                                            data_row.append(current_dFs_double2[value])
                                            data_row.append(current_kp_double2[value])
                                            data_row.append(current_dkp_double2[value])
                                            data_row.append(current_keff_double2[value])
                                            data_row.append(current_dkeff_double2[value])
                                            data_row.append(current_Ml_double_both[value])
                                            data_row.append(current_dMl_double_both[value])
                                            data_row.append(current_Mt_double_both[value])
                                            data_row.append(current_dMt_double_both[value])
                                            data_row.append(current_Fs_double_both[value])
                                            data_row.append(current_dFs_double_both[value])
                                            data_row.append(current_kp_double_both[value])
                                            data_row.append(current_dkp_double_both[value])
                                            data_row.append(current_keff_double_both[value])
                                            data_row.append(current_dkeff_double_both[value])
                                        if use_user_specified_lifetime == True:
                                            data_row.append(current_Ml_user_lifetime[value])
                                            data_row.append(current_dMl_user_lifetime[value])
                                            data_row.append(current_Mt_user_lifetime[value])
                                            data_row.append(current_dMt_user_lifetime[value])
                                            data_row.append(current_Fs_user_lifetime[value])
                                            data_row.append(current_dFs_user_lifetime[value])
                                            data_row.append(current_kp_user_lifetime[value])
                                            data_row.append(current_dkp_user_lifetime[value])
                                            data_row.append(current_keff_user_lifetime[value])
                                            data_row.append(current_dkeff_user_lifetime[value])
                                    writer.writerow(data_row)
            
            if input_type != '.csv':
                for k in range(0,len(file_number)):
                    if perform_Y2_single_fit == True:
                        plot_scatter('Configuration', 'A', file_number, fit1log_A_all_files, marker_size, y_unc=fit1log_A_unc_all_files, show=False, save=current_save_path+'_Y2_fit1_', yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'B', file_number, fit1log_B_all_files, marker_size, y_unc=fit1log_B_unc_all_files, show=False, save=current_save_path+'_Y2_fit1_', yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'lambda', file_number, fit1log_det_lifetime_all_files, marker_size, y_unc=fit1log_det_lifetime_unc_all_files, show=False, save=current_save_path+'_Y2_fit1_', yaxis_log=yaxis_log)
                    if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                        plot_scatter('Configuration', 'A', file_number, fit2log_A_all_files, marker_size, y_unc=fit2log_A_unc_all_files, show=False, save=current_save_path+'_Y2_fit2_', yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'B', file_number, fit2log_B_all_files, marker_size, y_unc=fit2log_B_unc_all_files, show=False, save=current_save_path+'_Y2_fit2_', yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'lambda1', file_number, fit2log_det_lifetime1_all_files, marker_size, y_unc=fit2log_det_lifetime1_unc_all_files, show=False, save=current_save_path+'_Y2_fit2_', yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'C', file_number, fit2log_C_all_files, marker_size, y_unc=fit2log_C_unc_all_files, show=False, save=current_save_path+'_Y2_fit2_', yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'D', file_number, fit2log_D_all_files, marker_size, y_unc=fit2log_D_unc_all_files, show=False, save=current_save_path+'_Y2_fit2_', yaxis_log=yaxis_log)
                        plot_scatter('Configuration', 'lambda2', file_number, fit2log_det_lifetime2_all_files, marker_size, y_unc=fit2log_det_lifetime2_unc_all_files, show=False, save=current_save_path+'_Y2_fit2_', yaxis_log=yaxis_log)
                
            print('Plotting all files together (x-axis = files) end')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
    
        
        # this sums Feynman histograms and performs subsequent analysis    
        if sum_Feynman_histograms == True:
            
            print('Start sum Feynman histograms')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Histogram_Sum/', '', current_file, add_current_file=False, make_dirs=True)   
            sum_histograms_x, sum_histograms_y = histogram_sum(histogram_x_all_files, histogram_y_all_files)
            
            first_reduced_factorial_moment_sum_list, second_reduced_factorial_moment_sum_list, third_reduced_factorial_moment_sum_list, fourth_reduced_factorial_moment_sum_list, n_list = reduced_factorial_moments(sum_histograms_y)
            first_factorial_moment_sum_list, second_factorial_moment_sum_list, third_factorial_moment_sum_list, fourth_factorial_moment_sum_list = factorial_moments(sum_histograms_y)
            single_feynman_mean_sum_list = first_factorial_moment_sum_list
            single_feynman_variance_sum_list = second_factorial_moment_sum_list
            single_variance_to_mean_sum_list = feynman_histogram_v2m(single_feynman_mean_sum_list,single_feynman_variance_sum_list)
            gate_width_sec = [entry*1e-9 for entry in gatewidth_list]
            Y1_sum_list, dY1_sum_list, Y2_sum_list, dY2_sum_list = excess_variance_reduced(gate_width_sec, sum_histograms_y, first_reduced_factorial_moment_sum_list, second_reduced_factorial_moment_sum_list, third_reduced_factorial_moment_sum_list, fourth_reduced_factorial_moment_sum_list)
            R1_sum_list = Y1_sum_list
            dR1_sum_list = dY1_sum_list
            Ym_sum_list, dYm_sum_list = excess_variance(gate_width_sec, sum_histograms_y, first_factorial_moment_sum_list, second_factorial_moment_sum_list, third_factorial_moment_sum_list, fourth_factorial_moment_sum_list)
            
            # this will plot Feynman histograms for the specified file and gatewidth if set to True by the user
            if plot_histograms == True or sum_Feynman_histograms == True:
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Histogram_Sum/Histograms/', 'Histogram_', current_file, add_current_file=True, make_dirs=True)
                for l in range(0,len(gatewidth_list)):
                    current_gatewidth = gatewidth_list[l]
                    print('Gate-width = ',current_gatewidth)
                    current_x = sum_histograms_x[l]
                    current_y = sum_histograms_y[l]
                    if histogram_normalize == True:
                        current_P = poissiondist.pmf(current_x, first_factorial_moment_sum_list[l])
                    else:
                        current_P = sum(current_y)*poissiondist.pmf(current_x, first_factorial_moment_sum_list[l])
                    if plot_histograms == True:
                        plotHistogram_single(current_gatewidth, current_x, current_y, current_P, show=False, limit_step=True, save=current_save_path+str(current_gatewidth), log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
                    else:
                        plotHistogram_single(current_gatewidth, current_x, current_y, current_P, show=False, limit_step=True, save=False, log=True, normalize=histogram_normalize, title=str(current_gatewidth)+' nsec')
                    histogram_x_sum_list.append(current_x)
                    histogram_y_sum_list.append(current_y)
                    histogram_P_sum_list.append(current_P)
            
            # this gets the total number of events
            total_events(gatewidth_list,histogram_x_sum_list,histogram_y_sum_list)
            
            # this runs the FeynmanYAnalysis.py script and extracts desired parameters
            R1_distribution_value_Hsum = Y1_distribution_value_Hsum = tuple(Y1_sum_list)
            R1_distribution_unc_Hsum = Y1_distribution_unc_Hsum = tuple(dY1_sum_list)
            Y1_distribution_Hsum = (Y1_distribution_value_Hsum,Y1_distribution_unc_Hsum)
            Y2_distribution_value_Hsum = tuple(Y2_sum_list)
            Y2_distribution_unc_Hsum = tuple(dY2_sum_list)
            Y2_distribution_Hsum = (Y2_distribution_value_Hsum,Y2_distribution_unc_Hsum)
        
            if (perform_Y2_single_fit == True or perform_Y2_double_fit == True) and len(gatewidth_list) < 6:
                sys.exit('Exit: at least 6 gate-widths are required to peform a single Y2 fit.')
            
            # Y2 single log fit
            if perform_Y2_single_fit == True:
                fit1log = fit1Log_xml(gatewidth_list, Y2_distribution_value_Hsum, Y2_distribution_unc_Hsum, guess=None)
                fit1log_temp = fit1log[0]
                fit1log_A = fit1log_temp[0]
                fit1log_B = fit1log_temp[1]
                fit1log_det_lifetime = 1/fit1log_B
                fit1log_temp = fit1log[1]
                fit1log_temp2 = fit1log_temp[0]
                fit1log_A_unc = np.sqrt(fit1log_temp2[0])
                fit1log_temp2 = fit1log_temp[1]
                fit1log_B_unc = np.sqrt(fit1log_temp2[1])
                fit1log_det_lifetime_unc = fit1log_det_lifetime*fit1log_B_unc/fit1log_B
                print('Histogram sum data, fit with 1 log. A = ',fit1log_A,' +/- ',fit1log_A_unc,'. B = ',fit1log_B,' +/- ',fit1log_B_unc,'. lifetime (1/B) = ',fit1log_det_lifetime,' +/- ',fit1log_det_lifetime_unc)
                fit_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                fit1_detailed_dis = []
                for fit_gatewidth in fit_gatewidths:
                    fit1_detailed_dis.append(fit1log_A * (1 - (1 - np.exp(-fit1log_B * fit_gatewidth)) / (fit1log_B* fit_gatewidth)))
                fit1_results = []
                fit1_results.append(fit_gatewidths)
                fit1_results.append(fit1_detailed_dis)
                fit1LogDistribution = []
                for gatewidth in gatewidth_list:
                    fit1LogDistribution.append(log_one(gatewidth, fit1log_A, fit1log_B))
                omega2_single_results = omega2_single(fit1log_B,gatewidth_list)
                R2_single_Y2_decay = R2_calc_rate(Y2_distribution_value_Hsum,omega2_single_results)
                R2_unc_single_Y2_decay = R2_unc_calc(gatewidth_list,R2_single_Y2_decay, omega2_single_results, Y2_distribution_unc_Hsum, fit1log_B, fit1log_B_unc)
                
            # Y2 double log fit    
            if perform_Y2_double_fit == True:
                perform_Y2_double_fit_continue = True
                fit2log = fit2Log_xml(gatewidth_list, Y2_distribution_value_Hsum, Y2_distribution_unc_Hsum, guess=None)
                fit2log_temp = fit2log[0]
                fit2log_A = fit2log_temp[0]
                fit2log_B = fit2log_temp[1]
                fit2log_C = fit2log_temp[2]
                fit2log_D = fit2log_temp[3]
                fit2log_det_lifetime1 = 1/fit2log_B
                fit2log_det_lifetime2 = 1/fit2log_D
                fit2log_amp = fit2log_A+fit2log_C
                fit2logA_percent = fit2log_A/(fit2log_A+fit2log_C)
                fit2logC_percent = fit2log_C/(fit2log_A+fit2log_C)
                
                if np.abs(fit2log_D/fit2log_B) >= 0.99 and np.abs(fit2log_D/fit2log_B) <= 1.01:
                    print('A double Y2 fit is not appropriate as it results in the same values for both parameters. A double fit will not be plotted/used.')
                    print('Histogram sum data, fit with 2 log. A = ',fit2log_A,'. B = ',fit2log_B,'. C = ',fit2log_C,'. D = ',fit2log_D,'. lifetime1 (1/B) = ',fit2log_det_lifetime1,'. lifetime2 (1/D) = ',fit2log_det_lifetime2)
                    omega2_double1_results = R2_double1_Y2_decay = R2_unc_double1_Y2_decay = omega2_double2_results = R2_double2_Y2_decay = R2_unc_double2_Y2_decay = ['N/A' for entry in gatewidth_list]
                    perform_Y2_double_fit_continue = False
                if perform_Y2_double_fit_continue == True:    
                    fit2log_temp = fit2log[1]
                    fit2log_temp2 = fit2log_temp[0]
                    fit2log_A_unc = np.sqrt(fit2log_temp2[0])
                    fit2log_temp2 = fit2log_temp[1]
                    fit2log_B_unc = np.sqrt(fit2log_temp2[1])
                    # Note there is NOT a sqrt here. I think that is correct. See: https://en.wikipedia.org/wiki/Propagation_of_uncertainty
                    fit2log_B_D = fit2log_temp2[3]
                    fit2log_temp2 = fit2log_temp[2]
                    fit2log_C_unc = np.sqrt(fit2log_temp2[2])
                    fit2log_temp2 = fit2log_temp[3]
                    fit2log_D_unc = np.sqrt(fit2log_temp2[3])
                    fit2log_det_lifetime1_unc = fit2log_det_lifetime1*fit2log_B_unc/fit2log_B
                    fit2log_det_lifetime2_unc = fit2log_det_lifetime2*fit2log_D_unc/fit2log_D
                    
                    # forces B to be > D. if it is not, then A and C are swapped (and B and D are swapped)
                    if fit2log_B < fit2log_D:
                        print('Switching first and second terms from fit to force B to be > D.')
                        temp = fit2log_A
                        temp2 = fit2log_C
                        fit2log_A = temp2
                        fit2log_C = temp
                        temp = fit2logA_percent
                        temp2 = fit2logC_percent
                        fit2logA_percent = temp2
                        fit2logC_percent = temp
                        temp = fit2log_A_unc
                        temp2 = fit2log_C_unc
                        fit2log_A_unc = temp2
                        fit2log_C_unc = temp
                        temp = fit2log_B
                        temp2 = fit2log_D
                        fit2log_B = temp2
                        fit2log_D = temp
                        temp = fit2log_B_unc
                        temp2 = fit2log_D_unc
                        fit2log_B_unc = temp2
                        fit2log_D_unc = temp
                        temp = fit2log_det_lifetime1
                        temp2 = fit2log_det_lifetime2
                        fit2log_det_lifetime1 = temp2
                        fit2log_det_lifetime2 = temp
                        temp = fit2log_det_lifetime1_unc
                        temp2 = fit2log_det_lifetime2_unc
                        fit2log_det_lifetime1_unc = temp2
                        fit2log_det_lifetime2_unc = temp
                    
                    print('Histogram sum data, fit with 2 log. A = ',fit2log_A,' +/- ',fit2log_A_unc,'. B = ',fit2log_B,' +/- ',fit2log_B_unc,'. C = ',fit2log_C,' +/- ',fit2log_C_unc,'. D = ',fit2log_D,' +/- ',fit2log_D_unc,'. lifetime1 (1/B) = ',fit2log_det_lifetime1,' +/- ',fit2log_det_lifetime1_unc,'. lifetime2 (1/D) = ',fit2log_det_lifetime2,' +/- ',fit2log_det_lifetime2_unc)
                    fit2_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                    fit2_detailed_dis = []
                    for fit2_gatewidth in fit2_gatewidths:
                        fit2_detailed_dis.append((fit2log_A * (1 - (1 - np.exp(-fit2log_B * fit2_gatewidth)) / (fit2log_B* fit2_gatewidth)))+(fit2log_C * (1 - (1 - np.exp(-fit2log_D * fit2_gatewidth)) / (fit2log_D* fit2_gatewidth))))
                    fit2_results = []
                    fit2_results.append(fit2_gatewidths)
                    fit2_results.append(fit2_detailed_dis)
                    fit2LogDistribution = []
                    for gatewidth in gatewidth_list:
                        fit2LogDistribution.append(log_two(gatewidth, fit2log_A, fit2log_B, fit2log_C, fit2log_D))
                    omega2_double1_results = omega2_single(fit2log_B,gatewidth_list)
                    R2_double1_Y2_decay = R2_calc_rate(Y2_distribution_value_Hsum,omega2_double1_results)
                    R2_unc_double1_Y2_decay = R2_unc_calc(gatewidth_list,R2_double1_Y2_decay, omega2_double1_results, Y2_distribution_unc_Hsum, fit2log_B, fit2log_B_unc)
                    omega2_double2_results = omega2_single(fit2log_D,gatewidth_list)
                    R2_double2_Y2_decay = R2_calc_rate(Y2_distribution_value_Hsum,omega2_double2_results)
                    R2_unc_double2_Y2_decay = R2_unc_calc(gatewidth_list,R2_double2_Y2_decay, omega2_double2_results, Y2_distribution_unc_Hsum, fit2log_D, fit2log_D_unc)
                    # This uses both terms, see unc equation in EUCLID subcritical paper
                    omega2_double_both_results = omega2_double(fit2logA_percent,fit2log_B,fit2logC_percent,fit2log_D,gatewidth_list)
                    R2_double_both_Y2_decay = R2_calc_rate(Y2_distribution_value_Hsum,omega2_double_both_results)
                    R2_unc_double_both_Y2_decay = R2_double_unc_calc(gatewidth_list,R2_double_both_Y2_decay, omega2_double_both_results, Y2_distribution_unc_Hsum, fit2logA_percent, fit2log_B, fit2log_B_unc, fit2logC_percent, fit2log_D, fit2log_D_unc, fit2log_B_D)
                    # in the future could these be combined similar to Michael Hua's work?    
            
            # User-specified lifetime
            if use_user_specified_lifetime == True:
                
                gate_width_sec = [entry*1e-9 for entry in gatewidth_list]
                gate_width_sec_b = [entry*1e-9/user_lifetime for entry in gatewidth_list]
        
                user_fit_results = curve_fit(log_one_user, gate_width_sec_b, Y2_sum_list, method="lm")
                temp = user_fit_results[0]
                user_A = temp[0]
                temp = user_fit_results[1]
                temp = temp[0]
                user_A_unc = np.sqrt(temp[0])
        
                print('Histogram sum data, fit with user-specified lifetime. A = ',user_A,' +/- ',user_A_unc,'. lifetime (1/B) = ',user_lifetime,' +/- ',user_lifetime_unc)
                fit_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                fit_gatewidths_b = [entry*1e-9/user_lifetime for entry in fit_gatewidths]
                
                fit_Y2 = []
                for gate in fit_gatewidths_b:
                    fit_Y2.append(log_one_user(gate, user_A))
                
                fit_lifetime_user_results = []
                fit_lifetime_user_results.append(fit_gatewidths)
                fit_lifetime_user_results.append(fit_Y2)
                omega2_lifetime_user_results = omega2_single(1/user_lifetime,gate_width_sec)
                R2_user_lifetime = R2_calc_rate(Y2_distribution_value_Hsum,omega2_lifetime_user_results)
                R2_unc_user_lifetime = R2_unc_calc(gatewidth_list,R2_user_lifetime, omega2_lifetime_user_results, Y2_distribution_unc_Hsum, 1/user_lifetime, user_lifetime_unc/user_lifetime**2)
            
            if calculation_type == 'Cf':
                calc_eff_kn_sum_list, calc_eff_unc_kn_sum_list = eff_from_Cf(gatewidth_list, Y1_sum_list, dY1_sum_list, nuS1_Cf252, Cf252_Fs, Cf252_dFs)  
            elif calculation_type == 'Multiplicity':
                # will revisit this in the future, currently cov between R1 and R2 is set to 0
                dR1R2_sum_list = [0 for i in range(0,len(gatewidth_list))]
                if perform_Y2_single_fit == True:
                    Ml_sum_list_Y2_single, a1_sum_list_Y2_single, a2_sum_list_Y2_single, a3_sum_list_Y2_single, a4_sum_list_Y2_single = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_single_Y2_decay, eff)
                    dMl_sum_list_Y2_single, dMldR1_sum_list_Y2_single, dMldR2_sum_list_Y2_single, dMldeff_sum_list_Y2_single = calc_dMl(gatewidth_list, a3_sum_list_Y2_single, a4_sum_list_Y2_single, R1_sum_list, dR1_sum_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, dR1R2_sum_list, eff, deff)
                    Fs_sum_list_Y2_single, a5_sum_list_Y2_single, a6_sum_list_Y2_single, a7_sum_list_Y2_single = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_single_Y2_decay, eff)
                    dFs_sum_list_Y2_single, dFsdR1_sum_list_Y2_single, dFsdR2_sum_list_Y2_single, dFsdeff_sum_list_Y2_single = calc_dFs(gatewidth_list, a5_sum_list_Y2_single, a6_sum_list_Y2_single, a7_sum_list_Y2_single, R1_sum_list, dR1_sum_list, R2_single_Y2_decay, R2_unc_single_Y2_decay, dR1R2_sum_list, eff, deff)
                    Mt_sum_list_Y2_single = calc_Mt(gatewidth_list, Ml_sum_list_Y2_single, nuI1, alpha)
                    dMt_sum_list_Y2_single = calc_dMt(gatewidth_list, nuI1, alpha, dMl_sum_list_Y2_single)
                    kp_sum_list_Y2_single = calc_kp(gatewidth_list, Mt_sum_list_Y2_single)
                    dkp_sum_list_Y2_single = calc_dkp(gatewidth_list, Mt_sum_list_Y2_single, dMt_sum_list_Y2_single)
                    keff_sum_list_Y2_single = calc_keff(gatewidth_list, kp_sum_list_Y2_single, beta_eff)
                    dkeff_sum_list_Y2_single = calc_dkeff(gatewidth_list, dkp_sum_list_Y2_single, beta_eff)
                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                    Ml_sum_list_Y2_double1, a1_sum_list_Y2_double1, a2_sum_list_Y2_double1, a3_sum_list_Y2_double1, a4_sum_list_Y2_double1 = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_double1_Y2_decay, eff)
                    dMl_sum_list_Y2_double1, dMldR1_sum_list_Y2_double1, dMldR2_sum_list_Y2_double1, dMldeff_sum_list_Y2_double1 = calc_dMl(gatewidth_list, a3_sum_list_Y2_double1, a4_sum_list_Y2_double1, R1_sum_list, dR1_sum_list, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, dR1R2_sum_list, eff, deff)
                    Fs_sum_list_Y2_double1, a5_sum_list_Y2_double1, a6_sum_list_Y2_double1, a7_sum_list_Y2_double1 = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_double1_Y2_decay, eff)
                    dFs_sum_list_Y2_double1, dFsdR1_sum_list_Y2_double1, dFsdR2_sum_list_Y2_double1, dFsdeff_sum_list_Y2_double1 = calc_dFs(gatewidth_list, a5_sum_list_Y2_double1, a6_sum_list_Y2_double1, a7_sum_list_Y2_double1, R1_sum_list, dR1_sum_list, R2_double1_Y2_decay, R2_unc_double1_Y2_decay, dR1R2_sum_list, eff, deff)
                    Mt_sum_list_Y2_double1 = calc_Mt(gatewidth_list, Ml_sum_list_Y2_double1, nuI1, alpha)
                    dMt_sum_list_Y2_double1 = calc_dMt(gatewidth_list, nuI1, alpha, dMl_sum_list_Y2_double1)
                    kp_sum_list_Y2_double1 = calc_kp(gatewidth_list, Mt_sum_list_Y2_double1)
                    dkp_sum_list_Y2_double1 = calc_dkp(gatewidth_list, Mt_sum_list_Y2_double1, dMt_sum_list_Y2_double1)
                    keff_sum_list_Y2_double1 = calc_keff(gatewidth_list, kp_sum_list_Y2_double1, beta_eff)
                    dkeff_sum_list_Y2_double1 = calc_dkeff(gatewidth_list, dkp_sum_list_Y2_double1, beta_eff)
                    Ml_sum_list_Y2_double2, a1_sum_list_Y2_double2, a2_sum_list_Y2_double2, a3_sum_list_Y2_double2, a4_sum_list_Y2_double2 = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_double2_Y2_decay, eff)
                    dMl_sum_list_Y2_double2, dMldR1_sum_list_Y2_double2, dMldR2_sum_list_Y2_double2, dMldeff_sum_list_Y2_double2 = calc_dMl(gatewidth_list, a3_sum_list_Y2_double2, a4_sum_list_Y2_double2, R1_sum_list, dR1_sum_list, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, dR1R2_sum_list, eff, deff)
                    Fs_sum_list_Y2_double2, a5_sum_list_Y2_double2, a6_sum_list_Y2_double2, a7_sum_list_Y2_double2 = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_double2_Y2_decay, eff)
                    dFs_sum_list_Y2_double2, dFsdR1_sum_list_Y2_double2, dFsdR2_sum_list_Y2_double2, dFsdeff_sum_list_Y2_double2 = calc_dFs(gatewidth_list, a5_sum_list_Y2_double2, a6_sum_list_Y2_double2, a7_sum_list_Y2_double2, R1_sum_list, dR1_sum_list, R2_double2_Y2_decay, R2_unc_double2_Y2_decay, dR1R2_sum_list, eff, deff)
                    Mt_sum_list_Y2_double2 = calc_Mt(gatewidth_list, Ml_sum_list_Y2_double2, nuI1, alpha)
                    dMt_sum_list_Y2_double2 = calc_dMt(gatewidth_list, nuI1, alpha, dMl_sum_list_Y2_double2)
                    kp_sum_list_Y2_double2 = calc_kp(gatewidth_list, Mt_sum_list_Y2_double2)
                    dkp_sum_list_Y2_double2 = calc_dkp(gatewidth_list, Mt_sum_list_Y2_double2, dMt_sum_list_Y2_double2)
                    keff_sum_list_Y2_double2 = calc_keff(gatewidth_list, kp_sum_list_Y2_double2, beta_eff)
                    dkeff_sum_list_Y2_double2 = calc_dkeff(gatewidth_list, dkp_sum_list_Y2_double2, beta_eff)
                    Ml_sum_list_Y2_double_both, a1_sum_list_Y2_double_both, a2_sum_list_Y2_double_both, a3_sum_list_Y2_double_both, a4_sum_list_Y2_double_both = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_double_both_Y2_decay, eff)
                    dMl_sum_list_Y2_double_both, dMldR1_sum_list_Y2_double_both, dMldR2_sum_list_Y2_double_both, dMldeff_sum_list_Y2_double_both = calc_dMl(gatewidth_list, a3_sum_list_Y2_double_both, a4_sum_list_Y2_double_both, R1_sum_list, dR1_sum_list, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, dR1R2_sum_list, eff, deff)
                    Fs_sum_list_Y2_double_both, a5_sum_list_Y2_double_both, a6_sum_list_Y2_double_both, a7_sum_list_Y2_double_both = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_double_both_Y2_decay, eff)
                    dFs_sum_list_Y2_double_both, dFsdR1_sum_list_Y2_double_both, dFsdR2_sum_list_Y2_double_both, dFsdeff_sum_list_Y2_double_both = calc_dFs(gatewidth_list, a5_sum_list_Y2_double_both, a6_sum_list_Y2_double_both, a7_sum_list_Y2_double_both, R1_sum_list, dR1_sum_list, R2_double_both_Y2_decay, R2_unc_double_both_Y2_decay, dR1R2_sum_list, eff, deff)
                    Mt_sum_list_Y2_double_both = calc_Mt(gatewidth_list, Ml_sum_list_Y2_double_both, nuI1, alpha)
                    dMt_sum_list_Y2_double_both = calc_dMt(gatewidth_list, nuI1, alpha, dMl_sum_list_Y2_double_both)
                    kp_sum_list_Y2_double_both = calc_kp(gatewidth_list, Mt_sum_list_Y2_double_both)
                    dkp_sum_list_Y2_double_both = calc_dkp(gatewidth_list, Mt_sum_list_Y2_double_both, dMt_sum_list_Y2_double_both)
                    keff_sum_list_Y2_double_both = calc_keff(gatewidth_list, kp_sum_list_Y2_double_both, beta_eff)
                    dkeff_sum_list_Y2_double_both = calc_dkeff(gatewidth_list, dkp_sum_list_Y2_double_both, beta_eff)
                if use_user_specified_lifetime == True:
                    Ml_sum_list_Y2_user_lifetime, a1_sum_list_Y2_user_lifetime, a2_sum_list_Y2_user_lifetime, a3_sum_list_Y2_user_lifetime, a4_sum_list_Y2_user_lifetime = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_user_lifetime_Y2_decay, eff)
                    dMl_sum_list_Y2_user_lifetime, dMldR1_sum_list_Y2_user_lifetime, dMldR2_sum_list_Y2_user_lifetime, dMldeff_sum_list_Y2_user_lifetime = calc_dMl(gatewidth_list, a3_sum_list_Y2_user_lifetime, a4_sum_list_Y2_user_lifetime, R1_sum_list, dR1_sum_list, R2_user_lifetime_Y2_decay, R2_unc_user_lifetime_Y2_decay, dR1R2_sum_list, eff, deff)
                    Fs_sum_list_Y2_user_lifetime, a5_sum_list_Y2_user_lifetime, a6_sum_list_Y2_user_lifetime, a7_sum_list_Y2_user_lifetime = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_sum_list, R2_user_lifetime_Y2_decay, eff)
                    dFs_sum_list_Y2_user_lifetime, dFsdR1_sum_list_Y2_user_lifetime, dFsdR2_sum_list_Y2_user_lifetime, dFsdeff_sum_list_Y2_user_lifetime = calc_dFs(gatewidth_list, a5_sum_list_Y2_user_lifetime, a6_sum_list_Y2_user_lifetime, a7_sum_list_Y2_user_lifetime, R1_sum_list, dR1_sum_list, R2_user_lifetime_Y2_decay, R2_unc_user_lifetime_Y2_decay, dR1R2_sum_list, eff, deff)
                    Mt_sum_list_Y2_user_lifetime = calc_Mt(gatewidth_list, Ml_sum_list_Y2_user_lifetime, nuI1, alpha)
                    dMt_sum_list_Y2_user_lifetime = calc_dMt(gatewidth_list, nuI1, alpha, dMl_sum_list_Y2_user_lifetime)
                    kp_sum_list_Y2_user_lifetime = calc_kp(gatewidth_list, Mt_sum_list_Y2_user_lifetime)
                    dkp_sum_list_Y2_user_lifetime = calc_dkp(gatewidth_list, Mt_sum_list_Y2_user_lifetime, dMt_sum_list_Y2_user_lifetime)
                    keff_sum_list_Y2_user_lifetime = calc_keff(gatewidth_list, kp_sum_list_Y2_user_lifetime, beta_eff)
                    dkeff_sum_list_Y2_user_lifetime = calc_dkeff(gatewidth_list, dkp_sum_list_Y2_user_lifetime, beta_eff)
            
            # plots from FeynmanYAnalysis.py
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Histogram_Sum/Rates/', 'FeynmanYan_Y2_', current_file, add_current_file=False, make_dirs=True)
            if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                plotY2_xml(gatewidth_list, Y2_distribution_value_Hsum, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, residuals=False, gaussianBins=50, show=False, save=current_save_path)
            
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Histogram_Sum/Rates/', 'FeynmanYan_Y2_residuals_', current_file, add_current_file=False, make_dirs=True)
            if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                plotResiduals_xml(gatewidth_list, Y2_distribution_value_Hsum, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, gaussianBins=100, show=False, save=current_save_path)
    
    
            # if desired to have historgrams with the same y-axis, this then finds the correct axis values and replots
            if histogram_match_axis == True:
                print('Creating histograms with matching axes.')
            
                final_xmin = 0
                final_xmax = 0
                for x in histogram_x_sum_list:
                    x_min = np.min(x)
                    x_max = np.max(x)
                    if x_min < final_xmin:
                        final_xmin = x
                    if x_max >= final_xmax:
                        final_xmax = 1.2*x_max
                
                y_no_zero = [[ele for ele in sub if ele !=0] for sub in histogram_y_sum_list]
                final_ymin = 1e5
                for current_y in y_no_zero:
                    final_ymin = np.min([final_ymin,np.min(current_y)])
                       
                final_ymax = 0
                for i in range(0,len(histogram_y_sum_list)):
                    temp1 = np.max(histogram_y_sum_list[i])
                    temp2 = np.max(histogram_P_sum_list[i])
                    y_max = np.max([temp1,temp2])
                    if y_max >= final_ymax:
                        final_ymax = 1.2*y_max
    
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Histogram_Sum/Histograms_axis_match/', 'Histogram_am_', current_file, add_current_file=True, make_dirs=True)
                
                for l in range(0,len(gatewidth_list)):
                    current_gatewidth = gatewidth_list[l]
                    print('Gate-width = ',current_gatewidth)
                    current_x = histogram_x_sum_list[l]
                    current_y = histogram_y_sum_list[l]
                    current_P = sum(current_y)*poissiondist.pmf(current_x, first_factorial_moment_sum_list[l])
                    plotHistogram_single(current_gatewidth, current_x, current_y, current_P, show=False, limit_step=True, save=current_save_path+str(current_gatewidth), log=True, xmin=final_xmin, xmax=final_xmax, ymin=final_ymin, ymax=final_ymax, title=str(current_gatewidth)+' nsec')
            
            
            print('Gate loop end')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Histogram_Sum/Rates/', '', current_file, add_current_file=False, make_dirs=True)    
            
            # plots of each parameter vs gatewidth for individual files
            plot_scatter_gatewidth(current_file_description, 'm1', 'micro-sec', gatewidth_list, first_reduced_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'm2', 'micro-sec', gatewidth_list, second_reduced_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'm3', 'micro-sec', gatewidth_list, third_reduced_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'm4', 'micro-sec', gatewidth_list, fourth_reduced_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C1', 'micro-sec', gatewidth_list, first_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C2', 'micro-sec', gatewidth_list, second_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C3', 'micro-sec', gatewidth_list, third_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'C4', 'micro-sec', gatewidth_list, fourth_factorial_moment_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'Y1', 'micro-sec', gatewidth_list, Y1_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dY1_sum_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dY1', 'micro-sec', gatewidth_list, dY1_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'R1', 'micro-sec', gatewidth_list, R1_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dR1_sum_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dR1', 'micro-sec', gatewidth_list, dR1_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_sum_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dY2', 'micro-sec', gatewidth_list, dY2_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'Ym', 'micro-sec', gatewidth_list, Ym_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dYm_sum_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth(current_file_description, 'dYm', 'micro-sec', gatewidth_list, dYm_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_single_fit == True:
                plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_sum_list, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, fit1=fit1_results, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_single_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_single_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_single_Y2_decay, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_single_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_sum_list, x_div=1000, show=False, save=current_save_path+'_fit2', mult_files=False, fit1=False, fit2=fit2_results, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_double1_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_double1_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double1_Y2_decay, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_double1_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_double2_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_double2_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double2_Y2_decay, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_double2_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_double_both_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_double_both_Y2_decay, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_double_both_Y2_decay, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_single_fit == True and perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_sum_list, x_div=1000, show=False, save=current_save_path+'_fit1+fit2', mult_files=False, fit1=fit1_results, fit2=fit2_results, yaxis_log=yaxis_log)
            if use_user_specified_lifetime == True:
                plot_scatter_gatewidth(current_file_description, 'Y2', 'micro-sec', gatewidth_list, Y2_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=dY2_sum_list, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, fit1=fit_lifetime_user_results, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'omega2', 'micro-sec', gatewidth_list, omega2_lifetime_user_results, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'R2', 'micro-sec', gatewidth_list, R2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=R2_unc_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dR2', 'micro-sec', gatewidth_list, R2_unc_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
            if calculation_type == 'Cf':
                plot_scatter_gatewidth(current_file_description, 'Efficiency', 'micro-sec', gatewidth_list, calc_eff_kn_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=calc_eff_unc_kn_sum_list, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth(current_file_description, 'dEfficiency', 'micro-sec', gatewidth_list, calc_eff_unc_kn_sum_list, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            elif calculation_type == 'Multiplicity':
                if perform_Y2_single_fit == True:
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dMl_sum_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dFs_sum_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dMt_sum_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dkp_sum_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_sum_list_Y2_single, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_sum_list_Y2_single, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dMl_sum_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dFs_sum_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dMt_sum_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dkp_sum_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_sum_list_Y2_double1, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_sum_list_Y2_double1, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dMl_sum_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dFs_sum_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dMt_sum_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dkp_sum_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_sum_list_Y2_double2, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_sum_list_Y2_double2, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dMl_sum_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dFs_sum_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dMt_sum_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dkp_sum_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_sum_list_Y2_double_both, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_sum_list_Y2_double_both, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                if use_user_specified_lifetime == True:
                    plot_scatter_gatewidth(current_file_description, 'Ml', 'micro-sec', gatewidth_list, Ml_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dMl_sum_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMl', 'micro-sec', gatewidth_list, dMl_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Fs', 'micro-sec', gatewidth_list, Fs_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dFs_sum_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dFs', 'micro-sec', gatewidth_list, dFs_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'Mt', 'micro-sec', gatewidth_list, Mt_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dMt_sum_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dMt', 'micro-sec', gatewidth_list, dMt_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'kp', 'micro-sec', gatewidth_list, kp_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dkp_sum_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkp', 'micro-sec', gatewidth_list, dkp_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'keff', 'micro-sec', gatewidth_list, keff_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=dkeff_sum_list_Y2_user_lifetime, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth(current_file_description, 'dkeff', 'micro-sec', gatewidth_list, dkeff_sum_list_Y2_user_lifetime, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
            
            print('Plotting histogram sum files end')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))        
            
            # set N/A to lists if fits were not performed
            if perform_Y2_single_fit != True:
                fit1log_A = fit1log_A_unc = fit1log_B = fit1log_B_unc = fit1log_det_lifetime = fit1log_det_lifetime_unc = 'N/A'   
                omega2_single_results = R2_single_Y2_decay = R2_unc_single_Y2_decay = ['N/A' for i in range(0,len(gatewidth_list))]
            if perform_Y2_double_fit != True or perform_Y2_double_fit_continue != True:
                fit2log_A = fit2log_A_unc = fit2log_B = fit2log_B_unc = fit2log_C = fit2log_C_unc = fit2log_D = fit2log_D_unc = fit2log_det_lifetime1 = fit2log_det_lifetime1_unc = fit2log_det_lifetime2 = fit2log_det_lifetime2_unc = 'N/A'
                omega2_double1_results = R2_double1_Y2_decay = R2_unc_double1_Y2_decay = omega2_double2_results = R2_double2_Y2_decay = R2_unc_double2_Y2_decay = R2_double_both_Y2_decay = R2_unc_double_both_Y2_decay = ['N/A' for i in range(0,len(gatewidth_list))]
            if use_user_specified_lifetime != True:
                omega2_lifetime_user_results = R2_user_lifetime = R2_unc_user_lifetime = ['N/A' for i in range(0,len(gatewidth_list))]
            
            # output a single csv file for each file and gives results vs gatewidth if set to True by the user
            if output_csv == True:
                    
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Histogram_Sum/Rates/', '', current_file, add_current_file=False, make_dirs=False)    
                
                csv_name = current_save_path+'Histogram_Sum_Rates.csv'
                    
                
                with open(csv_name, mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    header_row = ['Gate-width','m1','m2','m3','m4','C1','C2','C3','C4','Y1','dY1','Y2','dY2','R1','dR1','fit1log_A','fit1log_A_unc','fit1log_B','fit1log_B_unc','fit1log_det_lifetime','fit1log_det_lifetime_unc','omega2_single_results','R2_single_Y2_decay','R2_unc_single_Y2_decay','fit2log_A','fit2log_A_unc','fit2log_B','fit2log_B_unc','fit2log_C','fit2log_C_unc','fit2log_D','fit2log_D_unc','fit2log_det_lifetime1','fit2log_det_lifetime1_unc','fit2log_det_lifetime2','fit2log_det_lifetime2_unc','omega2_double1_results','R2_double1_Y2_decay','R2_unc_double1_Y2_decay','omega2_double2_results','R2_double2_Y2_decay','R2_unc_double2_Y2_decay','R2_double_both_Y2_decay','R2_unc_double_both_Y2_decay','omega2_lifetime_user_results','R2_user_lifetime','R2_unc_user_lifetime','Ym','dYm']
                    if calculation_type == 'Cf':
                        header_row.append('eff from Cf')
                        header_row.append('deff from Cf')
                    elif calculation_type == 'Multiplicity':
                        if perform_Y2_single_fit == True:
                            header_row.append('Ml (Y2 single)')
                            header_row.append('dMl (Y2 single)')
                            header_row.append('Fs (Y2 single)')
                            header_row.append('dFs (Y2 single)')
                            header_row.append('Mt (Y2 single)')
                            header_row.append('dMt (Y2 single)')
                            header_row.append('kp (Y2 single)')
                            header_row.append('dkp (Y2 single)')
                            header_row.append('keff (Y2 single)')
                            header_row.append('dkeff (Y2 single)')
                        if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                            header_row.append('Ml (Y2_double1)')
                            header_row.append('dMl (Y2 double1)')
                            header_row.append('Fs (Y2 double1)')
                            header_row.append('dFs (Y2 double1)')
                            header_row.append('Mt (Y2 double1)')
                            header_row.append('dMt (Y2 double1)')
                            header_row.append('kp (Y2 double1)')
                            header_row.append('dkp (Y2 double1)')
                            header_row.append('keff (Y2 double1)')
                            header_row.append('dkeff (Y2 double1)')
                            header_row.append('Ml (Y2_double2)')
                            header_row.append('dMl (Y2 double2)')
                            header_row.append('Fs (Y2 double2)')
                            header_row.append('dFs (Y2 double2)')
                            header_row.append('Mt (Y2 double2)')
                            header_row.append('dMt (Y2 double2)')
                            header_row.append('kp (Y2 double2)')
                            header_row.append('dkp (Y2 double2)')
                            header_row.append('keff (Y2 double2)')
                            header_row.append('dkeff (Y2 double2)')
                            header_row.append('Ml (Y2_double_both)')
                            header_row.append('dMl (Y2 double_both)')
                            header_row.append('Fs (Y2 double_both)')
                            header_row.append('dFs (Y2 double_both)')
                            header_row.append('Mt (Y2 double_both)')
                            header_row.append('dMt (Y2 double_both)')
                            header_row.append('kp (Y2 double_both)')
                            header_row.append('dkp (Y2 double_both)')
                            header_row.append('keff (Y2 double_both)')
                            header_row.append('dkeff (Y2 double_both)')
                        if use_user_specified_lifetime == True:
                            header_row.append('Ml (Y2_user_lifetime)')
                            header_row.append('dMl (Y2 user_lifetime)')
                            header_row.append('Fs (Y2 user_lifetime)')
                            header_row.append('dFs (Y2 user_lifetime)')
                            header_row.append('Mt (Y2 user_lifetime)')
                            header_row.append('dMt (Y2 user_lifetime)')
                            header_row.append('kp (Y2 user_lifetime)')
                            header_row.append('dkp (Y2 user_lifetime)')
                            header_row.append('keff (Y2 user_lifetime)')
                            header_row.append('dkeff (Y2 user_lifetime)')
                    writer.writerow(header_row)
                    for value in range(len(gatewidth_list)):
                        data_row = [gatewidth_list[value], first_reduced_factorial_moment_sum_list[value], second_reduced_factorial_moment_sum_list[value], third_reduced_factorial_moment_sum_list[value], fourth_reduced_factorial_moment_sum_list[value], first_factorial_moment_sum_list[value], second_factorial_moment_sum_list[value], third_factorial_moment_sum_list[value], fourth_factorial_moment_sum_list[value], Y1_sum_list[value], dY1_sum_list[value], Y2_sum_list[value], dY2_sum_list[value], R1_sum_list[value], dR1_sum_list[value], fit1log_A,fit1log_A_unc,fit1log_B,fit1log_B_unc,fit1log_det_lifetime,fit1log_det_lifetime_unc,omega2_single_results[value],R2_single_Y2_decay[value],R2_unc_single_Y2_decay[value],fit2log_A,fit2log_A_unc,fit2log_B,fit2log_B_unc,fit2log_C,fit2log_C_unc,fit2log_D,fit2log_D_unc,fit2log_det_lifetime1,fit2log_det_lifetime1_unc,fit2log_det_lifetime2,fit2log_det_lifetime2_unc,omega2_double1_results[value],R2_double1_Y2_decay[value],R2_unc_double1_Y2_decay[value],omega2_double2_results[value],R2_double2_Y2_decay[value],R2_unc_double2_Y2_decay[value],R2_double_both_Y2_decay[value],R2_unc_double_both_Y2_decay[value],omega2_lifetime_user_results[value],R2_user_lifetime[value],R2_unc_user_lifetime[value], Ym_sum_list[value], dYm_sum_list[value]]
                        if calculation_type == 'Cf':
                            data_row.append(calc_eff_kn_sum_list[value])
                            data_row.append(calc_eff_unc_kn_sum_list[value])
                        elif calculation_type == 'Multiplicity':
                            if perform_Y2_single_fit == True:
                                data_row.append(Ml_sum_list_Y2_single[value])
                                data_row.append(dMl_sum_list_Y2_single[value])
                                data_row.append(Fs_sum_list_Y2_single[value])
                                data_row.append(dFs_sum_list_Y2_single[value])
                                data_row.append(Mt_sum_list_Y2_single[value])
                                data_row.append(dMt_sum_list_Y2_single[value])
                                data_row.append(kp_sum_list_Y2_single[value])
                                data_row.append(dkp_sum_list_Y2_single[value])
                                data_row.append(keff_sum_list_Y2_single[value])
                                data_row.append(dkeff_sum_list_Y2_single[value])
                            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                data_row.append(Ml_sum_list_Y2_double1[value])
                                data_row.append(dMl_sum_list_Y2_double1[value])
                                data_row.append(Fs_sum_list_Y2_double1[value])
                                data_row.append(dFs_sum_list_Y2_double1[value])
                                data_row.append(Mt_sum_list_Y2_double1[value])
                                data_row.append(dMt_sum_list_Y2_double1[value])
                                data_row.append(kp_sum_list_Y2_double1[value])
                                data_row.append(dkp_sum_list_Y2_double1[value])
                                data_row.append(keff_sum_list_Y2_double1[value])
                                data_row.append(dkeff_sum_list_Y2_double1[value])
                                data_row.append(Ml_sum_list_Y2_double2[value])
                                data_row.append(dMl_sum_list_Y2_double2[value])
                                data_row.append(Fs_sum_list_Y2_double2[value])
                                data_row.append(dFs_sum_list_Y2_double2[value])
                                data_row.append(Mt_sum_list_Y2_double2[value])
                                data_row.append(dMt_sum_list_Y2_double2[value])
                                data_row.append(kp_sum_list_Y2_double2[value])
                                data_row.append(dkp_sum_list_Y2_double2[value])
                                data_row.append(keff_sum_list_Y2_double2[value])
                                data_row.append(dkeff_sum_list_Y2_double2[value])
                                data_row.append(Ml_sum_list_Y2_double_both[value])
                                data_row.append(dMl_sum_list_Y2_double_both[value])
                                data_row.append(Fs_sum_list_Y2_double_both[value])
                                data_row.append(dFs_sum_list_Y2_double_both[value])
                                data_row.append(Mt_sum_list_Y2_double_both[value])
                                data_row.append(dMt_sum_list_Y2_double_both[value])
                                data_row.append(kp_sum_list_Y2_double_both[value])
                                data_row.append(dkp_sum_list_Y2_double_both[value])
                                data_row.append(keff_sum_list_Y2_double_both[value])
                                data_row.append(dkeff_sum_list_Y2_double_both[value])
                            if use_user_specified_lifetime == True:
                                data_row.append(Ml_sum_list_Y2_user_lifetime[value])
                                data_row.append(dMl_sum_list_Y2_user_lifetime[value])
                                data_row.append(Fs_sum_list_Y2_user_lifetime[value])
                                data_row.append(dFs_sum_list_Y2_user_lifetime[value])
                                data_row.append(Mt_sum_list_Y2_user_lifetime[value])
                                data_row.append(dMt_sum_list_Y2_user_lifetime[value])
                                data_row.append(kp_sum_list_Y2_user_lifetime[value])
                                data_row.append(dkp_sum_list_Y2_user_lifetime[value])
                                data_row.append(keff_sum_list_Y2_user_lifetime[value])
                                data_row.append(dkeff_sum_list_Y2_user_lifetime[value]) 
                        writer.writerow(data_row)
                        
                if compare_combine_Y2_rate_results_and_Feynman_sum == True and combine_Y2_rate_results == True:
                    sum_histogram_filepath = current_save_path
                    print('Note: compare_combine_Y2_rate_results_and_Feynman_sum, output_csv, combine_Y2_rate_results, and sum_Feynman_histograms are all set to True. The user sum_histogram_filepath is being ignore. sum_histogram_filepath is set to ',sum_histogram_filepath)                
            
            print('End sum Feynman histograms')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
        
        # this combines results starting at the rates
        # the value is a weighted average 
        # the unc is sum of squares
        if combine_Y2_rate_results == True:
            
            print('Combining Y2 rate results')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combined/', '', current_file, add_current_file=False, make_dirs=True)   
            
            Y1_combined, Y1_combined_unc, Y1_combined_sd, Y1_individual_unc_avg = combine_rates(Y1_all_files, dY1_all_files)
            R1_combined, R1_combined_unc, R1_combined_sd, R1_individual_unc_avg = combine_rates(R1_all_files, dR1_all_files)
            Y2_combined, Y2_combined_unc, Y2_combined_sd, Y2_individual_unc_avg = combine_rates(Y2_all_files, dY2_all_files)
            Ym_combined, Ym_combined_unc, Ym_combined_sd, Ym_individual_unc_avg = combine_rates(Ym_all_files, dYm_all_files)        
            
            if combine_Y2_rate_results_old_method == True:
                if perform_Y2_single_fit == True:
                    R2_single_Y2_decay_combined, R2_single_Y2_decay_combined_unc, R2_single_Y2_decay_combined_sd, R2_single_Y2_decay_individual_unc_avg = combine_rates(R2_single_Y2_decay_all_files, R2_unc_single_Y2_decay_all_files)
                if perform_Y2_double_fit == True:
                    R2_double1_Y2_decay_combined, R2_double1_Y2_decay_combined_unc, R2_double1_Y2_decay_combined_sd, R2_double1_Y2_decay_individual_unc_avg = combine_rates(R2_double1_Y2_decay_all_files, R2_unc_double1_Y2_decay_all_files)
                    R2_double2_Y2_decay_combined, R2_double2_Y2_decay_combined_unc, R2_double2_Y2_decay_combined_sd, R2_double2_Y2_decay_individual_unc_avg = combine_rates(R2_double2_Y2_decay_all_files, R2_unc_double2_Y2_decay_all_files)
                    R2_double_both_Y2_decay_combined, R2_double_both_Y2_decay_combined_unc, R2_double_both_Y2_decay_combined_sd, R2_double_both_Y2_decay_individual_unc_avg = combine_rates(R2_double_both_Y2_decay_all_files, R2_unc_double_both_Y2_decay_all_files)
                if use_user_specified_lifetime == True:
                    R2_user_lifetime_combined, R2_user_lifetime_combined_unc, R2_user_lifetime_combined_sd, R2_user_lifetime_individual_unc_avg = combine_rates(R2_user_lifetime_all_files, R2_unc_user_lifetime_all_files)
                if calculation_type == 'Cf':
                    calc_eff_kn_combined, calc_eff_kn_combined_unc, calc_eff_kn_combined_sd, calc_eff_kn_individual_unc_avg = combine_rates(calc_eff_kn_all_files, calc_eff_unc_kn_all_files)
                elif calculation_type == 'Multiplicity':
                    if perform_Y2_single_fit == True:
                        Ml_single_combined, Ml_single_combined_unc, Ml_single_combined_sd, Ml_single_individual_unc_avg, = combine_rates(Ml_single_all_files, dMl_single_all_files)
                        Mt_single_combined, Mt_single_combined_unc, Mt_single_combined_sd, Mt_single_individual_unc_avg, = combine_rates(Mt_single_all_files, dMt_single_all_files)
                        Fs_single_combined, Fs_single_combined_unc, Fs_single_combined_sd, Fs_single_individual_unc_avg, = combine_rates(Fs_single_all_files, dFs_single_all_files)
                        kp_single_combined, kp_single_combined_unc, kp_single_combined_sd, kp_single_individual_unc_avg, = combine_rates(kp_single_all_files, dkp_single_all_files)
                        keff_single_combined, keff_single_combined_unc, keff_single_combined_sd, keff_single_individual_unc_avg, = combine_rates(keff_single_all_files, dkeff_single_all_files)
                    if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                        Ml_double1_combined, Ml_double1_combined_unc, Ml_double1_combined_sd, Ml_double1_individual_unc_avg, = combine_rates(Ml_double1_all_files, dMl_double1_all_files)
                        Mt_double1_combined, Mt_double1_combined_unc, Mt_double1_combined_sd, Mt_double1_individual_unc_avg, = combine_rates(Mt_double1_all_files, dMt_double1_all_files)
                        Fs_double1_combined, Fs_double1_combined_unc, Fs_double1_combined_sd, Fs_double1_individual_unc_avg, = combine_rates(Fs_double1_all_files, dFs_double1_all_files)
                        kp_double1_combined, kp_double1_combined_unc, kp_double1_combined_sd, kp_double1_individual_unc_avg, = combine_rates(kp_double1_all_files, dkp_double1_all_files)
                        keff_double1_combined, keff_double1_combined_unc, keff_double1_combined_sd, keff_double1_individual_unc_avg, = combine_rates(keff_double1_all_files, dkeff_double1_all_files)
                        Ml_double2_combined, Ml_double2_combined_unc, Ml_double2_combined_sd, Ml_double2_individual_unc_avg, = combine_rates(Ml_double2_all_files, dMl_double2_all_files)
                        Mt_double2_combined, Mt_double2_combined_unc, Mt_double2_combined_sd, Mt_double2_individual_unc_avg, = combine_rates(Mt_double2_all_files, dMt_double2_all_files)
                        Fs_double2_combined, Fs_double2_combined_unc, Fs_double2_combined_sd, Fs_double2_individual_unc_avg, = combine_rates(Fs_double2_all_files, dFs_double2_all_files)
                        kp_double2_combined, kp_double2_combined_unc, kp_double2_combined_sd, kp_double2_individual_unc_avg, = combine_rates(kp_double2_all_files, dkp_double2_all_files)
                        keff_double2_combined, keff_double2_combined_unc, keff_double2_combined_sd, keff_double2_individual_unc_avg, = combine_rates(keff_double2_all_files, dkeff_double2_all_files)
                        Ml_double_both_combined, Ml_double_both_combined_unc, Ml_double_both_combined_sd, Ml_double_both_individual_unc_avg, = combine_rates(Ml_double_both_all_files, dMl_double_both_all_files)
                        Mt_double_both_combined, Mt_double_both_combined_unc, Mt_double_both_combined_sd, Mt_double_both_individual_unc_avg, = combine_rates(Mt_double_both_all_files, dMt_double_both_all_files)
                        Fs_double_both_combined, Fs_double_both_combined_unc, Fs_double_both_combined_sd, Fs_double_both_individual_unc_avg, = combine_rates(Fs_double_both_all_files, dFs_double_both_all_files)
                        kp_double_both_combined, kp_double_both_combined_unc, kp_double_both_combined_sd, kp_double_both_individual_unc_avg, = combine_rates(kp_double_both_all_files, dkp_double_both_all_files)
                        keff_double_both_combined, keff_double_both_combined_unc, keff_double_both_combined_sd, keff_double_both_individual_unc_avg, = combine_rates(keff_double_both_all_files, dkeff_double_both_all_files)
                    if use_user_specified_lifetime == True:
                        Ml_user_lifetime_combined, Ml_user_lifetime_combined_unc, Ml_user_lifetime_combined_sd, Ml_user_lifetime_individual_unc_avg, = combine_rates(Ml_user_lifetime_all_files, dMl_user_lifetime_all_files)
                        Mt_user_lifetime_combined, Mt_user_lifetime_combined_unc, Mt_user_lifetime_combined_sd, Mt_user_lifetime_individual_unc_avg, = combine_rates(Mt_user_lifetime_all_files, dMt_user_lifetime_all_files)
                        Fs_user_lifetime_combined, Fs_user_lifetime_combined_unc, Fs_user_lifetime_combined_sd, Fs_user_lifetime_individual_unc_avg, = combine_rates(Fs_user_lifetime_all_files, dFs_user_lifetime_all_files)
                        kp_user_lifetime_combined, kp_user_lifetime_combined_unc, kp_user_lifetime_combined_sd, kp_user_lifetime_individual_unc_avg, = combine_rates(kp_user_lifetime_all_files, dkp_user_lifetime_all_files)
                        keff_user_lifetime_combined, keff_user_lifetime_combined_unc, keff_user_lifetime_combined_sd, keff_user_lifetime_individual_unc_avg, = combine_rates(keff_user_lifetime_all_files, dkeff_user_lifetime_all_files)
            else:
                # Y2 single log fit
                if perform_Y2_single_fit == True:
                    fit1log = fit1Log_xml(gatewidth_list, Y2_combined, Y2_combined_unc, guess=None)
                    fit1log_temp = fit1log[0]
                    fit1log_A = fit1log_temp[0]
                    fit1log_B = fit1log_temp[1]
                    fit1log_det_lifetime = 1/fit1log_B
                    fit1log_temp = fit1log[1]
                    fit1log_temp2 = fit1log_temp[0]
                    fit1log_A_unc = np.sqrt(fit1log_temp2[0])
                    fit1log_temp2 = fit1log_temp[1]
                    fit1log_B_unc = np.sqrt(fit1log_temp2[1])
                    fit1log_det_lifetime_unc = fit1log_det_lifetime*fit1log_B_unc/fit1log_B
                    print('Combined data, fit with 1 log. A = ',fit1log_A,' +/- ',fit1log_A_unc,'. B = ',fit1log_B,' +/- ',fit1log_B_unc,'. lifetime (1/B) = ',fit1log_det_lifetime,' +/- ',fit1log_det_lifetime_unc)
                    fit_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                    fit1_detailed_dis = []
                    for fit_gatewidth in fit_gatewidths:
                        fit1_detailed_dis.append(fit1log_A * (1 - (1 - np.exp(-fit1log_B * fit_gatewidth)) / (fit1log_B* fit_gatewidth)))
                    fit1_results = []
                    fit1_results.append(fit_gatewidths)
                    fit1_results.append(fit1_detailed_dis)
                    fit1LogDistribution = []
                    for gatewidth in gatewidth_list:
                        fit1LogDistribution.append(log_one(gatewidth, fit1log_A, fit1log_B))
                    omega2_single_results = omega2_single(fit1log_B,gatewidth_list)
                    R2_single_Y2_decay_combined = R2_calc_rate(Y2_combined,omega2_single_results)
                    R2_single_Y2_decay_combined_unc = R2_unc_calc(gatewidth_list,R2_single_Y2_decay_combined, omega2_single_results, Y2_combined_unc, fit1log_B, fit1log_B_unc)
                    
                # Y2 double log fit    
                if perform_Y2_double_fit == True:
                    perform_Y2_double_fit_continue = True
                    fit2log = fit2Log_xml(gatewidth_list, Y2_combined, Y2_combined_unc, guess=None)
                    fit2log_temp = fit2log[0]
                    fit2log_A = fit2log_temp[0]
                    fit2log_B = fit2log_temp[1]
                    fit2log_C = fit2log_temp[2]
                    fit2log_D = fit2log_temp[3]
                    fit2log_det_lifetime1 = 1/fit2log_B
                    fit2log_det_lifetime2 = 1/fit2log_D
                    fit2log_amp = fit2log_A+fit2log_C
                    fit2logA_percent = fit2log_A/(fit2log_A+fit2log_C)
                    fit2logC_percent = fit2log_C/(fit2log_A+fit2log_C)
                    
                    if np.abs(fit2log_D/fit2log_B) >= 0.99 and np.abs(fit2log_D/fit2log_B) <= 1.01:
                        print('A double Y2 fit is not appropriate as it results in the same values for both parameters. A double fit will not be plotted/used.')
                        print('Combined data, fit with 2 log. A = ',fit2log_A,'. B = ',fit2log_B,'. C = ',fit2log_C,'. D = ',fit2log_D,'. lifetime1 (1/B) = ',fit2log_det_lifetime1,'. lifetime2 (1/D) = ',fit2log_det_lifetime2)
                        omega2_double1_results = R2_double1_Y2_decay_combined = R2_single_Y2_decay_combined_unc = omega2_double2_results = R2_double2_Y2_decay_combined = R2_double2_Y2_decay_combined_unc = ['N/A' for entry in gatewidth_list]
                        perform_Y2_double_fit_continue = False
                    if perform_Y2_double_fit_continue == True:    
                        fit2log_temp = fit2log[1]
                        fit2log_temp2 = fit2log_temp[0]
                        fit2log_A_unc = np.sqrt(fit2log_temp2[0])
                        fit2log_temp2 = fit2log_temp[1]
                        fit2log_B_unc = np.sqrt(fit2log_temp2[1])
                        # Note there is NOT a sqrt here. I think that is correct. See: https://en.wikipedia.org/wiki/Propagation_of_uncertainty
                        fit2log_B_D = fit2log_temp2[3]
                        fit2log_temp2 = fit2log_temp[2]
                        fit2log_C_unc = np.sqrt(fit2log_temp2[2])
                        fit2log_temp2 = fit2log_temp[3]
                        fit2log_D_unc = np.sqrt(fit2log_temp2[3])
                        fit2log_det_lifetime1_unc = fit2log_det_lifetime1*fit2log_B_unc/fit2log_B
                        fit2log_det_lifetime2_unc = fit2log_det_lifetime2*fit2log_D_unc/fit2log_D
                        
                        # forces B to be > D. if it is not, then A and C are swapped (and B and D are swapped)
                        if fit2log_B < fit2log_D:
                            print('Switching first and second terms from fit to force B to be > D.')
                            temp = fit2log_A
                            temp2 = fit2log_C
                            fit2log_A = temp2
                            fit2log_C = temp
                            temp = fit2logA_percent
                            temp2 = fit2logC_percent
                            fit2logA_percent = temp2
                            fit2logC_percent = temp
                            temp = fit2log_A_unc
                            temp2 = fit2log_C_unc
                            fit2log_A_unc = temp2
                            fit2log_C_unc = temp
                            temp = fit2log_B
                            temp2 = fit2log_D
                            fit2log_B = temp2
                            fit2log_D = temp
                            temp = fit2log_B_unc
                            temp2 = fit2log_D_unc
                            fit2log_B_unc = temp2
                            fit2log_D_unc = temp
                            temp = fit2log_det_lifetime1
                            temp2 = fit2log_det_lifetime2
                            fit2log_det_lifetime1 = temp2
                            fit2log_det_lifetime2 = temp
                            temp = fit2log_det_lifetime1_unc
                            temp2 = fit2log_det_lifetime2_unc
                            fit2log_det_lifetime1_unc = temp2
                            fit2log_det_lifetime2_unc = temp
                        
                        print('Combined data, fit with 2 log. A = ',fit2log_A,' +/- ',fit2log_A_unc,'. B = ',fit2log_B,' +/- ',fit2log_B_unc,'. C = ',fit2log_C,' +/- ',fit2log_C_unc,'. D = ',fit2log_D,' +/- ',fit2log_D_unc,'. lifetime1 (1/B) = ',fit2log_det_lifetime1,' +/- ',fit2log_det_lifetime1_unc,'. lifetime2 (1/D) = ',fit2log_det_lifetime2,' +/- ',fit2log_det_lifetime2_unc)
                        fit2_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                        fit2_detailed_dis = []
                        for fit2_gatewidth in fit2_gatewidths:
                            fit2_detailed_dis.append((fit2log_A * (1 - (1 - np.exp(-fit2log_B * fit2_gatewidth)) / (fit2log_B* fit2_gatewidth)))+(fit2log_C * (1 - (1 - np.exp(-fit2log_D * fit2_gatewidth)) / (fit2log_D* fit2_gatewidth))))
                        fit2_results = []
                        fit2_results.append(fit2_gatewidths)
                        fit2_results.append(fit2_detailed_dis)
                        fit2LogDistribution = []
                        for gatewidth in gatewidth_list:
                            fit2LogDistribution.append(log_two(gatewidth, fit2log_A, fit2log_B, fit2log_C, fit2log_D))
                        omega2_double1_results = omega2_single(fit2log_B,gatewidth_list)
                        R2_double1_Y2_decay_combined = R2_calc_rate(Y2_combined,omega2_double1_results)
                        R2_double1_Y2_decay_combined_unc = R2_unc_calc(gatewidth_list,R2_double1_Y2_decay_combined, omega2_double1_results, Y2_combined_unc, fit2log_B, fit2log_B_unc)
                        omega2_double2_results = omega2_single(fit2log_D,gatewidth_list)
                        R2_double2_Y2_decay_combined = R2_calc_rate(Y2_combined,omega2_double2_results)
                        R2_double2_Y2_decay_combined_unc = R2_unc_calc(gatewidth_list,R2_double2_Y2_decay_combined, omega2_double2_results, Y2_combined_unc, fit2log_D, fit2log_D_unc)
                        # This uses both terms, see unc equation in EUCLID subcritical paper
                        omega2_double_both_results = omega2_double(fit2logA_percent,fit2log_B,fit2logC_percent,fit2log_D,gatewidth_list)
                        R2_double_both_Y2_decay_combined = R2_calc_rate(Y2_combined,omega2_double_both_results)
                        R2_double_both_Y2_decay_combined_unc = R2_double_unc_calc(gatewidth_list,R2_double_both_Y2_decay_combined, omega2_double_both_results, Y2_combined_unc, fit2logA_percent, fit2log_B, fit2log_B_unc, fit2logC_percent, fit2log_D, fit2log_D_unc, fit2log_B_D)
                        # in the future could these be combined similar to Michael Hua's work?    
                
                # User-specified lifetime
                if use_user_specified_lifetime == True:
                    
                    gate_width_sec = [entry*1e-9 for entry in gatewidth_list]
                    gate_width_sec_b = [entry*1e-9/user_lifetime for entry in gatewidth_list]
            
                    user_fit_results = curve_fit(log_one_user, gate_width_sec_b, Y2_combined, method="lm")
                    temp = user_fit_results[0]
                    user_A = temp[0]
                    temp = user_fit_results[1]
                    temp = temp[0]
                    user_A_unc = np.sqrt(temp[0])
            
                    print('Combined data, fit with user-specified lifetime. A = ',user_A,' +/- ',user_A_unc,'. lifetime (1/B) = ',user_lifetime,' +/- ',user_lifetime_unc)
                    fit_gatewidths = np.logspace(np.log10(np.min(gatewidth_list)),np.log10(np.max(gatewidth_list)),num=1000)
                    fit_gatewidths_b = [entry*1e-9/user_lifetime for entry in fit_gatewidths]
                    
                    fit_Y2 = []
                    for gate in fit_gatewidths_b:
                        fit_Y2.append(log_one_user(gate, user_A))
                    
                    fit_lifetime_user_results = []
                    fit_lifetime_user_results.append(fit_gatewidths)
                    fit_lifetime_user_results.append(fit_Y2)
                    omega2_lifetime_user_results = omega2_single(1/user_lifetime,gate_width_sec)
                    R2_user_lifetime_combined = R2_calc_rate(Y2_combined,omega2_lifetime_user_results)
                    R2_user_lifetime_combined_unc = R2_unc_calc(gatewidth_list,R2_user_lifetime_combined, omega2_lifetime_user_results, Y2_combined_unc, 1/user_lifetime, user_lifetime_unc/user_lifetime**2)
                
                if calculation_type == 'Cf':
                    calc_eff_kn_combined, calc_eff_kn_combined_unc = eff_from_Cf(gatewidth_list, Y1_combined, Y1_combined_unc, nuS1_Cf252, Cf252_Fs, Cf252_dFs)  
                elif calculation_type == 'Multiplicity':
                    # will revisit this in the future, currently cov between R1 and R2 is set to 0
                    dR1R2_combined = [0 for i in range(0,len(gatewidth_list))]
                    if perform_Y2_single_fit == True:
                        Ml_single_combined, a1_single_combined, a2_single_combined, a3_single_combined, a4_single_combined = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_single_Y2_decay_combined, eff)
                        Ml_single_combined_unc, dMldR1_single_combined, dMldR2_single_combined, dMldeff_single_combined = calc_dMl(gatewidth_list, a3_single_combined, a4_single_combined, R1_combined, R1_combined_unc, R2_single_Y2_decay_combined, R2_single_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Fs_single_combined, a5_single_combined, a6_single_combined, a7_single_combined = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_single_Y2_decay_combined, eff)
                        Fs_single_combined_unc, dFsdR1_single_combined, dFsdR2_single_combined, dFsdeff_single_combined = calc_dFs(gatewidth_list, a5_single_combined, a6_single_combined, a7_single_combined, R1_combined, R1_combined_unc, R2_single_Y2_decay_combined, R2_single_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Mt_single_combined = calc_Mt(gatewidth_list, Ml_single_combined, nuI1, alpha)
                        Mt_single_combined_unc = calc_dMt(gatewidth_list, nuI1, alpha, Ml_single_combined_unc)
                        kp_single_combined = calc_kp(gatewidth_list, Mt_single_combined)
                        kp_single_combined_unc = calc_dkp(gatewidth_list, Mt_single_combined, Mt_single_combined_unc)
                        keff_single_combined = calc_keff(gatewidth_list, kp_single_combined, beta_eff)
                        keff_single_combined_unc = calc_dkeff(gatewidth_list, kp_single_combined_unc, beta_eff)
                    if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                        Ml_double1_combined, a1_double1_combined, a2_double1_combined, a3_double1_combined, a4_double1_combined = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_double1_Y2_decay_combined, eff)
                        Ml_double1_combined_unc, dMldR1_double1_combined, dMldR2_double1_combined, dMldeff_double1_combined = calc_dMl(gatewidth_list, a3_double1_combined, a4_double1_combined, R1_combined, R1_combined_unc, R2_double1_Y2_decay_combined, R2_single_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Fs_double1_combined, a5_double1_combined, a6_double1_combined, a7_double1_combined = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_double1_Y2_decay_combined, eff)
                        Fs_double1_combined_unc, dFsdR1_double1_combined, dFsdR2_double1_combined, dFsdeff_double1_combined = calc_dFs(gatewidth_list, a5_double1_combined, a6_double1_combined, a7_double1_combined, R1_combined, R1_combined_unc, R2_double1_Y2_decay_combined, R2_single_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Mt_double1_combined = calc_Mt(gatewidth_list, Ml_double1_combined, nuI1, alpha)
                        Mt_double1_combined_unc = calc_dMt(gatewidth_list, nuI1, alpha, Ml_double1_combined_unc)
                        kp_double1_combined = calc_kp(gatewidth_list, Mt_double1_combined)
                        kp_double1_combined_unc = calc_dkp(gatewidth_list, Mt_double1_combined, Mt_double1_combined_unc)
                        keff_double1_combined = calc_keff(gatewidth_list, kp_double1_combined, beta_eff)
                        keff_double1_combined_unc = calc_dkeff(gatewidth_list, kp_double1_combined_unc, beta_eff)
                        Ml_double2_combined, a1_double2_combined, a2_double2_combined, a3_double2_combined, a4_double2_combined = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_double2_Y2_decay_combined, eff)
                        Ml_double2_combined_unc, dMldR1_double2_combined, dMldR2_double2_combined, dMldeff_double2_combined = calc_dMl(gatewidth_list, a3_double2_combined, a4_double2_combined, R1_combined, R1_combined_unc, R2_double2_Y2_decay_combined, R2_double2_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Fs_double2_combined, a5_double2_combined, a6_double2_combined, a7_double2_combined = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_double2_Y2_decay_combined, eff)
                        Fs_double2_combined_unc, dFsdR1_double2_combined, dFsdR2_double2_combined, dFsdeff_double2_combined = calc_dFs(gatewidth_list, a5_double2_combined, a6_double2_combined, a7_double2_combined, R1_combined, R1_combined_unc, R2_double2_Y2_decay_combined, R2_double2_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Mt_double2_combined = calc_Mt(gatewidth_list, Ml_double2_combined, nuI1, alpha)
                        Mt_double2_combined_unc = calc_dMt(gatewidth_list, nuI1, alpha, Ml_double2_combined_unc)
                        kp_double2_combined = calc_kp(gatewidth_list, Mt_double2_combined)
                        kp_double2_combined_unc = calc_dkp(gatewidth_list, Mt_double2_combined, Mt_double2_combined_unc)
                        keff_double2_combined = calc_keff(gatewidth_list, kp_double2_combined, beta_eff)
                        keff_double2_combined_unc = calc_dkeff(gatewidth_list, kp_double2_combined_unc, beta_eff)
                        Ml_double_both_combined, a1_double_both_combined, a2_double_both_combined, a3_double_both_combined, a4_double_both_combined = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_double_both_Y2_decay_combined, eff)
                        Ml_double_both_combined_unc, dMldR1_double_both_combined, dMldR2_double_both_combined, dMldeff_double_both_combined = calc_dMl(gatewidth_list, a3_double_both_combined, a4_double_both_combined, R1_combined, R1_combined_unc, R2_double_both_Y2_decay_combined, R2_double_both_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Fs_double_both_combined, a5_double_both_combined, a6_double_both_combined, a7_double_both_combined = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_double_both_Y2_decay_combined, eff)
                        Fs_double_both_combined_unc, dFsdR1_double_both_combined, dFsdR2_double_both_combined, dFsdeff_double_both_combined = calc_dFs(gatewidth_list, a5_double_both_combined, a6_double_both_combined, a7_double_both_combined, R1_combined, R1_combined_unc, R2_double_both_Y2_decay_combined, R2_double_both_Y2_decay_combined_unc, dR1R2_combined, eff, deff)
                        Mt_double_both_combined = calc_Mt(gatewidth_list, Ml_double_both_combined, nuI1, alpha)
                        Mt_double_both_combined_unc = calc_dMt(gatewidth_list, nuI1, alpha, Ml_double_both_combined_unc)
                        kp_double_both_combined = calc_kp(gatewidth_list, Mt_double_both_combined)
                        kp_double_both_combined_unc = calc_dkp(gatewidth_list, Mt_double_both_combined, Mt_double_both_combined_unc)
                        keff_double_both_combined = calc_keff(gatewidth_list, kp_double_both_combined, beta_eff)
                        keff_double_both_combined_unc = calc_dkeff(gatewidth_list, kp_double_both_combined_unc, beta_eff)
                    if use_user_specified_lifetime == True:
                        Ml_user_lifetime_combined, a1_user_lifetime_combined, a2_user_lifetime_combined, a3_user_lifetime_combined, a4_user_lifetime_combined = calc_Ml(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_user_lifetime_combined_Y2_decay, eff)
                        Ml_user_lifetime_combined_unc, dMldR1_user_lifetime_combined, dMldR2_user_lifetime_combined, dMldeff_user_lifetime_combined = calc_dMl(gatewidth_list, a3_user_lifetime_combined, a4_user_lifetime_combined, R1_combined, R1_combined_unc, R2_user_lifetime_combined_Y2_decay, R2_unc_user_lifetime_Y2_decay, dR1R2_combined, eff, deff)
                        Fs_user_lifetime_combined, a5_user_lifetime_combined, a6_user_lifetime_combined, a7_user_lifetime_combined = calc_Fs(gatewidth_list, nuS1, nuS2, nuI1, nuI2, R1_combined, R2_user_lifetime_combined_Y2_decay, eff)
                        Fs_user_lifetime_combined_unc, dFsdR1_user_lifetime_combined, dFsdR2_user_lifetime_combined, dFsdeff_user_lifetime_combined = calc_dFs(gatewidth_list, a5_user_lifetime_combined, a6_user_lifetime_combined, a7_user_lifetime_combined, R1_combined, R1_combined_unc, R2_user_lifetime_combined_Y2_decay, R2_unc_user_lifetime_Y2_decay, dR1R2_combined, eff, deff)
                        Mt_user_lifetime_combined = calc_Mt(gatewidth_list, Ml_user_lifetime_combined, nuI1, alpha)
                        Mt_user_lifetime_combined_unc = calc_dMt(gatewidth_list, nuI1, alpha, Ml_user_lifetime_combined_unc)
                        kp_user_lifetime_combined = calc_kp(gatewidth_list, Mt_user_lifetime_combined)
                        kp_user_lifetime_combined_unc = calc_dkp(gatewidth_list, Mt_user_lifetime_combined, Mt_user_lifetime_combined_unc)
                        keff_user_lifetime_combined = calc_keff(gatewidth_list, kp_user_lifetime_combined, beta_eff)
                        keff_user_lifetime_combined_unc = calc_dkeff(gatewidth_list, kp_user_lifetime_combined_unc, beta_eff)
                        
                # plots from FeynmanYAnalysis.py
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combined/Rates/', 'FeynmanYan_Y2_', current_file, add_current_file=False, make_dirs=True)
                if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                    plotY2_xml(gatewidth_list, Y2_combined, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, residuals=False, gaussianBins=50, show=False, save=current_save_path)
                
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combined/Rates/', 'FeynmanYan_Y2_residuals_', current_file, add_current_file=False, make_dirs=True)
                if perform_Y2_single_fit == True and perform_Y2_double_fit == True:
                    plotResiduals_xml(gatewidth_list, Y2_combined, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, gaussianBins=100, show=False, save=current_save_path)
                    
            # plot combined results
            current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combined/Rates/', '', current_file, add_current_file=False, make_dirs=True)   
            
            plot_scatter_gatewidth('Combined', 'Y1', 'micro-sec', gatewidth_list, Y1_combined, marker_size, plot_titles, current_file[:-4], y_unc=Y1_combined_unc, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth('Combined', 'dY1', 'micro-sec', gatewidth_list, Y1_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth('Combined', 'R1', 'micro-sec', gatewidth_list, R1_combined, marker_size, plot_titles, current_file[:-4], y_unc=R1_combined_unc, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth('Combined', 'dR1', 'micro-sec', gatewidth_list, R1_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth('Combined', 'Y2', 'micro-sec', gatewidth_list, Y2_combined, marker_size, plot_titles, current_file[:-4], y_unc=Y2_combined_unc, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth('Combined', 'dY2', 'micro-sec', gatewidth_list, Y2_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth('Combined', 'Ym', 'micro-sec', gatewidth_list, Ym_combined, marker_size, plot_titles, current_file[:-4], y_unc=Ym_combined_unc, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            plot_scatter_gatewidth('Combined', 'dYm', 'micro-sec', gatewidth_list, Ym_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_single_fit == True:
                plot_scatter_gatewidth('Combined', 'R2', 'micro-sec', gatewidth_list, R2_single_Y2_decay_combined, marker_size, plot_titles, current_file[:-4], y_unc=R2_single_Y2_decay_combined_unc, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'dR2', 'micro-sec', gatewidth_list, R2_single_Y2_decay_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                plot_scatter_gatewidth('Combined', 'R2', 'micro-sec', gatewidth_list, R2_double1_Y2_decay_combined, marker_size, plot_titles, current_file[:-4], y_unc=R2_double1_Y2_decay_combined_unc, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'dR2', 'micro-sec', gatewidth_list, R2_double1_Y2_decay_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'R2', 'micro-sec', gatewidth_list, R2_double2_Y2_decay_combined, marker_size, plot_titles, current_file[:-4], y_unc=R2_double2_Y2_decay_combined_unc, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'dR2', 'micro-sec', gatewidth_list, R2_double2_Y2_decay_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'R2', 'micro-sec', gatewidth_list, R2_double_both_Y2_decay_combined, marker_size, plot_titles, current_file[:-4], y_unc=R2_double_both_Y2_decay_combined_unc, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'dR2', 'micro-sec', gatewidth_list, R2_double_both_Y2_decay_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
            if use_user_specified_lifetime == True:
                plot_scatter_gatewidth('Combined', 'R2', 'micro-sec', gatewidth_list, R2_user_lifetime_combined, marker_size, plot_titles, current_file[:-4], y_unc=R2_user_lifetime_combined_unc, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'dR2', 'micro-sec', gatewidth_list, R2_user_lifetime_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
            if calculation_type == 'Cf':
                plot_scatter_gatewidth('Combined', 'Efficiency', 'micro-sec', gatewidth_list, calc_eff_kn_combined, marker_size, plot_titles, current_file[:-4], y_unc=calc_eff_kn_combined_unc, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
                plot_scatter_gatewidth('Combined', 'dEfficiency', 'micro-sec', gatewidth_list, calc_eff_kn_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
            elif calculation_type == 'Multiplicity':
                if perform_Y2_single_fit == True:
                    plot_scatter_gatewidth('Combined', 'Ml', 'micro-sec', gatewidth_list, Ml_single_combined, marker_size, plot_titles, current_file[:-4], y_unc=Ml_single_combined_unc, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMl', 'micro-sec', gatewidth_list, Ml_single_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Fs', 'micro-sec', gatewidth_list, Fs_single_combined, marker_size, plot_titles, current_file[:-4], y_unc=Fs_single_combined_unc, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dFs', 'micro-sec', gatewidth_list, Fs_single_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Mt', 'micro-sec', gatewidth_list, Mt_single_combined, marker_size, plot_titles, current_file[:-4], y_unc=Mt_single_combined_unc, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMt', 'micro-sec', gatewidth_list, Mt_single_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'kp', 'micro-sec', gatewidth_list, kp_single_combined, marker_size, plot_titles, current_file[:-4], y_unc=kp_single_combined_unc, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkp', 'micro-sec', gatewidth_list, kp_single_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'keff', 'micro-sec', gatewidth_list, keff_single_combined, marker_size, plot_titles, current_file[:-4], y_unc=keff_single_combined_unc, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkeff', 'micro-sec', gatewidth_list, keff_single_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                    plot_scatter_gatewidth('Combined', 'Ml', 'micro-sec', gatewidth_list, Ml_double1_combined, marker_size, plot_titles, current_file[:-4], y_unc=Ml_double1_combined_unc, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMl', 'micro-sec', gatewidth_list, Ml_double1_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Fs', 'micro-sec', gatewidth_list, Fs_double1_combined, marker_size, plot_titles, current_file[:-4], y_unc=Fs_double1_combined_unc, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dFs', 'micro-sec', gatewidth_list, Fs_double1_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Mt', 'micro-sec', gatewidth_list, Mt_double1_combined, marker_size, plot_titles, current_file[:-4], y_unc=Mt_double1_combined_unc, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMt', 'micro-sec', gatewidth_list, Mt_double1_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'kp', 'micro-sec', gatewidth_list, kp_double1_combined, marker_size, plot_titles, current_file[:-4], y_unc=kp_double1_combined_unc, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkp', 'micro-sec', gatewidth_list, kp_double1_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'keff', 'micro-sec', gatewidth_list, keff_double1_combined, marker_size, plot_titles, current_file[:-4], y_unc=keff_double1_combined_unc, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkeff', 'micro-sec', gatewidth_list, keff_double1_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Ml', 'micro-sec', gatewidth_list, Ml_double2_combined, marker_size, plot_titles, current_file[:-4], y_unc=Ml_double2_combined_unc, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMl', 'micro-sec', gatewidth_list, Ml_double2_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Fs', 'micro-sec', gatewidth_list, Fs_double2_combined, marker_size, plot_titles, current_file[:-4], y_unc=Fs_double2_combined_unc, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dFs', 'micro-sec', gatewidth_list, Fs_double2_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Mt', 'micro-sec', gatewidth_list, Mt_double2_combined, marker_size, plot_titles, current_file[:-4], y_unc=Mt_double2_combined_unc, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMt', 'micro-sec', gatewidth_list, Mt_double2_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'kp', 'micro-sec', gatewidth_list, kp_double2_combined, marker_size, plot_titles, current_file[:-4], y_unc=kp_double2_combined_unc, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkp', 'micro-sec', gatewidth_list, kp_double2_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'keff', 'micro-sec', gatewidth_list, keff_double2_combined, marker_size, plot_titles, current_file[:-4], y_unc=keff_double2_combined_unc, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkeff', 'micro-sec', gatewidth_list, keff_double2_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Ml', 'micro-sec', gatewidth_list, Ml_double_both_combined, marker_size, plot_titles, current_file[:-4], y_unc=Ml_double_both_combined_unc, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMl', 'micro-sec', gatewidth_list, Ml_double_both_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Fs', 'micro-sec', gatewidth_list, Fs_double_both_combined, marker_size, plot_titles, current_file[:-4], y_unc=Fs_double_both_combined_unc, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dFs', 'micro-sec', gatewidth_list, Fs_double_both_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Mt', 'micro-sec', gatewidth_list, Mt_double_both_combined, marker_size, plot_titles, current_file[:-4], y_unc=Mt_double_both_combined_unc, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMt', 'micro-sec', gatewidth_list, Mt_double_both_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'kp', 'micro-sec', gatewidth_list, kp_double_both_combined, marker_size, plot_titles, current_file[:-4], y_unc=kp_double_both_combined_unc, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkp', 'micro-sec', gatewidth_list, kp_double_both_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'keff', 'micro-sec', gatewidth_list, keff_double_both_combined, marker_size, plot_titles, current_file[:-4], y_unc=keff_double_both_combined_unc, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkeff', 'micro-sec', gatewidth_list, keff_double_both_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
                if use_user_specified_lifetime == True:
                    plot_scatter_gatewidth('Combined', 'Ml', 'micro-sec', gatewidth_list, Ml_user_lifetime_combined, marker_size, plot_titles, current_file[:-4], y_unc=Ml_user_lifetime_combined_unc, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMl', 'micro-sec', gatewidth_list, Ml_user_lifetime_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Fs', 'micro-sec', gatewidth_list, Fs_user_lifetime_combined, marker_size, plot_titles, current_file[:-4], y_unc=Fs_user_lifetime_combined_unc, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dFs', 'micro-sec', gatewidth_list, Fs_user_lifetime_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'Mt', 'micro-sec', gatewidth_list, Mt_user_lifetime_combined, marker_size, plot_titles, current_file[:-4], y_unc=Mt_user_lifetime_combined_unc, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dMt', 'micro-sec', gatewidth_list, Mt_user_lifetime_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'kp', 'micro-sec', gatewidth_list, kp_user_lifetime_combined, marker_size, plot_titles, current_file[:-4], y_unc=kp_user_lifetime_combined_unc, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkp', 'micro-sec', gatewidth_list, kp_user_lifetime_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'keff', 'micro-sec', gatewidth_list, keff_user_lifetime_combined, marker_size, plot_titles, current_file[:-4], y_unc=keff_user_lifetime_combined_unc, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
                    plot_scatter_gatewidth('Combined', 'dkeff', 'micro-sec', gatewidth_list, keff_user_lifetime_combined_unc, marker_size, plot_titles, current_file[:-4], y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime_fit', mult_files=False, yaxis_log=yaxis_log)
            
            # output a single csv file for the combined results
            if output_csv == True:
                current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combined/Rates/', '', current_file, add_current_file=False, make_dirs=True)   
                
                # rates list
                csv_name = current_save_path+'Combined_rates.csv'
                    
                # set N/A to lists if fits were not performed
                if perform_Y2_single_fit != True:
                    R2_single_Y2_decay_combined = R2_single_Y2_decay_combined_unc = ['N/A' for i in range(0,len(gatewidth_list))]
                if perform_Y2_double_fit != True or perform_Y2_double_fit_continue != True:
                    R2_double1_Y2_decay_combined = R2_double1_Y2_decay_combined_unc = R2_double2_Y2_decay_combined = R2_double2_Y2_decay_combined_unc = R2_double_both_Y2_decay_combined = R2_double_both_Y2_decay_combined_unc = ['N/A' for i in range(0,len(gatewidth_list))]
                if use_user_specified_lifetime != True:
                    R2_user_lifetime_combined = R2_user_lifetime_combined_unc = ['N/A' for i in range(0,len(gatewidth_list))]
                if combine_Y2_rate_results_old_method != True:
                    R2_single_Y2_decay_combined_sd = R2_single_Y2_decay_individual_unc_avg = R2_double1_Y2_decay_combined_sd = R2_double1_Y2_decay_individual_unc_avg = R2_double2_Y2_decay_combined_sd = R2_double2_Y2_decay_individual_unc_avg = R2_double_both_Y2_decay_combined_sd = R2_double_both_Y2_decay_individual_unc_avg = R2_user_lifetime_combined_sd = R2_user_lifetime_individual_unc_avg = Ml_single_combined_sd = Ml_single_individual_unc_avg = Fs_single_individual_unc_avg = Fs_single_combined_sd = Mt_single_combined_sd = Mt_single_individual_unc_avg = kp_single_combined_sd = kp_single_individual_unc_avg = keff_single_combined_sd = keff_single_individual_unc_avg = Ml_double1_combined_sd = Ml_double1_individual_unc_avg = Fs_double1_individual_unc_avg = Fs_double1_combined_sd = Mt_double1_combined_sd = Mt_double1_individual_unc_avg = kp_double1_combined_sd = kp_double1_individual_unc_avg = keff_double1_combined_sd = keff_double1_individual_unc_avg = Ml_double2_combined_sd = Ml_double2_individual_unc_avg = Fs_double2_individual_unc_avg = Fs_double2_combined_sd = Mt_double2_combined_sd = Mt_double2_individual_unc_avg = kp_double2_combined_sd = kp_double2_individual_unc_avg = keff_double2_combined_sd = keff_double2_individual_unc_avg = Ml_double_both_combined_sd = Ml_double_both_individual_unc_avg = Fs_double_both_individual_unc_avg = Fs_double_both_combined_sd = Mt_double_both_combined_sd = Mt_double_both_individual_unc_avg = kp_double_both_combined_sd = kp_double_both_individual_unc_avg = keff_double_both_combined_sd = keff_double_both_individual_unc_avg = Ml_user_lifetime_combined_sd = Ml_user_lifetime_individual_unc_avg = Fs_user_lifetime_individual_unc_avg = Fs_user_lifetime_combined_sd = Mt_user_lifetime_combined_sd = Mt_user_lifetime_individual_unc_avg = kp_user_lifetime_combined_sd = kp_user_lifetime_individual_unc_avg = keff_user_lifetime_combined_sd = keff_user_lifetime_individual_unc_avg = ['N/A' for i in range(0,len(gatewidth_list))]
                with open(csv_name, mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    header_row = ['Gate-width','Y1','dY1 combined','Y1 sd','dY1 individual unc avg','Y2','dY2 combined','Y2 sd','dY2 individual unc avg','R1','dR1 combined','R1 sd','dR1 individual unc avg','R2_single_Y2_decay','R2_unc_single_Y2_decay combined','R2_single_Y2_decay sd','R2_unc_single_Y2_decay individual unc avg','R2_double1_Y2_decay','R2_unc_double1_Y2_decay combined','R2_double1_Y2_decay sd','R2_unc_double1_Y2_decay unc avg','R2_double2_Y2_decay','R2_unc_double2_Y2_decay combined','R2_double2_Y2_decay sd','R2_unc_double2_Y2_decay unc avg','R2_double_both_Y2_decay','R2_unc_double_both_Y2_decay combined','R2_double_both_Y2_decay sd','R2_unc_double_both_Y2_decay unc avg','R2_user_lifetime','R2_unc_user_lifetime combined','R2_user_lifetime sd','R2_unc_user_lifetime unc avg','Ym','dYm combined','Ym sd','dYm unc avg']
                    if calculation_type == 'Cf':
                        header_row.append('eff from Cf')
                        header_row.append('deff from Cf combined')
                        header_row.append('eff from Cf sd')
                        header_row.append('deff from Cf individual unc avg')
                    elif calculation_type == 'Multiplicity':
                        if perform_Y2_single_fit == True:
                            header_row.append('Ml (Y2 single)')
                            header_row.append('dMl combined (Y2 single)')
                            header_row.append('Ml sd')
                            header_row.append('Ml individual unc avg  (Y2 single)')
                            header_row.append('Fs (Y2 single)')
                            header_row.append('dFs combined (Y2 single)')
                            header_row.append('Fs sd')
                            header_row.append('Fs individual unc avg  (Y2 single)')
                            header_row.append('Mt (Y2 single)')
                            header_row.append('dMt combined (Y2 single)')
                            header_row.append('Mt sd')
                            header_row.append('Mt individual unc avg  (Y2 single)')
                            header_row.append('kp (Y2 single)')
                            header_row.append('dkp combined (Y2 single)')
                            header_row.append('kp sd')
                            header_row.append('kp individual unc avg  (Y2 single)')
                            header_row.append('keff (Y2 single)')
                            header_row.append('dkeff combined (Y2 single)')
                            header_row.append('keff sd')
                            header_row.append('keff individual unc avg  (Y2 single)')
                        if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                            header_row.append('Ml (Y2 double1)')
                            header_row.append('dMl combined (Y2 double1)')
                            header_row.append('Ml sd')
                            header_row.append('Ml individual unc avg  (Y2 double1)')
                            header_row.append('Fs (Y2 double1)')
                            header_row.append('dFs combined (Y2 double1)')
                            header_row.append('Fs sd')
                            header_row.append('Fs individual unc avg  (Y2 double1)')
                            header_row.append('Mt (Y2 double1)')
                            header_row.append('dMt combined (Y2 double1)')
                            header_row.append('Mt sd')
                            header_row.append('Mt individual unc avg  (Y2 double1)')
                            header_row.append('kp (Y2 double1)')
                            header_row.append('dkp combined (Y2 double1)')
                            header_row.append('kp sd')
                            header_row.append('kp individual unc avg  (Y2 double1)')
                            header_row.append('keff (Y2 double1)')
                            header_row.append('dkeff combined (Y2 double1)')
                            header_row.append('keff sd')
                            header_row.append('keff individual unc avg  (Y2 double1)')
                            header_row.append('Ml (Y2 double2)')
                            header_row.append('dMl combined (Y2 double2)')
                            header_row.append('Ml sd')
                            header_row.append('Ml individual unc avg  (Y2 double2)')
                            header_row.append('Fs (Y2 double2)')
                            header_row.append('dFs combined (Y2 double2)')
                            header_row.append('Fs sd')
                            header_row.append('Fs individual unc avg  (Y2 double2)')
                            header_row.append('Mt (Y2 double2)')
                            header_row.append('dMt combined (Y2 double2)')
                            header_row.append('Mt sd')
                            header_row.append('Mt individual unc avg  (Y2 double2)')
                            header_row.append('kp (Y2 double2)')
                            header_row.append('dkp combined (Y2 double2)')
                            header_row.append('kp sd')
                            header_row.append('kp individual unc avg  (Y2 double2)')
                            header_row.append('keff (Y2 double2)')
                            header_row.append('dkeff combined (Y2 double2)')
                            header_row.append('keff sd')
                            header_row.append('keff individual unc avg  (Y2 double2)')
                            header_row.append('Ml (Y2 double_both)')
                            header_row.append('dMl combined (Y2 double_both)')
                            header_row.append('Ml sd')
                            header_row.append('Ml individual unc avg  (Y2 double_both)')
                            header_row.append('Fs (Y2 double_both)')
                            header_row.append('dFs combined (Y2 double_both)')
                            header_row.append('Fs sd')
                            header_row.append('Fs individual unc avg  (Y2 double_both)')
                            header_row.append('Mt (Y2 double_both)')
                            header_row.append('dMt combined (Y2 double_both)')
                            header_row.append('Mt sd')
                            header_row.append('Mt individual unc avg  (Y2 double_both)')
                            header_row.append('kp (Y2 double_both)')
                            header_row.append('dkp combined (Y2 double_both)')
                            header_row.append('kp sd')
                            header_row.append('kp individual unc avg  (Y2 double_both)')
                            header_row.append('keff (Y2 double_both)')
                            header_row.append('dkeff combined (Y2 double_both)')
                            header_row.append('keff sd')
                            header_row.append('keff individual unc avg  (Y2 double_both)')
                        if use_user_specified_lifetime == True:
                            header_row.append('Ml (Y2 user_lifetime)')
                            header_row.append('dMl combined (Y2 user_lifetime)')
                            header_row.append('Ml sd')
                            header_row.append('Ml individual unc avg  (Y2 user_lifetime)')
                            header_row.append('Fs (Y2 user_lifetime)')
                            header_row.append('dFs combined (Y2 user_lifetime)')
                            header_row.append('Fs sd')
                            header_row.append('Fs individual unc avg  (Y2 user_lifetime)')
                            header_row.append('Mt (Y2 user_lifetime)')
                            header_row.append('dMt combined (Y2 user_lifetime)')
                            header_row.append('Mt sd')
                            header_row.append('Mt individual unc avg  (Y2 user_lifetime)')
                            header_row.append('kp (Y2 user_lifetime)')
                            header_row.append('dkp combined (Y2 user_lifetime)')
                            header_row.append('kp sd')
                            header_row.append('kp individual unc avg  (Y2 user_lifetime)')
                            header_row.append('keff (Y2 user_lifetime)')
                            header_row.append('dkeff combined (Y2 user_lifetime)')
                            header_row.append('keff sd')
                            header_row.append('keff individual unc avg  (Y2 user_lifetime)')
                    writer.writerow(header_row)
                    for value in range(len(gatewidth_list)):
                        data_row = [gatewidth_list[value], Y1_combined[value], Y1_combined_unc[value], Y1_combined_sd[value], Y1_individual_unc_avg[value], Y2_combined[value], Y2_combined_unc[value], Y2_combined_sd[value], Y2_individual_unc_avg[value], R1_combined[value], R1_combined_unc[value], R1_combined_sd[value], R1_individual_unc_avg[value], R2_single_Y2_decay_combined[value], R2_single_Y2_decay_combined_unc[value], R2_single_Y2_decay_combined_sd[value], R2_single_Y2_decay_individual_unc_avg[value], R2_double1_Y2_decay_combined[value], R2_double1_Y2_decay_combined_unc[value], R2_double1_Y2_decay_combined_sd[value], R2_double1_Y2_decay_individual_unc_avg[value], R2_double2_Y2_decay_combined[value], R2_double2_Y2_decay_combined_unc[value], R2_double2_Y2_decay_combined_sd[value], R2_double2_Y2_decay_individual_unc_avg[value], R2_double_both_Y2_decay_combined[value], R2_double_both_Y2_decay_combined_unc[value], R2_double_both_Y2_decay_combined_sd[value], R2_double_both_Y2_decay_individual_unc_avg[value], R2_user_lifetime_combined[value], R2_user_lifetime_combined_unc[value], R2_user_lifetime_combined_sd[value], R2_user_lifetime_individual_unc_avg[value], Ym_combined[value], Ym_combined_unc[value], Ym_combined_sd[value], Ym_individual_unc_avg[value]]
                        if calculation_type == 'Cf':
                            data_row.append(calc_eff_kn_combined[value])
                            data_row.append(calc_eff_kn_combined_unc[value])
                            data_row.append(calc_eff_kn_combined_sd[value])
                            data_row.append(calc_eff_kn_individual_unc_avg[value])
                        if calculation_type == 'Multiplicity':
                            if perform_Y2_single_fit == True:
                                data_row.append(Ml_single_combined[value])
                                data_row.append(Ml_single_combined_unc[value])
                                data_row.append(Ml_single_combined_sd[value])
                                data_row.append(Ml_single_individual_unc_avg[value])
                                data_row.append(Fs_single_combined[value])
                                data_row.append(Fs_single_combined_unc[value])
                                data_row.append(Fs_single_combined_sd[value])
                                data_row.append(Fs_single_individual_unc_avg[value])
                                data_row.append(Mt_single_combined[value])
                                data_row.append(Mt_single_combined_unc[value])
                                data_row.append(Mt_single_combined_sd[value])
                                data_row.append(Mt_single_individual_unc_avg[value])
                                data_row.append(kp_single_combined[value])
                                data_row.append(kp_single_combined_unc[value])
                                data_row.append(kp_single_combined_sd[value])
                                data_row.append(kp_single_individual_unc_avg[value])
                                data_row.append(keff_single_combined[value])
                                data_row.append(keff_single_combined_unc[value])
                                data_row.append(keff_single_combined_sd[value])
                                data_row.append(keff_single_individual_unc_avg[value])
                            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                data_row.append(Ml_double1_combined[value])
                                data_row.append(Ml_double1_combined_unc[value])
                                data_row.append(Ml_double1_combined_sd[value])
                                data_row.append(Ml_double1_individual_unc_avg[value])
                                data_row.append(Fs_double1_combined[value])
                                data_row.append(Fs_double1_combined_unc[value])
                                data_row.append(Fs_double1_combined_sd[value])
                                data_row.append(Fs_double1_individual_unc_avg[value])
                                data_row.append(Mt_double1_combined[value])
                                data_row.append(Mt_double1_combined_unc[value])
                                data_row.append(Mt_double1_combined_sd[value])
                                data_row.append(Mt_double1_individual_unc_avg[value])
                                data_row.append(kp_double1_combined[value])
                                data_row.append(kp_double1_combined_unc[value])
                                data_row.append(kp_double1_combined_sd[value])
                                data_row.append(kp_double1_individual_unc_avg[value])
                                data_row.append(keff_double1_combined[value])
                                data_row.append(keff_double1_combined_unc[value])
                                data_row.append(keff_double1_combined_sd[value])
                                data_row.append(keff_double1_individual_unc_avg[value])
                                data_row.append(Ml_double2_combined[value])
                                data_row.append(Ml_double2_combined_unc[value])
                                data_row.append(Ml_double2_combined_sd[value])
                                data_row.append(Ml_double2_individual_unc_avg[value])
                                data_row.append(Fs_double2_combined[value])
                                data_row.append(Fs_double2_combined_unc[value])
                                data_row.append(Fs_double2_combined_sd[value])
                                data_row.append(Fs_double2_individual_unc_avg[value])
                                data_row.append(Mt_double2_combined[value])
                                data_row.append(Mt_double2_combined_unc[value])
                                data_row.append(Mt_double2_combined_sd[value])
                                data_row.append(Mt_double2_individual_unc_avg[value])
                                data_row.append(kp_double2_combined[value])
                                data_row.append(kp_double2_combined_unc[value])
                                data_row.append(kp_double2_combined_sd[value])
                                data_row.append(kp_double2_individual_unc_avg[value])
                                data_row.append(keff_double2_combined[value])
                                data_row.append(keff_double2_combined_unc[value])
                                data_row.append(keff_double2_combined_sd[value])
                                data_row.append(keff_double2_individual_unc_avg[value])
                                data_row.append(Ml_double_both_combined[value])
                                data_row.append(Ml_double_both_combined_unc[value])
                                data_row.append(Ml_double_both_combined_sd[value])
                                data_row.append(Ml_double_both_individual_unc_avg[value])
                                data_row.append(Fs_double_both_combined[value])
                                data_row.append(Fs_double_both_combined_unc[value])
                                data_row.append(Fs_double_both_combined_sd[value])
                                data_row.append(Fs_double_both_individual_unc_avg[value])
                                data_row.append(Mt_double_both_combined[value])
                                data_row.append(Mt_double_both_combined_unc[value])
                                data_row.append(Mt_double_both_combined_sd[value])
                                data_row.append(Mt_double_both_individual_unc_avg[value])
                                data_row.append(kp_double_both_combined[value])
                                data_row.append(kp_double_both_combined_unc[value])
                                data_row.append(kp_double_both_combined_sd[value])
                                data_row.append(kp_double_both_individual_unc_avg[value])
                                data_row.append(keff_double_both_combined[value])
                                data_row.append(keff_double_both_combined_unc[value])
                                data_row.append(keff_double_both_combined_sd[value])
                                data_row.append(keff_double_both_individual_unc_avg[value])
                            if use_user_specified_lifetime == True:
                                data_row.append(Ml_user_lifetime_combined[value])
                                data_row.append(Ml_user_lifetime_combined_unc[value])
                                data_row.append(Ml_user_lifetime_combined_sd[value])
                                data_row.append(Ml_user_lifetime_individual_unc_avg[value])
                                data_row.append(Fs_user_lifetime_combined[value])
                                data_row.append(Fs_user_lifetime_combined_unc[value])
                                data_row.append(Fs_user_lifetime_combined_sd[value])
                                data_row.append(Fs_user_lifetime_individual_unc_avg[value])
                                data_row.append(Mt_user_lifetime_combined[value])
                                data_row.append(Mt_user_lifetime_combined_unc[value])
                                data_row.append(Mt_user_lifetime_combined_sd[value])
                                data_row.append(Mt_user_lifetime_individual_unc_avg[value])
                                data_row.append(kp_user_lifetime_combined[value])
                                data_row.append(kp_user_lifetime_combined_unc[value])
                                data_row.append(kp_user_lifetime_combined_sd[value])
                                data_row.append(kp_user_lifetime_individual_unc_avg[value])
                                data_row.append(keff_user_lifetime_combined[value])
                                data_row.append(keff_user_lifetime_combined_unc[value])
                                data_row.append(keff_user_lifetime_combined_sd[value])
                                data_row.append(keff_user_lifetime_individual_unc_avg[value])
                        writer.writerow(data_row)
                        
                if compare_combine_Y2_rate_results_and_Feynman_sum == True and sum_Feynman_histograms == True:
                    combine_Y2_rate_results_filepath = current_save_path
                    print('Note: compare_combine_Y2_rate_results_and_Feynman_sum, output_csv, combine_Y2_rate_results, and sum_Feynman_histograms are all set to True. The user combine_Y2_rate_results_filepath is being ignore. combine_Y2_rate_results_filepath is set to ',combine_Y2_rate_results_filepath)
            
            if combine_statistical_plots == True:
                
                print('combine Y2 rate results: combine_statistical_plots')
                print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
                
                # plot combined statistical plots
                m1_transposed = np.array(first_reduced_factorial_moment_all_files).T.tolist()
                m2_transposed = np.array(second_reduced_factorial_moment_all_files).T.tolist()
                m3_transposed = np.array(third_reduced_factorial_moment_all_files).T.tolist()
                m4_transposed = np.array(fourth_reduced_factorial_moment_all_files).T.tolist()
                C1_transposed = np.array(first_factorial_moment_all_files).T.tolist()
                C2_transposed = np.array(second_factorial_moment_all_files).T.tolist()
                C3_transposed = np.array(third_factorial_moment_all_files).T.tolist()
                C4_transposed = np.array(fourth_factorial_moment_all_files).T.tolist()
                Y1_transposed = np.array(Y1_all_files).T.tolist()
                dY1_transposed = np.array(dY1_all_files).T.tolist()
                R1_transposed = np.array(R1_all_files).T.tolist()
                dR1_transposed = np.array(dR1_all_files).T.tolist()
                Y2_transposed = np.array(Y2_all_files).T.tolist()
                dY2_transposed = np.array(dY2_all_files).T.tolist()
                Ym_transposed = np.array(Ym_all_files).T.tolist()
                dYm_transposed = np.array(dYm_all_files).T.tolist()
                if perform_Y2_single_fit == True:
                    omega2_single_results_transposed = np.array(omega2_single_results_all_files).T.tolist()
                    R2_single_Y2_decay_transposed = np.array(R2_single_Y2_decay_all_files).T.tolist()
                    R2_unc_single_Y2_decay_transposed = np.array(R2_unc_single_Y2_decay_all_files).T.tolist()
                if perform_Y2_double_fit == True:
                    omega2_double1_results_transposed = np.array(omega2_double1_results_all_files).T.tolist()
                    R2_double1_Y2_decay_transposed = np.array(R2_double1_Y2_decay_all_files).T.tolist()
                    R2_unc_double1_Y2_decay_transposed = np.array(R2_unc_double1_Y2_decay_all_files).T.tolist()
                    omega2_double2_results_transposed = np.array(omega2_double2_results_all_files).T.tolist()
                    R2_double2_Y2_decay_transposed = np.array(R2_double2_Y2_decay_all_files).T.tolist()
                    R2_unc_double2_Y2_decay_transposed = np.array(R2_unc_double2_Y2_decay_all_files).T.tolist()
                    R2_double_both_Y2_decay_transposed = np.array(R2_double_both_Y2_decay_all_files).T.tolist()
                    R2_unc_double_both_Y2_decay_transposed = np.array(R2_unc_double_both_Y2_decay_all_files).T.tolist()
                if use_user_specified_lifetime == True:
                    omega2_lifetime_user_results_transposed = np.array(omega2_lifetime_user_results_all_files).T.tolist()
                    R2_user_lifetime_transposed = np.array(R2_user_lifetime_all_files).T.tolist()
                    R2_unc_user_lifetime_transposed = np.array(R2_unc_user_lifetime_all_files).T.tolist()
                if calculation_type == 'Cf':
                    calc_eff_kn_transposed = np.array(calc_eff_kn_all_files).T.tolist()
                    calc_eff_unc_kn_transposed = np.array(calc_eff_unc_kn_all_files).T.tolist()
                elif calculation_type == 'Multiplicity':
                    dR1R2_transposed = np.array(dR1R2_all_files).T.tolist()
                    if perform_Y2_single_fit == True:
                        a1_single_transposed = np.array(a1_single_all_files).T.tolist()
                        a2_single_transposed = np.array(a2_single_all_files).T.tolist()
                        a3_single_transposed = np.array(a3_single_all_files).T.tolist()
                        a4_single_transposed = np.array(a4_single_all_files).T.tolist()
                        a5_single_transposed = np.array(a5_single_all_files).T.tolist()
                        a6_single_transposed = np.array(a6_single_all_files).T.tolist()
                        a7_single_transposed = np.array(a7_single_all_files).T.tolist()
                        Ml_single_transposed = np.array(Ml_single_all_files).T.tolist()
                        dMl_single_transposed = np.array(dMl_single_all_files).T.tolist()
                        dMldR1_single_transposed = np.array(dMldR1_single_all_files).T.tolist()
                        dMldR2_single_transposed = np.array(dMldR2_single_all_files).T.tolist()
                        dMldeff_single_transposed = np.array(dMldeff_single_all_files).T.tolist()
                        Mt_single_transposed = np.array(Mt_single_all_files).T.tolist()
                        dMt_single_transposed = np.array(dMt_single_all_files).T.tolist()
                        Fs_single_transposed = np.array(Fs_single_all_files).T.tolist()
                        dFs_single_transposed = np.array(dFs_single_all_files).T.tolist()
                        dFsdR1_single_transposed = np.array(dFsdR1_single_all_files).T.tolist()
                        dFsdR2_single_transposed = np.array(dFsdR2_single_all_files).T.tolist()
                        dFsdeff_single_transposed = np.array(dFsdeff_single_all_files).T.tolist()
                        kp_single_transposed = np.array(kp_single_all_files).T.tolist()
                        dkp_single_transposed = np.array(dkp_single_all_files).T.tolist()
                        keff_single_transposed = np.array(keff_single_all_files).T.tolist()
                        dkeff_single_transposed = np.array(dkeff_single_all_files).T.tolist()
                    if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                        a1_double1_transposed = np.array(a1_double1_all_files).T.tolist()
                        a2_double1_transposed = np.array(a2_double1_all_files).T.tolist()
                        a3_double1_transposed = np.array(a3_double1_all_files).T.tolist()
                        a4_double1_transposed = np.array(a4_double1_all_files).T.tolist()
                        a5_double1_transposed = np.array(a5_double1_all_files).T.tolist()
                        a6_double1_transposed = np.array(a6_double1_all_files).T.tolist()
                        a7_double1_transposed = np.array(a7_double1_all_files).T.tolist()
                        Ml_double1_transposed = np.array(Ml_double1_all_files).T.tolist()
                        dMl_double1_transposed = np.array(dMl_double1_all_files).T.tolist()
                        dMldR1_double1_transposed = np.array(dMldR1_double1_all_files).T.tolist()
                        dMldR2_double1_transposed = np.array(dMldR2_double1_all_files).T.tolist()
                        dMldeff_double1_transposed = np.array(dMldeff_double1_all_files).T.tolist()
                        Mt_double1_transposed = np.array(Mt_double1_all_files).T.tolist()
                        dMt_double1_transposed = np.array(dMt_double1_all_files).T.tolist()
                        Fs_double1_transposed = np.array(Fs_double1_all_files).T.tolist()
                        dFs_double1_transposed = np.array(dFs_double1_all_files).T.tolist()
                        dFsdR1_double1_transposed = np.array(dFsdR1_double1_all_files).T.tolist()
                        dFsdR2_double1_transposed = np.array(dFsdR2_double1_all_files).T.tolist()
                        dFsdeff_double1_transposed = np.array(dFsdeff_double1_all_files).T.tolist()
                        kp_double1_transposed = np.array(kp_double1_all_files).T.tolist()
                        dkp_double1_transposed = np.array(dkp_double1_all_files).T.tolist()
                        keff_double1_transposed = np.array(keff_double1_all_files).T.tolist()
                        dkeff_double1_transposed = np.array(dkeff_double1_all_files).T.tolist()
                        a1_double2_transposed = np.array(a1_double2_all_files).T.tolist()
                        a2_double2_transposed = np.array(a2_double2_all_files).T.tolist()
                        a3_double2_transposed = np.array(a3_double2_all_files).T.tolist()
                        a4_double2_transposed = np.array(a4_double2_all_files).T.tolist()
                        a5_double2_transposed = np.array(a5_double2_all_files).T.tolist()
                        a6_double2_transposed = np.array(a6_double2_all_files).T.tolist()
                        a7_double2_transposed = np.array(a7_double2_all_files).T.tolist()
                        Ml_double2_transposed = np.array(Ml_double2_all_files).T.tolist()
                        dMl_double2_transposed = np.array(dMl_double2_all_files).T.tolist()
                        dMldR1_double2_transposed = np.array(dMldR1_double2_all_files).T.tolist()
                        dMldR2_double2_transposed = np.array(dMldR2_double2_all_files).T.tolist()
                        dMldeff_double2_transposed = np.array(dMldeff_double2_all_files).T.tolist()
                        Mt_double2_transposed = np.array(Mt_double2_all_files).T.tolist()
                        dMt_double2_transposed = np.array(dMt_double2_all_files).T.tolist()
                        Fs_double2_transposed = np.array(Fs_double2_all_files).T.tolist()
                        dFs_double2_transposed = np.array(dFs_double2_all_files).T.tolist()
                        dFsdR1_double2_transposed = np.array(dFsdR1_double2_all_files).T.tolist()
                        dFsdR2_double2_transposed = np.array(dFsdR2_double2_all_files).T.tolist()
                        dFsdeff_double2_transposed = np.array(dFsdeff_double2_all_files).T.tolist()
                        kp_double2_transposed = np.array(kp_double2_all_files).T.tolist()
                        dkp_double2_transposed = np.array(dkp_double2_all_files).T.tolist()
                        keff_double2_transposed = np.array(keff_double2_all_files).T.tolist()
                        dkeff_double2_transposed = np.array(dkeff_double2_all_files).T.tolist()
                        a1_double_both_transposed = np.array(a1_double_both_all_files).T.tolist()
                        a2_double_both_transposed = np.array(a2_double_both_all_files).T.tolist()
                        a3_double_both_transposed = np.array(a3_double_both_all_files).T.tolist()
                        a4_double_both_transposed = np.array(a4_double_both_all_files).T.tolist()
                        a5_double_both_transposed = np.array(a5_double_both_all_files).T.tolist()
                        a6_double_both_transposed = np.array(a6_double_both_all_files).T.tolist()
                        a7_double_both_transposed = np.array(a7_double_both_all_files).T.tolist()
                        Ml_double_both_transposed = np.array(Ml_double_both_all_files).T.tolist()
                        dMl_double_both_transposed = np.array(dMl_double_both_all_files).T.tolist()
                        dMldR1_double_both_transposed = np.array(dMldR1_double_both_all_files).T.tolist()
                        dMldR2_double_both_transposed = np.array(dMldR2_double_both_all_files).T.tolist()
                        dMldeff_double_both_transposed = np.array(dMldeff_double_both_all_files).T.tolist()
                        Mt_double_both_transposed = np.array(Mt_double_both_all_files).T.tolist()
                        dMt_double_both_transposed = np.array(dMt_double_both_all_files).T.tolist()
                        Fs_double_both_transposed = np.array(Fs_double_both_all_files).T.tolist()
                        dFs_double_both_transposed = np.array(dFs_double_both_all_files).T.tolist()
                        dFsdR1_double_both_transposed = np.array(dFsdR1_double_both_all_files).T.tolist()
                        dFsdR2_double_both_transposed = np.array(dFsdR2_double_both_all_files).T.tolist()
                        dFsdeff_double_both_transposed = np.array(dFsdeff_double_both_all_files).T.tolist()
                        kp_double_both_transposed = np.array(kp_double_both_all_files).T.tolist()
                        dkp_double_both_transposed = np.array(dkp_double_both_all_files).T.tolist()
                        keff_double_both_transposed = np.array(keff_double_both_all_files).T.tolist()
                        dkeff_double_both_transposed = np.array(dkeff_double_both_all_files).T.tolist()
                    if use_user_specified_lifetime == True:
                        a1_user_lifetime_transposed = np.array(a1_user_lifetime_all_files).T.tolist()
                        a2_user_lifetime_transposed = np.array(a2_user_lifetime_all_files).T.tolist()
                        a3_user_lifetime_transposed = np.array(a3_user_lifetime_all_files).T.tolist()
                        a4_user_lifetime_transposed = np.array(a4_user_lifetime_all_files).T.tolist()
                        a5_user_lifetime_transposed = np.array(a5_user_lifetime_all_files).T.tolist()
                        a6_user_lifetime_transposed = np.array(a6_user_lifetime_all_files).T.tolist()
                        a7_user_lifetime_transposed = np.array(a7_user_lifetime_all_files).T.tolist()
                        Ml_user_lifetime_transposed = np.array(Ml_user_lifetime_all_files).T.tolist()
                        dMl_user_lifetime_transposed = np.array(dMl_user_lifetime_all_files).T.tolist()
                        dMldR1_user_lifetime_transposed = np.array(dMldR1_user_lifetime_all_files).T.tolist()
                        dMldR2_user_lifetime_transposed = np.array(dMldR2_user_lifetime_all_files).T.tolist()
                        dMldeff_user_lifetime_transposed = np.array(dMldeff_user_lifetime_all_files).T.tolist()
                        Mt_user_lifetime_transposed = np.array(Mt_user_lifetime_all_files).T.tolist()
                        dMt_user_lifetime_transposed = np.array(dMt_user_lifetime_all_files).T.tolist()
                        Fs_user_lifetime_transposed = np.array(Fs_user_lifetime_all_files).T.tolist()
                        dFs_user_lifetime_transposed = np.array(dFs_user_lifetime_all_files).T.tolist()
                        dFsdR1_user_lifetime_transposed = np.array(dFsdR1_user_lifetime_all_files).T.tolist()
                        dFsdR2_user_lifetime_transposed = np.array(dFsdR2_user_lifetime_all_files).T.tolist()
                        dFsdeff_user_lifetime_transposed = np.array(dFsdeff_user_lifetime_all_files).T.tolist()
                        kp_user_lifetime_transposed = np.array(kp_user_lifetime_all_files).T.tolist()
                        dkp_user_lifetime_transposed = np.array(dkp_user_lifetime_all_files).T.tolist()
                        keff_user_lifetime_transposed = np.array(keff_user_lifetime_all_files).T.tolist()
                        dkeff_user_lifetime_transposed = np.array(dkeff_user_lifetime_all_files).T.tolist()
                    
                for gate in range(0,len(gatewidth_list)):
                    current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combined/Stat_Plots/', '', current_file, add_current_file=False, make_dirs=True)   
                    
                    current_gatewidth = gatewidth_list[gate]
                    print('Plotting combine_statistical_plots. Gate-width = ',current_gatewidth)
                    
                    current_m1 = m1_transposed[gate]
                    current_m2 = m2_transposed[gate]
                    current_m3 = m3_transposed[gate]
                    current_m4 = m4_transposed[gate]
                    current_C1 = C1_transposed[gate]
                    current_C2 = C2_transposed[gate]
                    current_C3 = C3_transposed[gate]
                    current_C4 = C4_transposed[gate]
                    Y1_data_current_gate = Y1_transposed[gate]
                    dY1_data_current_gate = dY1_transposed[gate]
                    Y1_combined_current_gate = Y1_combined[gate]
                    Y1_combined_sd_current_gate = Y1_combined_sd[gate]
                    Y1_individual_unc_avg_current_gate = Y1_individual_unc_avg[gate]
                    R1_data_current_gate = R1_transposed[gate]
                    dR1_data_current_gate = dR1_transposed[gate]
                    R1_combined_current_gate = R1_combined[gate]
                    R1_combined_sd_current_gate = R1_combined_sd[gate]
                    R1_individual_unc_avg_current_gate = R1_individual_unc_avg[gate]
                    Y2_data_current_gate = Y2_transposed[gate]
                    dY2_data_current_gate = dY2_transposed[gate]
                    Y2_combined_current_gate = Y2_combined[gate]
                    Y2_combined_sd_current_gate = Y2_combined_sd[gate]
                    Y2_individual_unc_avg_current_gate = Y2_individual_unc_avg[gate]
                    Ym_data_current_gate = Ym_transposed[gate]
                    dYm_data_current_gate = dYm_transposed[gate]
                    Ym_combined_current_gate = Ym_combined[gate]
                    Ym_combined_sd_current_gate = Ym_combined_sd[gate]
                    Ym_individual_unc_avg_current_gate = Ym_individual_unc_avg[gate]                   
                    if perform_Y2_single_fit == True:
                        current_omega2_single = omega2_single_results_transposed[gate]
                        R2_single_Y2_decay_data_current_gate = R2_single_Y2_decay_transposed[gate]
                        R2_unc_single_Y2_decay_data_current_gate = R2_unc_single_Y2_decay_transposed[gate]
                        R2_single_Y2_decay_combined_current_gate = R2_single_Y2_decay_combined[gate]
                        if combine_Y2_rate_results_old_method == True:
                            R2_single_Y2_decay_combined_sd_current_gate = R2_single_Y2_decay_combined_sd[gate]
                            R2_single_Y2_decay_individual_unc_avg_current_gate = R2_single_Y2_decay_individual_unc_avg[gate]
                    if perform_Y2_double_fit == True:
                        current_omega2_double1 = omega2_double1_results_transposed[gate]
                        R2_double1_Y2_decay_data_current_gate = R2_double1_Y2_decay_transposed[gate]
                        R2_unc_double1_Y2_decay_data_current_gate = R2_unc_double1_Y2_decay_transposed[gate]
                        R2_double1_Y2_decay_combined_current_gate = R2_double1_Y2_decay_combined[gate]
                        current_omega2_double2 = omega2_double2_results_transposed[gate]
                        R2_double2_Y2_decay_data_current_gate = R2_double2_Y2_decay_transposed[gate]
                        R2_unc_double2_Y2_decay_data_current_gate = R2_unc_double2_Y2_decay_transposed[gate]
                        R2_double2_Y2_decay_combined_current_gate = R2_double2_Y2_decay_combined[gate]
                        R2_double_both_Y2_decay_data_current_gate = R2_double_both_Y2_decay_transposed[gate]
                        R2_unc_double_both_Y2_decay_data_current_gate = R2_unc_double_both_Y2_decay_transposed[gate]
                        R2_double_both_Y2_decay_combined_current_gate = R2_double_both_Y2_decay_combined[gate]
                        if combine_Y2_rate_results_old_method == True:
                            R2_double1_Y2_decay_combined_sd_current_gate = R2_double1_Y2_decay_combined_sd[gate]
                            R2_double1_Y2_decay_individual_unc_avg_current_gate = R2_double1_Y2_decay_individual_unc_avg[gate]    
                            R2_double2_Y2_decay_combined_sd_current_gate = R2_double2_Y2_decay_combined_sd[gate]
                            R2_double2_Y2_decay_individual_unc_avg_current_gate = R2_double2_Y2_decay_individual_unc_avg[gate]
                            R2_double_both_Y2_decay_combined_sd_current_gate = R2_double_both_Y2_decay_combined_sd[gate]
                            R2_double_both_Y2_decay_individual_unc_avg_current_gate = R2_double_both_Y2_decay_individual_unc_avg[gate]
                    if use_user_specified_lifetime == True:
                        current_omega2_lifetime_user = omega2_lifetime_user_results_transposed[gate]
                        R2_user_lifetime_data_current_gate = R2_user_lifetime_transposed[gate]
                        R2_unc_user_lifetime_data_current_gate = R2_unc_user_lifetime_transposed[gate]
                        R2_user_lifetime_combined_current_gate = R2_user_lifetime_combined[gate]
                        if combine_Y2_rate_results_old_method == True:
                            R2_user_lifetime_combined_sd_current_gate = R2_user_lifetime_combined_sd[gate]
                            R2_user_lifetime_individual_unc_avg_current_gate = R2_user_lifetime_individual_unc_avg[gate]
                    if calculation_type == 'Cf':
                        calc_eff_kn_current_gate = calc_eff_kn_transposed[gate]
                        calc_eff_unc_kn_current_gate = calc_eff_kn_transposed[gate]
                        calc_eff_kn_combined_current_gate = calc_eff_kn_combined[gate]
                        calc_eff_kn_combined_sd_current_gate = calc_eff_kn_combined_sd[gate]
                        calc_eff_kn_individual_unc_current_gate = calc_eff_kn_individual_unc_avg[gate]
                    elif calculation_type == 'Multiplicity':
                        if perform_Y2_single_fit == True:
                            Ml_single_data_current_gate = Ml_single_transposed[gate]
                            dMl_single_data_current_gate = dMl_single_transposed[gate]
                            Ml_single_combined_current_gate = Ml_single_combined[gate]
                            Mt_single_data_current_gate = Mt_single_transposed[gate]
                            dMt_single_data_current_gate = dMt_single_transposed[gate]
                            Mt_single_combined_current_gate = Mt_single_combined[gate]
                            Fs_single_data_current_gate = Fs_single_transposed[gate]
                            dFs_single_data_current_gate = dFs_single_transposed[gate]
                            Fs_single_combined_current_gate = Fs_single_combined[gate]
                            kp_single_data_current_gate = kp_single_transposed[gate]
                            dkp_single_data_current_gate = dkp_single_transposed[gate]
                            kp_single_combined_current_gate = kp_single_combined[gate]
                            keff_single_data_current_gate = keff_single_transposed[gate]
                            dkeff_single_data_current_gate = dkeff_single_transposed[gate]
                            keff_single_combined_current_gate = keff_single_combined[gate]
                            if combine_Y2_rate_results_old_method == True:
                                Ml_single_combined_sd_current_gate = Ml_single_combined_sd[gate]
                                Ml_single_individual_unc_avg_current_gate = Ml_single_individual_unc_avg[gate]
                                Mt_single_combined_sd_current_gate = Mt_single_combined_sd[gate]
                                Mt_single_individual_unc_avg_current_gate = Mt_single_individual_unc_avg[gate]
                                Fs_single_combined_sd_current_gate = Fs_single_combined_sd[gate]
                                Fs_single_individual_unc_avg_current_gate = Fs_single_individual_unc_avg[gate]
                                kp_single_combined_sd_current_gate = kp_single_combined_sd[gate]
                                kp_single_individual_unc_avg_current_gate = kp_single_individual_unc_avg[gate]
                                keff_single_combined_sd_current_gate = keff_single_combined_sd[gate]
                                keff_single_individual_unc_avg_current_gate = keff_single_individual_unc_avg[gate]
                        if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                            Ml_double1_data_current_gate = Ml_double1_transposed[gate]
                            dMl_double1_data_current_gate = dMl_double1_transposed[gate]
                            Ml_double1_combined_current_gate = Ml_double1_combined[gate]
                            Mt_double1_data_current_gate = Mt_double1_transposed[gate]
                            dMt_double1_data_current_gate = dMt_double1_transposed[gate]
                            Mt_double1_combined_current_gate = Mt_double1_combined[gate]
                            Fs_double1_data_current_gate = Fs_double1_transposed[gate]
                            dFs_double1_data_current_gate = dFs_double1_transposed[gate]
                            Fs_double1_combined_current_gate = Fs_double1_combined[gate]
                            kp_double1_data_current_gate = kp_double1_transposed[gate]
                            dkp_double1_data_current_gate = dkp_double1_transposed[gate]
                            kp_double1_combined_current_gate = kp_double1_combined[gate]
                            keff_double1_data_current_gate = keff_double1_transposed[gate]
                            dkeff_double1_data_current_gate = dkeff_double1_transposed[gate]
                            keff_double1_combined_current_gate = keff_double1_combined[gate]
                            Ml_double2_data_current_gate = Ml_double2_transposed[gate]
                            dMl_double2_data_current_gate = dMl_double2_transposed[gate]
                            Ml_double2_combined_current_gate = Ml_double2_combined[gate]
                            Mt_double2_data_current_gate = Mt_double2_transposed[gate]
                            dMt_double2_data_current_gate = dMt_double2_transposed[gate]
                            Mt_double2_combined_current_gate = Mt_double2_combined[gate]
                            Fs_double2_data_current_gate = Fs_double2_transposed[gate]
                            dFs_double2_data_current_gate = dFs_double2_transposed[gate]
                            Fs_double2_combined_current_gate = Fs_double2_combined[gate]
                            kp_double2_data_current_gate = kp_double2_transposed[gate]
                            dkp_double2_data_current_gate = dkp_double2_transposed[gate]
                            kp_double2_combined_current_gate = kp_double2_combined[gate]
                            keff_double2_data_current_gate = keff_double2_transposed[gate]
                            dkeff_double2_data_current_gate = dkeff_double2_transposed[gate]
                            keff_double2_combined_current_gate = keff_double2_combined[gate]
                            Ml_double_both_data_current_gate = Ml_double_both_transposed[gate]
                            dMl_double_both_data_current_gate = dMl_double_both_transposed[gate]
                            Ml_double_both_combined_current_gate = Ml_double_both_combined[gate]
                            Mt_double_both_data_current_gate = Mt_double_both_transposed[gate]
                            dMt_double_both_data_current_gate = dMt_double_both_transposed[gate]
                            Mt_double_both_combined_current_gate = Mt_double_both_combined[gate]
                            Fs_double_both_data_current_gate = Fs_double_both_transposed[gate]
                            dFs_double_both_data_current_gate = dFs_double_both_transposed[gate]
                            Fs_double_both_combined_current_gate = Fs_double_both_combined[gate]
                            kp_double_both_data_current_gate = kp_double_both_transposed[gate]
                            dkp_double_both_data_current_gate = dkp_double_both_transposed[gate]
                            kp_double_both_combined_current_gate = kp_double_both_combined[gate]
                            keff_double_both_data_current_gate = keff_double_both_transposed[gate]
                            dkeff_double_both_data_current_gate = dkeff_double_both_transposed[gate]
                            keff_double_both_combined_current_gate = keff_double_both_combined[gate]
                            if combine_Y2_rate_results_old_method == True:
                                Ml_double1_combined_sd_current_gate = Ml_double1_combined_sd[gate]
                                Ml_double1_individual_unc_avg_current_gate = Ml_double1_individual_unc_avg[gate]
                                Mt_double1_combined_sd_current_gate = Mt_double1_combined_sd[gate]
                                Mt_double1_individual_unc_avg_current_gate = Mt_double1_individual_unc_avg[gate]
                                Fs_double1_combined_sd_current_gate = Fs_double1_combined_sd[gate]
                                Fs_double1_individual_unc_avg_current_gate = Fs_double1_individual_unc_avg[gate]
                                kp_double1_combined_sd_current_gate = kp_double1_combined_sd[gate]
                                kp_double1_individual_unc_avg_current_gate = kp_double1_individual_unc_avg[gate]
                                keff_double1_combined_sd_current_gate = keff_double1_combined_sd[gate]
                                keff_double1_individual_unc_avg_current_gate = keff_double1_individual_unc_avg[gate]
                                Ml_double2_combined_sd_current_gate = Ml_double2_combined_sd[gate]
                                Ml_double2_individual_unc_avg_current_gate = Ml_double2_individual_unc_avg[gate]
                                Mt_double2_combined_sd_current_gate = Mt_double2_combined_sd[gate]
                                Mt_double2_individual_unc_avg_current_gate = Mt_double2_individual_unc_avg[gate]
                                Fs_double2_combined_sd_current_gate = Fs_double2_combined_sd[gate]
                                Fs_double2_individual_unc_avg_current_gate = Fs_double2_individual_unc_avg[gate]
                                kp_double2_combined_sd_current_gate = kp_double2_combined_sd[gate]
                                kp_double2_individual_unc_avg_current_gate = kp_double2_individual_unc_avg[gate]
                                keff_double2_combined_sd_current_gate = keff_double2_combined_sd[gate]
                                keff_double2_individual_unc_avg_current_gate = keff_double2_individual_unc_avg[gate]
                                Ml_double_both_combined_sd_current_gate = Ml_double_both_combined_sd[gate]
                                Ml_double_both_individual_unc_avg_current_gate = Ml_double_both_individual_unc_avg[gate]
                                Mt_double_both_combined_sd_current_gate = Mt_double_both_combined_sd[gate]
                                Mt_double_both_individual_unc_avg_current_gate = Mt_double_both_individual_unc_avg[gate]
                                Fs_double_both_combined_sd_current_gate = Fs_double_both_combined_sd[gate]
                                Fs_double_both_individual_unc_avg_current_gate = Fs_double_both_individual_unc_avg[gate]
                                kp_double_both_combined_sd_current_gate = kp_double_both_combined_sd[gate]
                                kp_double_both_individual_unc_avg_current_gate = kp_double_both_individual_unc_avg[gate]
                                keff_double_both_combined_sd_current_gate = keff_double_both_combined_sd[gate]
                                keff_double_both_individual_unc_avg_current_gate = keff_double_both_individual_unc_avg[gate]
                        if use_user_specified_lifetime == True:
                            Ml_user_lifetime_data_current_gate = Ml_user_lifetime_transposed[gate]
                            dMl_user_lifetime_data_current_gate = dMl_user_lifetime_transposed[gate]
                            Ml_user_lifetime_combined_current_gate = Ml_user_lifetime_combined[gate]
                            Mt_user_lifetime_data_current_gate = Mt_user_lifetime_transposed[gate]
                            dMt_user_lifetime_data_current_gate = dMt_user_lifetime_transposed[gate]
                            Mt_user_lifetime_combined_current_gate = Mt_user_lifetime_combined[gate]
                            Fs_user_lifetime_data_current_gate = Fs_user_lifetime_transposed[gate]
                            dFs_user_lifetime_data_current_gate = dFs_user_lifetime_transposed[gate]
                            Fs_user_lifetime_combined_current_gate = Fs_user_lifetime_combined[gate]
                            kp_user_lifetime_data_current_gate = kp_user_lifetime_transposed[gate]
                            dkp_user_lifetime_data_current_gate = dkp_user_lifetime_transposed[gate]
                            kp_user_lifetime_combined_current_gate = kp_user_lifetime_combined[gate]
                            keff_user_lifetime_data_current_gate = keff_user_lifetime_transposed[gate]
                            dkeff_user_lifetime_data_current_gate = dkeff_user_lifetime_transposed[gate]
                            keff_user_lifetime_combined_current_gate = keff_user_lifetime_combined[gate]
                            if combine_Y2_rate_results_old_method == True:
                                Ml_user_lifetime_combined_sd_current_gate = Ml_user_lifetime_combined_sd[gate]
                                Ml_user_lifetime_individual_unc_avg_current_gate = Ml_user_lifetime_individual_unc_avg[gate]
                                Mt_user_lifetime_combined_sd_current_gate = Mt_user_lifetime_combined_sd[gate]
                                Mt_user_lifetime_individual_unc_avg_current_gate = Mt_user_lifetime_individual_unc_avg[gate]
                                Fs_user_lifetime_combined_sd_current_gate = Fs_user_lifetime_combined_sd[gate]
                                Fs_user_lifetime_individual_unc_avg_current_gate = Fs_user_lifetime_individual_unc_avg[gate]
                                kp_user_lifetime_combined_sd_current_gate = kp_user_lifetime_combined_sd[gate]
                                kp_user_lifetime_individual_unc_avg_current_gate = kp_user_lifetime_individual_unc_avg[gate]
                                keff_user_lifetime_combined_sd_current_gate = keff_user_lifetime_combined_sd[gate]
                                keff_user_lifetime_individual_unc_avg_current_gate = keff_user_lifetime_individual_unc_avg[gate]
                
                    if user_gatewidths_plot_all_files_vs_con != True or (user_gatewidths_plot_all_files_vs_con == True and current_gatewidth in plot_all_files_vs_con_gatewidth_list):
                        plotHistogram_vs_gaussian('Y1', current_gatewidth, Y1_data_current_gate, Y1_combined_current_gate, Y1_combined_sd_current_gate, Y1_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth), log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                        plotHistogram_vs_gaussian('R1', current_gatewidth, R1_data_current_gate, R1_combined_current_gate, R1_combined_sd_current_gate, R1_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth), log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                        plotHistogram_vs_gaussian('Y2', current_gatewidth, Y2_data_current_gate, Y2_combined_current_gate, Y2_combined_sd_current_gate, Y2_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth), log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                        plotHistogram_vs_gaussian('Ym', current_gatewidth, Ym_data_current_gate, Ym_combined_current_gate, Ym_combined_sd_current_gate, Ym_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth), log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                        if combine_Y2_rate_results_old_method == True:
                            if perform_Y2_single_fit == True:
                                plotHistogram_vs_gaussian('R2', current_gatewidth, R2_single_Y2_decay_data_current_gate, R2_single_Y2_decay_combined_current_gate, R2_single_Y2_decay_combined_sd_current_gate, R2_single_Y2_decay_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_single_', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                            if perform_Y2_double_fit == True:
                                plotHistogram_vs_gaussian('R2', current_gatewidth, R2_double1_Y2_decay_data_current_gate, R2_double1_Y2_decay_combined_current_gate, R2_double1_Y2_decay_combined_sd_current_gate, R2_double1_Y2_decay_individual_unc_avg_current_gate , show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double1_', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                plotHistogram_vs_gaussian('R2', current_gatewidth, R2_double2_Y2_decay_data_current_gate, R2_double2_Y2_decay_combined_current_gate, R2_double2_Y2_decay_combined_sd_current_gate, R2_double2_Y2_decay_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double2_', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                plotHistogram_vs_gaussian('R2', current_gatewidth, R2_double_both_Y2_decay_data_current_gate, R2_double_both_Y2_decay_combined_current_gate, R2_double_both_Y2_decay_combined_sd_current_gate, R2_double_both_Y2_decay_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double_both_', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                            if use_user_specified_lifetime == True:
                                plotHistogram_vs_gaussian('R2', current_gatewidth, R2_user_lifetime_data_current_gate, R2_user_lifetime_combined_current_gate, R2_user_lifetime_combined_sd_current_gate, R2_user_lifetime_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime_', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                            if calculation_type == 'Cf':
                                plotHistogram_vs_gaussian('Efficiency', current_gatewidth, calc_eff_kn_current_gate, calc_eff_kn_combined_current_gate, calc_eff_kn_combined_sd_current_gate, calc_eff_kn_individual_unc_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth), log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                            elif calculation_type == 'Multiplicity':
                                if perform_Y2_single_fit == True:
                                    plotHistogram_vs_gaussian('Ml', current_gatewidth, Ml_single_data_current_gate, Ml_single_combined_current_gate, Ml_single_combined_sd_current_gate, Ml_single_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_single', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Mt', current_gatewidth, Mt_single_data_current_gate, Mt_single_combined_current_gate, Mt_single_combined_sd_current_gate, Mt_single_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_single', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Fs', current_gatewidth, Fs_single_data_current_gate, Fs_single_combined_current_gate, Fs_single_combined_sd_current_gate, Fs_single_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_single', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('kp', current_gatewidth, kp_single_data_current_gate, kp_single_combined_current_gate, kp_single_combined_sd_current_gate, kp_single_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_single', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('keff', current_gatewidth, keff_single_data_current_gate, keff_single_combined_current_gate, keff_single_combined_sd_current_gate, keff_single_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_single', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                    plotHistogram_vs_gaussian('Ml', current_gatewidth, Ml_double1_data_current_gate, Ml_double1_combined_current_gate, Ml_double1_combined_sd_current_gate, Ml_double1_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double1', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Mt', current_gatewidth, Mt_double1_data_current_gate, Mt_double1_combined_current_gate, Mt_double1_combined_sd_current_gate, Mt_double1_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double1', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Fs', current_gatewidth, Fs_double1_data_current_gate, Fs_double1_combined_current_gate, Fs_double1_combined_sd_current_gate, Fs_double1_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double1', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('kp', current_gatewidth, kp_double1_data_current_gate, kp_double1_combined_current_gate, kp_double1_combined_sd_current_gate, kp_double1_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double1', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('keff', current_gatewidth, keff_double1_data_current_gate, keff_double1_combined_current_gate, keff_double1_combined_sd_current_gate, keff_double1_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double1', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Ml', current_gatewidth, Ml_double2_data_current_gate, Ml_double2_combined_current_gate, Ml_double2_combined_sd_current_gate, Ml_double2_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double2', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Mt', current_gatewidth, Mt_double2_data_current_gate, Mt_double2_combined_current_gate, Mt_double2_combined_sd_current_gate, Mt_double2_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double2', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Fs', current_gatewidth, Fs_double2_data_current_gate, Fs_double2_combined_current_gate, Fs_double2_combined_sd_current_gate, Fs_double2_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double2', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('kp', current_gatewidth, kp_double2_data_current_gate, kp_double2_combined_current_gate, kp_double2_combined_sd_current_gate, kp_double2_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double2', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('keff', current_gatewidth, keff_double2_data_current_gate, keff_double2_combined_current_gate, keff_double2_combined_sd_current_gate, keff_double2_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double2', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Ml', current_gatewidth, Ml_double_both_data_current_gate, Ml_double_both_combined_current_gate, Ml_double_both_combined_sd_current_gate, Ml_double_both_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double_both', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Mt', current_gatewidth, Mt_double_both_data_current_gate, Mt_double_both_combined_current_gate, Mt_double_both_combined_sd_current_gate, Mt_double_both_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double_both', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Fs', current_gatewidth, Fs_double_both_data_current_gate, Fs_double_both_combined_current_gate, Fs_double_both_combined_sd_current_gate, Fs_double_both_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double_both', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('kp', current_gatewidth, kp_double_both_data_current_gate, kp_double_both_combined_current_gate, kp_double_both_combined_sd_current_gate, kp_double_both_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double_both', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('keff', current_gatewidth, keff_double_both_data_current_gate, keff_double_both_combined_current_gate, keff_double_both_combined_sd_current_gate, keff_double_both_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_double_both', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                if use_user_specified_lifetime == True:
                                    plotHistogram_vs_gaussian('Ml', current_gatewidth, Ml_user_lifetime_data_current_gate, Ml_user_lifetime_combined_current_gate, Ml_user_lifetime_combined_sd_current_gate, Ml_user_lifetime_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Mt', current_gatewidth, Mt_user_lifetime_data_current_gate, Mt_user_lifetime_combined_current_gate, Mt_user_lifetime_combined_sd_current_gate, Mt_user_lifetime_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('Fs', current_gatewidth, Fs_user_lifetime_data_current_gate, Fs_user_lifetime_combined_current_gate, Fs_user_lifetime_combined_sd_current_gate, Fs_user_lifetime_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('kp', current_gatewidth, kp_user_lifetime_data_current_gate, kp_user_lifetime_combined_current_gate, kp_user_lifetime_combined_sd_current_gate, kp_user_lifetime_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plotHistogram_vs_gaussian('keff', current_gatewidth, keff_user_lifetime_data_current_gate, keff_user_lifetime_combined_current_gate, keff_user_lifetime_combined_sd_current_gate, keff_user_lifetime_individual_unc_avg_current_gate, show=False, limit_step=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', log=False, title=False, show_gaussian=True, show_avg=True, show_sd=True, show_unc_avg=True)
                        
                        #if plot_all_files_vs_con == True:
                        current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'All_Files/Configurations/', '', current_file, add_current_file=False, make_dirs=True)
                        plot_scatter_with_stats('Configuration', 'm1', file_number, current_m1, np.average(current_m1), np.std(current_m1, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'm2', file_number, current_m2, np.average(current_m2), np.std(current_m2, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'm3', file_number, current_m3, np.average(current_m3), np.std(current_m3, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'm4', file_number, current_m4, np.average(current_m4), np.std(current_m4, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'C1', file_number, current_C1, np.average(current_C1), np.std(current_C1, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'C2', file_number, current_C2, np.average(current_C2), np.std(current_C2, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'C3', file_number, current_C3, np.average(current_C3), np.std(current_C3, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'C4', file_number, current_C4, np.average(current_C4), np.std(current_C4, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'Y1', file_number, Y1_data_current_gate, Y1_combined_current_gate, Y1_combined_sd_current_gate, Y1_individual_unc_avg_current_gate, marker_size, y_unc=dY1_data_current_gate, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                        plot_scatter_with_stats('Configuration', 'dY1', file_number, dY1_data_current_gate, np.average(dY1_data_current_gate), np.std(dY1_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'R1', file_number, R1_data_current_gate, R1_combined_current_gate, R1_combined_sd_current_gate, R1_individual_unc_avg_current_gate, marker_size, y_unc=dR1_data_current_gate, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                        plot_scatter_with_stats('Configuration', 'dR1', file_number, dR1_data_current_gate, np.average(dR1_data_current_gate), np.std(dR1_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'Y2', file_number, Y2_data_current_gate, Y2_combined_current_gate, Y2_combined_sd_current_gate, Y2_individual_unc_avg_current_gate, marker_size, y_unc=dY2_data_current_gate, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                        plot_scatter_with_stats('Configuration', 'dY2', file_number, dY2_data_current_gate, np.average(dY2_data_current_gate), np.std(dY2_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        plot_scatter_with_stats('Configuration', 'Ym', file_number, Ym_data_current_gate, Ym_combined_current_gate, Ym_combined_sd_current_gate, Ym_individual_unc_avg_current_gate, marker_size, y_unc=dYm_data_current_gate, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                        plot_scatter_with_stats('Configuration', 'dYm', file_number, dYm_data_current_gate, np.average(dYm_data_current_gate), np.std(dYm_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                        if combine_Y2_rate_results_old_method == True:
                            if perform_Y2_single_fit == True:
                                plot_scatter_with_stats('Configuration', 'omega2', file_number, current_omega2_single, np.average(current_omega2_single), np.std(current_omega2_single, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_single_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                plot_scatter_with_stats('Configuration', 'R2', file_number, R2_single_Y2_decay_data_current_gate, R2_single_Y2_decay_combined_current_gate, R2_single_Y2_decay_combined_sd_current_gate, R2_single_Y2_decay_individual_unc_avg_current_gate, marker_size, y_unc=R2_unc_single_Y2_decay_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_single_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                plot_scatter_with_stats('Configuration', 'dR2', file_number, R2_unc_single_Y2_decay_data_current_gate, np.average(R2_unc_single_Y2_decay_data_current_gate), np.std(R2_unc_single_Y2_decay_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_single_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                            if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                plot_scatter_with_stats('Configuration', 'omega2', file_number, current_omega2_double1, np.average(current_omega2_double1), np.std(current_omega2_double1, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double1_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                plot_scatter_with_stats('Configuration', 'R2', file_number, R2_double1_Y2_decay_data_current_gate, R2_double1_Y2_decay_combined_current_gate, R2_double1_Y2_decay_combined_sd_current_gate, R2_double1_Y2_decay_individual_unc_avg_current_gate, marker_size, y_unc=R2_unc_double1_Y2_decay_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double1_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                plot_scatter_with_stats('Configuration', 'dR2', file_number, R2_unc_double1_Y2_decay_data_current_gate, np.average(R2_unc_double1_Y2_decay_data_current_gate), np.std(R2_unc_double1_Y2_decay_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double1_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                plot_scatter_with_stats('Configuration', 'omega2', file_number, current_omega2_double2, np.average(current_omega2_double2), np.std(current_omega2_double2, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double2_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                plot_scatter_with_stats('Configuration', 'R2', file_number, R2_double2_Y2_decay_data_current_gate, R2_double2_Y2_decay_combined_current_gate, R2_double2_Y2_decay_combined_sd_current_gate, R2_double2_Y2_decay_individual_unc_avg_current_gate, marker_size, y_unc=R2_unc_double2_Y2_decay_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double2_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                plot_scatter_with_stats('Configuration', 'dR2', file_number, R2_unc_double2_Y2_decay_data_current_gate, np.average(R2_unc_double2_Y2_decay_data_current_gate), np.std(R2_unc_double2_Y2_decay_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double2_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                plot_scatter_with_stats('Configuration', 'R2', file_number, R2_double_both_Y2_decay_data_current_gate, R2_double_both_Y2_decay_combined_current_gate, R2_double_both_Y2_decay_combined_sd_current_gate, R2_double_both_Y2_decay_individual_unc_avg_current_gate, marker_size, y_unc=R2_unc_double_both_Y2_decay_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double_both_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                plot_scatter_with_stats('Configuration', 'dR2', file_number, R2_unc_double_both_Y2_decay_data_current_gate, np.average(R2_unc_double_both_Y2_decay_data_current_gate), np.std(R2_unc_double_both_Y2_decay_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double_both_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                            if use_user_specified_lifetime == True:
                                plot_scatter_with_stats('Configuration', 'omega2', file_number, current_omega2_user_lifetime, np.average(current_omega2_user_lifetime), np.std(current_omega2_user_lifetime, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                plot_scatter_with_stats('Configuration', 'R2', file_number, R2_user_lifetime_data_current_gate, R2_user_lifetime_combined_current_gate, R2_user_lifetime_combined_sd_current_gate, R2_user_lifetime_individual_unc_avg_current_gate, marker_size, y_unc=R2_unc_user_lifetime_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                plot_scatter_with_stats('Configuration', 'dR2', file_number, R2_unc_user_lifetime_data_current_gate, np.average(R2_unc_user_lifetime_data_current_gate), np.std(R2_unc_user_lifetime_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime_', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                            if calculation_type == 'Cf':
                                plot_scatter_with_stats('Configuration', 'Efficiency', file_number, calc_eff_kn_current_gate, calc_eff_kn_combined_current_gate, calc_eff_kn_combined_sd_current_gate, calc_eff_kn_individual_unc_current_gate, marker_size, y_unc=calc_eff_unc_kn_current_gate, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                plot_scatter_with_stats('Configuration', 'dEfficiency', file_number, calc_eff_unc_kn_current_gate, np.average(calc_eff_unc_kn_current_gate), np.std(calc_eff_unc_kn_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth), yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                            elif calculation_type == 'Multiplicity':
                                if perform_Y2_single_fit == True:
                                    plot_scatter_with_stats('Configuration', 'Ml', file_number, Ml_single_data_current_gate, Ml_single_combined_current_gate, Ml_single_combined_sd_current_gate, Ml_single_individual_unc_avg_current_gate, marker_size, y_unc=dMl_single_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMl', file_number, dMl_single_data_current_gate, np.average(dMl_single_data_current_gate), np.std(dMl_single_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Mt', file_number, Mt_single_data_current_gate, Mt_single_combined_current_gate, Mt_single_combined_sd_current_gate, Mt_single_individual_unc_avg_current_gate, marker_size, y_unc=dMt_single_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMt', file_number, dMt_single_data_current_gate, np.average(dMt_single_data_current_gate), np.std(dMt_single_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Fs', file_number, Fs_single_data_current_gate, Fs_single_combined_current_gate, Fs_single_combined_sd_current_gate, Fs_single_individual_unc_avg_current_gate, marker_size, y_unc=dFs_single_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dFs', file_number, dFs_single_data_current_gate, np.average(dFs_single_data_current_gate), np.std(dFs_single_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'kp', file_number, kp_single_data_current_gate, kp_single_combined_current_gate, kp_single_combined_sd_current_gate, kp_single_individual_unc_avg_current_gate, marker_size, y_unc=dkp_single_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkp', file_number, dkp_single_data_current_gate, np.average(dkp_single_data_current_gate), np.std(dkp_single_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'keff', file_number, keff_single_data_current_gate, keff_single_combined_current_gate, keff_single_combined_sd_current_gate, keff_single_individual_unc_avg_current_gate, marker_size, y_unc=dkeff_single_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkeff', file_number, dkeff_single_data_current_gate, np.average(dkeff_single_data_current_gate), np.std(dkeff_single_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_single', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                    plot_scatter_with_stats('Configuration', 'Ml', file_number, Ml_double1_data_current_gate, Ml_double1_combined_current_gate, Ml_double1_combined_sd_current_gate, Ml_double1_individual_unc_avg_current_gate, marker_size, y_unc=dMl_double1_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMl', file_number, dMl_double1_data_current_gate, np.average(dMl_double1_data_current_gate), np.std(dMl_double1_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Mt', file_number, Mt_double1_data_current_gate, Mt_double1_combined_current_gate, Mt_double1_combined_sd_current_gate, Mt_double1_individual_unc_avg_current_gate, marker_size, y_unc=dMt_double1_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMt', file_number, dMt_double1_data_current_gate, np.average(dMt_double1_data_current_gate), np.std(dMt_double1_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Fs', file_number, Fs_double1_data_current_gate, Fs_double1_combined_current_gate, Fs_double1_combined_sd_current_gate, Fs_double1_individual_unc_avg_current_gate, marker_size, y_unc=dFs_double1_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dFs', file_number, dFs_double1_data_current_gate, np.average(dFs_double1_data_current_gate), np.std(dFs_double1_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'kp', file_number, kp_double1_data_current_gate, kp_double1_combined_current_gate, kp_double1_combined_sd_current_gate, kp_double1_individual_unc_avg_current_gate, marker_size, y_unc=dkp_double1_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkp', file_number, dkp_double1_data_current_gate, np.average(dkp_double1_data_current_gate), np.std(dkp_double1_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'keff', file_number, keff_double1_data_current_gate, keff_double1_combined_current_gate, keff_double1_combined_sd_current_gate, keff_double1_individual_unc_avg_current_gate, marker_size, y_unc=dkeff_double1_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkeff', file_number, dkeff_double1_data_current_gate, np.average(dkeff_double1_data_current_gate), np.std(dkeff_double1_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double1', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Ml', file_number, Ml_double2_data_current_gate, Ml_double2_combined_current_gate, Ml_double2_combined_sd_current_gate, Ml_double2_individual_unc_avg_current_gate, marker_size, y_unc=dMl_double2_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMl', file_number, dMl_double2_data_current_gate, np.average(dMl_double2_data_current_gate), np.std(dMl_double2_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Mt', file_number, Mt_double2_data_current_gate, Mt_double2_combined_current_gate, Mt_double2_combined_sd_current_gate, Mt_double2_individual_unc_avg_current_gate, marker_size, y_unc=dMt_double2_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMt', file_number, dMt_double2_data_current_gate, np.average(dMt_double2_data_current_gate), np.std(dMt_double2_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Fs', file_number, Fs_double2_data_current_gate, Fs_double2_combined_current_gate, Fs_double2_combined_sd_current_gate, Fs_double2_individual_unc_avg_current_gate, marker_size, y_unc=dFs_double2_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dFs', file_number, dFs_double2_data_current_gate, np.average(dFs_double2_data_current_gate), np.std(dFs_double2_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'kp', file_number, kp_double2_data_current_gate, kp_double2_combined_current_gate, kp_double2_combined_sd_current_gate, kp_double2_individual_unc_avg_current_gate, marker_size, y_unc=dkp_double2_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkp', file_number, dkp_double2_data_current_gate, np.average(dkp_double2_data_current_gate), np.std(dkp_double2_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'keff', file_number, keff_double2_data_current_gate, keff_double2_combined_current_gate, keff_double2_combined_sd_current_gate, keff_double2_individual_unc_avg_current_gate, marker_size, y_unc=dkeff_double2_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkeff', file_number, dkeff_double2_data_current_gate, np.average(dkeff_double2_data_current_gate), np.std(dkeff_double2_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double2', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Ml', file_number, Ml_double_both_data_current_gate, Ml_double_both_combined_current_gate, Ml_double_both_combined_sd_current_gate, Ml_double_both_individual_unc_avg_current_gate, marker_size, y_unc=dMl_double_both_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMl', file_number, dMl_double_both_data_current_gate, np.average(dMl_double_both_data_current_gate), np.std(dMl_double_both_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Mt', file_number, Mt_double_both_data_current_gate, Mt_double_both_combined_current_gate, Mt_double_both_combined_sd_current_gate, Mt_double_both_individual_unc_avg_current_gate, marker_size, y_unc=dMt_double_both_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMt', file_number, dMt_double_both_data_current_gate, np.average(dMt_double_both_data_current_gate), np.std(dMt_double_both_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Fs', file_number, Fs_double_both_data_current_gate, Fs_double_both_combined_current_gate, Fs_double_both_combined_sd_current_gate, Fs_double_both_individual_unc_avg_current_gate, marker_size, y_unc=dFs_double_both_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dFs', file_number, dFs_double_both_data_current_gate, np.average(dFs_double_both_data_current_gate), np.std(dFs_double_both_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'kp', file_number, kp_double_both_data_current_gate, kp_double_both_combined_current_gate, kp_double_both_combined_sd_current_gate, kp_double_both_individual_unc_avg_current_gate, marker_size, y_unc=dkp_double_both_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkp', file_number, dkp_double_both_data_current_gate, np.average(dkp_double_both_data_current_gate), np.std(dkp_double_both_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'keff', file_number, keff_double_both_data_current_gate, keff_double_both_combined_current_gate, keff_double_both_combined_sd_current_gate, keff_double_both_individual_unc_avg_current_gate, marker_size, y_unc=dkeff_double_both_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkeff', file_number, dkeff_double_both_data_current_gate, np.average(dkeff_double_both_data_current_gate), np.std(dkeff_double_both_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_double_both', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                if use_user_specified_lifetime == True:
                                    plot_scatter_with_stats('Configuration', 'Ml', file_number, Ml_user_lifetime_data_current_gate, Ml_user_lifetime_combined_current_gate, Ml_user_lifetime_combined_sd_current_gate, Ml_user_lifetime_individual_unc_avg_current_gate, marker_size, y_unc=dMl_user_lifetime_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMl', file_number, dMl_user_lifetime_data_current_gate, np.average(dMl_user_lifetime_data_current_gate), np.std(dMl_user_lifetime_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Mt', file_number, Mt_user_lifetime_data_current_gate, Mt_user_lifetime_combined_current_gate, Mt_user_lifetime_combined_sd_current_gate, Mt_user_lifetime_individual_unc_avg_current_gate, marker_size, y_unc=dMt_user_lifetime_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dMt', file_number, dMt_user_lifetime_data_current_gate, np.average(dMt_user_lifetime_data_current_gate), np.std(dMt_user_lifetime_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'Fs', file_number, Fs_user_lifetime_data_current_gate, Fs_user_lifetime_combined_current_gate, Fs_user_lifetime_combined_sd_current_gate, Fs_user_lifetime_individual_unc_avg_current_gate, marker_size, y_unc=dFs_user_lifetime_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dFs', file_number, dFs_user_lifetime_data_current_gate, np.average(dFs_user_lifetime_data_current_gate), np.std(dFs_user_lifetime_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'kp', file_number, kp_user_lifetime_data_current_gate, kp_user_lifetime_combined_current_gate, kp_user_lifetime_combined_sd_current_gate, kp_user_lifetime_individual_unc_avg_current_gate, marker_size, y_unc=dkp_user_lifetime_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkp', file_number, dkp_user_lifetime_data_current_gate, np.average(dkp_user_lifetime_data_current_gate), np.std(dkp_user_lifetime_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                                    plot_scatter_with_stats('Configuration', 'keff', file_number, keff_user_lifetime_data_current_gate, keff_user_lifetime_combined_current_gate, keff_user_lifetime_combined_sd_current_gate, keff_user_lifetime_individual_unc_avg_current_gate, marker_size, y_unc=dkeff_user_lifetime_data_current_gate, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=True)
                                    plot_scatter_with_stats('Configuration', 'dkeff', file_number, dkeff_user_lifetime_data_current_gate, np.average(dkeff_user_lifetime_data_current_gate), np.std(dkeff_user_lifetime_data_current_gate, ddof=1), 0, marker_size, y_unc=None, show=False, save=current_save_path+str(current_gatewidth)+'_user_lifetime', yaxis_log=yaxis_log, show_avg=True, show_sd=True, show_unc_avg=False)
                    
                print('End combine Y2 rate results: combine_statistical_plots')
                print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
                
                if include_stats_rates == True:
                    
                    print('Combine Y2 rate results: combine statistical percent plots')
                    print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
                    
                    plot_scatter_stat_percent('micro-sec', 'm1', gatewidth_list, m1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'm2', gatewidth_list, m2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'm3', gatewidth_list, m3_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'm4', gatewidth_list, m4_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'C1', gatewidth_list, C1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'C2', gatewidth_list, C2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'C3', gatewidth_list, C3_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'C4', gatewidth_list, C4_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'Y1', gatewidth_list, Y1_transposed, Y1_combined, Y1_combined_sd, Y1_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=True)
                    plot_scatter_stat_percent('micro-sec', 'dY1', gatewidth_list, dY1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'R1', gatewidth_list, R1_transposed, R1_combined, R1_combined_sd, R1_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=True)
                    plot_scatter_stat_percent('micro-sec', 'dR1', gatewidth_list, dR1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'Y2', gatewidth_list, Y2_transposed, Y2_combined, Y2_combined_sd, Y2_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=True)
                    plot_scatter_stat_percent('micro-sec', 'dY2', gatewidth_list, dY2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    plot_scatter_stat_percent('micro-sec', 'Ym', gatewidth_list, Ym_transposed, Ym_combined, Ym_combined_sd, Ym_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=True)
                    plot_scatter_stat_percent('micro-sec', 'dYm', gatewidth_list, dYm_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                    if combine_Y2_rate_results_old_method == True:
                        if perform_Y2_single_fit == True:
                            plot_scatter_stat_percent('micro-sec', 'omega2', gatewidth_list, omega2_single_results_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_single_', yaxis_log=yaxis_log, show_unc=False)
                            plot_scatter_stat_percent('micro-sec', 'R2', gatewidth_list, R2_single_Y2_decay_transposed, R2_single_Y2_decay_combined, R2_single_Y2_decay_combined_sd, R2_single_Y2_decay_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_single_', yaxis_log=yaxis_log, show_unc=True)
                            plot_scatter_stat_percent('micro-sec', 'dR2', gatewidth_list, R2_unc_single_Y2_decay_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_single_', yaxis_log=yaxis_log, show_unc=False)
                        if perform_Y2_double_fit == True:
                            plot_scatter_stat_percent('micro-sec', 'omega2', gatewidth_list, omega2_double1_results_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double1_', yaxis_log=yaxis_log, show_unc=False)
                            plot_scatter_stat_percent('micro-sec', 'R2', gatewidth_list, R2_double1_Y2_decay_transposed, R2_double1_Y2_decay_combined, R2_double1_Y2_decay_combined_sd, R2_double1_Y2_decay_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double1_', yaxis_log=yaxis_log, show_unc=True)
                            plot_scatter_stat_percent('micro-sec', 'dR2', gatewidth_list, R2_unc_double1_Y2_decay_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double1_', yaxis_log=yaxis_log, show_unc=False)
                            plot_scatter_stat_percent('micro-sec', 'omega2', gatewidth_list, omega2_double2_results_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double2_', yaxis_log=yaxis_log, show_unc=False)
                            plot_scatter_stat_percent('micro-sec', 'R2', gatewidth_list, R2_double2_Y2_decay_transposed, R2_double2_Y2_decay_combined, R2_double2_Y2_decay_combined_sd, R2_double2_Y2_decay_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double2_', yaxis_log=yaxis_log, show_unc=True)
                            plot_scatter_stat_percent('micro-sec', 'dR2', gatewidth_list, R2_unc_double2_Y2_decay_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double2_', yaxis_log=yaxis_log, show_unc=False)
                            plot_scatter_stat_percent('micro-sec', 'R2', gatewidth_list, R2_double_both_Y2_decay_transposed, R2_double_both_Y2_decay_combined, R2_double_both_Y2_decay_combined_sd, R2_double_both_Y2_decay_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both_', yaxis_log=yaxis_log, show_unc=True)
                            plot_scatter_stat_percent('micro-sec', 'dR2', gatewidth_list, R2_unc_double_both_Y2_decay_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both_', yaxis_log=yaxis_log, show_unc=False)
                        if use_user_specified_lifetime == True:
                            plot_scatter_stat_percent('micro-sec', 'omega2', gatewidth_list, omega2_lifetime_user_results_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=False)
                            plot_scatter_stat_percent('micro-sec', 'R2', gatewidth_list, R2_user_lifetime_transposed, R2_user_lifetime_combined, R2_user_lifetime_combined_sd, R2_user_lifetime_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=True)
                            plot_scatter_stat_percent('micro-sec', 'dR2', gatewidth_list, R2_unc_user_lifetime_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=False)
                        if calculation_type == 'Cf':
                            plot_scatter_stat_percent('micro-sec', 'Efficiency', gatewidth_list, calc_eff_kn_transposed, calc_eff_kn_combined, calc_eff_kn_combined_sd, calc_eff_kn_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=True)
                            plot_scatter_stat_percent('micro-sec', 'dEfficiency', gatewidth_list, calc_eff_unc_kn_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path, yaxis_log=yaxis_log, show_unc=False)
                        elif calculation_type == 'Multiplicity':
                                if perform_Y2_single_fit == True:
                                    plot_scatter_stat_percent('micro-sec', 'Ml', gatewidth_list, Ml_single_transposed, Ml_single_combined, Ml_single_combined_sd, Ml_single_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMl', gatewidth_list, dMl_single_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Mt', gatewidth_list, Mt_single_transposed, Mt_single_combined, Mt_single_combined_sd, Mt_single_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMt', gatewidth_list, dMt_single_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Fs', gatewidth_list, Fs_single_transposed, Fs_single_combined, Fs_single_combined_sd, Fs_single_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dFs', gatewidth_list, dFs_single_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'kp', gatewidth_list, kp_single_transposed, kp_single_combined, kp_single_combined_sd, kp_single_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkp', gatewidth_list, dkp_single_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'keff', gatewidth_list, keff_single_transposed, keff_single_combined, keff_single_combined_sd, keff_single_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkeff', gatewidth_list, dkeff_single_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_single', yaxis_log=yaxis_log, show_unc=False)
                                if perform_Y2_double_fit == True and perform_Y2_double_fit_continue == True:
                                    plot_scatter_stat_percent('micro-sec', 'Ml', gatewidth_list, Ml_double1_transposed, Ml_double1_combined, Ml_double1_combined_sd, Ml_double1_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMl', gatewidth_list, dMl_double1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Mt', gatewidth_list, Mt_double1_transposed, Mt_double1_combined, Mt_double1_combined_sd, Mt_double1_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMt', gatewidth_list, dMt_double1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Fs', gatewidth_list, Fs_double1_transposed, Fs_double1_combined, Fs_double1_combined_sd, Fs_double1_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dFs', gatewidth_list, dFs_double1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'kp', gatewidth_list, kp_double1_transposed, kp_double1_combined, kp_double1_combined_sd, kp_double1_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkp', gatewidth_list, dkp_double1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'keff', gatewidth_list, keff_double1_transposed, keff_double1_combined, keff_double1_combined_sd, keff_double1_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkeff', gatewidth_list, dkeff_double1_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double1', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Ml', gatewidth_list, Ml_double2_transposed, Ml_double2_combined, Ml_double2_combined_sd, Ml_double2_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMl', gatewidth_list, dMl_double2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Mt', gatewidth_list, Mt_double2_transposed, Mt_double2_combined, Mt_double2_combined_sd, Mt_double2_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMt', gatewidth_list, dMt_double2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Fs', gatewidth_list, Fs_double2_transposed, Fs_double2_combined, Fs_double2_combined_sd, Fs_double2_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dFs', gatewidth_list, dFs_double2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'kp', gatewidth_list, kp_double2_transposed, kp_double2_combined, kp_double2_combined_sd, kp_double2_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkp', gatewidth_list, dkp_double2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'keff', gatewidth_list, keff_double2_transposed, keff_double2_combined, keff_double2_combined_sd, keff_double2_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkeff', gatewidth_list, dkeff_double2_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double2', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Ml', gatewidth_list, Ml_double_both_transposed, Ml_double_both_combined, Ml_double_both_combined_sd, Ml_double_both_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMl', gatewidth_list, dMl_double_both_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Mt', gatewidth_list, Mt_double_both_transposed, Mt_double_both_combined, Mt_double_both_combined_sd, Mt_double_both_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMt', gatewidth_list, dMt_double_both_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Fs', gatewidth_list, Fs_double_both_transposed, Fs_double_both_combined, Fs_double_both_combined_sd, Fs_double_both_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dFs', gatewidth_list, dFs_double_both_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'kp', gatewidth_list, kp_double_both_transposed, kp_double_both_combined, kp_double_both_combined_sd, kp_double_both_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkp', gatewidth_list, dkp_double_both_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'keff', gatewidth_list, keff_double_both_transposed, keff_double_both_combined, keff_double_both_combined_sd, keff_double_both_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkeff', gatewidth_list, dkeff_double_both_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_double_both', yaxis_log=yaxis_log, show_unc=False)
                                if use_user_specified_lifetime == True:
                                    plot_scatter_stat_percent('micro-sec', 'Ml', gatewidth_list, Ml_user_lifetime_transposed, Ml_user_lifetime_combined, Ml_user_lifetime_combined_sd, Ml_user_lifetime_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMl', gatewidth_list, dMl_user_lifetime_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Mt', gatewidth_list, Mt_user_lifetime_transposed, Mt_user_lifetime_combined, Mt_user_lifetime_combined_sd, Mt_user_lifetime_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dMt', gatewidth_list, dMt_user_lifetime_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'Fs', gatewidth_list, Fs_user_lifetime_transposed, Fs_user_lifetime_combined, Fs_user_lifetime_combined_sd, Fs_user_lifetime_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dFs', gatewidth_list, dFs_user_lifetime_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'kp', gatewidth_list, kp_user_lifetime_transposed, kp_user_lifetime_combined, kp_user_lifetime_combined_sd, kp_user_lifetime_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkp', gatewidth_list, dkp_user_lifetime_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=False)
                                    plot_scatter_stat_percent('micro-sec', 'keff', gatewidth_list, keff_user_lifetime_transposed, keff_user_lifetime_combined, keff_user_lifetime_combined_sd, keff_user_lifetime_individual_unc_avg, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=True)
                                    plot_scatter_stat_percent('micro-sec', 'dkeff', gatewidth_list, dkeff_user_lifetime_transposed, 0, 0, 0, marker_size, x_div=1000, show=False, save=current_save_path+'_user_lifetime', yaxis_log=yaxis_log, show_unc=False)
                        
                    print('End combine Y2 rate results: combine statistical percent plots')
                    print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
            
            print('End combine Y2 rate results')
            print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

# compares combine_Y2_rate_results and summed Feynman histogram
if compare_combine_Y2_rate_results_and_Feynman_sum == True:
    
    print('Compare combine_Y2_rate_results and summed Feynman histogram')
    print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
    
    current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combine_Sum_Compare/Rates/', '', '', add_current_file=False, make_dirs=True)
    
    # Now this .py file and the script below need to be updated, then Multiplicity can be added in
    gatewidth_pass, gatewidth_compare, Y1_pass, Y1_compare, Y1_difference, dY1_pass, dY1_compare, dY1_difference, R1_pass, R1_compare, R1_difference, dR1_pass, dR1_compare, dR1_difference, Y2_pass, Y2_compare, Y2_difference, dY2_pass, dY2_compare, dY2_difference, Ym_pass, Ym_compare, Ym_difference, dYm_pass, dYm_compare, dYm_difference, R2_single_Y2_pass, R2_single_Y2_compare, R2_single_Y2_difference, dR2_single_Y2_pass, dR2_single_Y2_compare, dR2_single_Y2_difference, R2_double1_Y2_pass, R2_double1_Y2_compare, R2_double1_Y2_difference, dR2_double1_Y2_pass, dR2_double1_Y2_compare, dR2_double1_Y2_difference, R2_double2_Y2_pass, R2_double2_Y2_compare, R2_double2_Y2_difference, dR2_double2_Y2_pass, dR2_double2_Y2_compare, dR2_double2_Y2_difference,R2_double_both_Y2_pass, R2_double_both_Y2_compare, R2_double_both_Y2_difference, dR2_double_both_Y2_pass, dR2_double_both_Y2_compare, dR2_double_both_Y2_difference,R2_user_lifetime_Y2_pass, R2_user_lifetime_Y2_compare, R2_user_lifetime_Y2_difference, dR2_user_lifetime_Y2_pass, dR2_user_lifetime_Y2_compare, dR2_user_lifetime_Y2_difference, calc_eff_kn_pass, calc_eff_kn_compare, calc_eff_kn_difference, calc_eff_unc_kn_pass, calc_eff_unc_kn_compare, calc_eff_unc_kn_difference, Ml_Y2single_pass, Ml_Y2single_compare, Ml_Y2single_difference, dMl_Y2single_pass, dMl_Y2single_compare, dMl_Y2single_difference, Mt_Y2single_pass, Mt_Y2single_compare, Mt_Y2single_difference, dMt_Y2single_pass, dMt_Y2single_compare, dMt_Y2single_difference, Fs_Y2single_pass, Fs_Y2single_compare, Fs_Y2single_difference, dFs_Y2single_pass, dFs_Y2single_compare, dFs_Y2single_difference, kp_Y2single_pass, kp_Y2single_compare, kp_Y2single_difference, dkp_Y2single_pass, dkp_Y2single_compare, dkp_Y2single_difference, keff_Y2single_pass, keff_Y2single_compare, keff_Y2single_difference, dkeff_Y2single_pass, dkeff_Y2single_compare, dkeff_Y2single_difference, Ml_Y2double1_pass, Ml_Y2double1_compare, Ml_Y2double1_difference, dMl_Y2double1_pass, dMl_Y2double1_compare, dMl_Y2double1_difference, Mt_Y2double1_pass, Mt_Y2double1_compare, Mt_Y2double1_difference, dMt_Y2double1_pass, dMt_Y2double1_compare, dMt_Y2double1_difference, Fs_Y2double1_pass, Fs_Y2double1_compare, Fs_Y2double1_difference, dFs_Y2double1_pass, dFs_Y2double1_compare, dFs_Y2double1_difference, kp_Y2double1_pass, kp_Y2double1_compare, kp_Y2double1_difference, dkp_Y2double1_pass, dkp_Y2double1_compare, dkp_Y2double1_difference, keff_Y2double1_pass, keff_Y2double1_compare, keff_Y2double1_difference, dkeff_Y2double1_pass, dkeff_Y2double1_compare, dkeff_Y2double1_difference, Ml_Y2double2_pass, Ml_Y2double2_compare, Ml_Y2double2_difference, dMl_Y2double2_pass, dMl_Y2double2_compare, dMl_Y2double2_difference, Mt_Y2double2_pass, Mt_Y2double2_compare, Mt_Y2double2_difference, dMt_Y2double2_pass, dMt_Y2double2_compare, dMt_Y2double2_difference, Fs_Y2double2_pass, Fs_Y2double2_compare, Fs_Y2double2_difference, dFs_Y2double2_pass, dFs_Y2double2_compare, dFs_Y2double2_difference, kp_Y2double2_pass, kp_Y2double2_compare, kp_Y2double2_difference, dkp_Y2double2_pass, dkp_Y2double2_compare, dkp_Y2double2_difference, keff_Y2double2_pass, keff_Y2double2_compare, keff_Y2double2_difference, dkeff_Y2double2_pass, dkeff_Y2double2_compare, dkeff_Y2double2_difference, Ml_Y2double_both_pass, Ml_Y2double_both_compare, Ml_Y2double_both_difference, dMl_Y2double_both_pass, dMl_Y2double_both_compare, dMl_Y2double_both_difference, Mt_Y2double_both_pass, Mt_Y2double_both_compare, Mt_Y2double_both_difference, dMt_Y2double_both_pass, dMt_Y2double_both_compare, dMt_Y2double_both_difference, Fs_Y2double_both_pass, Fs_Y2double_both_compare, Fs_Y2double_both_difference, dFs_Y2double_both_pass, dFs_Y2double_both_compare, dFs_Y2double_both_difference, kp_Y2double_both_pass, kp_Y2double_both_compare, kp_Y2double_both_difference, dkp_Y2double_both_pass, dkp_Y2double_both_compare, dkp_Y2double_both_difference, keff_Y2double_both_pass, keff_Y2double_both_compare, keff_Y2double_both_difference, dkeff_Y2double_both_pass, dkeff_Y2double_both_compare, dkeff_Y2double_both_difference, Ml_Y2user_lifetime_pass, Ml_Y2user_lifetime_compare, Ml_Y2user_lifetime_difference, dMl_Y2user_lifetime_pass, dMl_Y2user_lifetime_compare, dMl_Y2user_lifetime_difference, Mt_Y2user_lifetime_pass, Mt_Y2user_lifetime_compare, Mt_Y2user_lifetime_difference, dMt_Y2user_lifetime_pass, dMt_Y2user_lifetime_compare, dMt_Y2user_lifetime_difference, Fs_Y2user_lifetime_pass, Fs_Y2user_lifetime_compare, Fs_Y2user_lifetime_difference, dFs_Y2user_lifetime_pass, dFs_Y2user_lifetime_compare, dFs_Y2user_lifetime_difference, kp_Y2user_lifetime_pass, kp_Y2user_lifetime_compare, kp_Y2user_lifetime_difference, dkp_Y2user_lifetime_pass, dkp_Y2user_lifetime_compare, dkp_Y2user_lifetime_difference, keff_Y2user_lifetime_pass, keff_Y2user_lifetime_compare, keff_Y2user_lifetime_difference, dkeff_Y2user_lifetime_pass, dkeff_Y2user_lifetime_compare, dkeff_Y2user_lifetime_difference = compare_combine_sum(combine_Y2_rate_results_filepath, sum_histogram_filepath,current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime)
    
    file_descriptions = ('Combined','Feynman Histogram Sum')
    if gatewidth_pass == True and Y1_pass == True and dY1_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Y1', 'micro-sec', gatewidth_compare, Y1_compare, marker_size, plot_titles, '', y_unc=dY1_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dY1', 'micro-sec', gatewidth_compare, dY1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Y1 % difference', 'micro-sec', gatewidth_compare[0], Y1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dY1 % difference', 'micro-sec', gatewidth_compare[0], dY1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R1_pass == True and dR1_pass == True:
        plot_scatter_gatewidth(file_descriptions, 'R1', 'micro-sec', gatewidth_compare, R1_compare, marker_size, plot_titles, '', y_unc=dR1_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions, 'dR1', 'micro-sec', gatewidth_compare, dR1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'R1 % difference', 'micro-sec', gatewidth_compare[0], R1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dR1 % difference', 'micro-sec', gatewidth_compare[0], dR1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Y2_pass == True and dY2_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Y2', 'micro-sec', gatewidth_compare, Y2_compare, marker_size, plot_titles, '', y_unc=dY2_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dY2', 'micro-sec', gatewidth_compare, dY2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Y2 % difference', 'micro-sec', gatewidth_compare[0], Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dY2 % difference', 'micro-sec', gatewidth_compare[0], dY2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ym_pass == True and dYm_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Ym', 'micro-sec', gatewidth_compare, Ym_compare, marker_size, plot_titles, '', y_unc=dYm_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dYm', 'micro-sec', gatewidth_compare, dYm_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Ym % difference', 'micro-sec', gatewidth_compare[0], Ym_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dYm % difference', 'micro-sec', gatewidth_compare[0], dYm_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_single_Y2_pass == True and dR2_single_Y2_pass == True:
        plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_compare, R2_single_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_single_Y2_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_compare, dR2_single_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'R2 % difference', 'micro-sec', gatewidth_compare[0], R2_single_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dR2 % difference', 'micro-sec', gatewidth_compare[0], dR2_single_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_double1_Y2_pass == True and dR2_double1_Y2_pass == True:
        plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_compare, R2_double1_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_double1_Y2_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_compare, dR2_double1_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'R2 % difference', 'micro-sec', gatewidth_compare[0], R2_double1_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dR2 % difference', 'micro-sec', gatewidth_compare[0], dR2_double1_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_double2_Y2_pass == True and dR2_double2_Y2_pass == True:
        plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_compare, R2_double2_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_double2_Y2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_compare, dR2_double2_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'R2 % difference', 'micro-sec', gatewidth_compare[0], R2_double2_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dR2 % difference', 'micro-sec', gatewidth_compare[0], dR2_double2_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_double_both_Y2_pass == True and dR2_double_both_Y2_pass == True:
        plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_compare, R2_double_both_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_double_both_Y2_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_compare, dR2_double_both_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'R2 % difference', 'micro-sec', gatewidth_compare[0], R2_double_both_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dR2 % difference', 'micro-sec', gatewidth_compare[0], dR2_double_both_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_user_lifetime_Y2_pass == True and dR2_user_lifetime_Y2_pass == True:
        plot_scatter_gatewidth(file_descriptions, 'R2', 'micro-sec', gatewidth_compare, R2_user_lifetime_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_user_lifetime_Y2_compare, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions, 'dR2', 'micro-sec', gatewidth_compare, dR2_user_lifetime_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'R2 % difference', 'micro-sec', gatewidth_compare[0], R2_user_lifetime_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dR2 % difference', 'micro-sec', gatewidth_compare[0], dR2_user_lifetime_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and calc_eff_kn_pass == True and calc_eff_unc_kn_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Efficiency', 'micro-sec', gatewidth_compare, calc_eff_kn_compare, marker_size, plot_titles, '', y_unc=calc_eff_unc_kn_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dEfficiency', 'micro-sec', gatewidth_compare, calc_eff_unc_kn_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Efficiency % difference', 'micro-sec', gatewidth_compare[0], calc_eff_kn_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dEfficiency % difference', 'micro-sec', gatewidth_compare[0], calc_eff_unc_kn_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2single_pass == True and dMl_Y2single_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2single_compare, marker_size, plot_titles, '', y_unc=dMl_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Ml % difference', 'micro-sec', gatewidth_compare[0], Ml_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl % difference', 'micro-sec', gatewidth_compare[0], dMl_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2single_pass == True and dMt_Y2single_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2single_compare, marker_size, plot_titles, '', y_unc=dMt_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Mt % difference', 'micro-sec', gatewidth_compare[0], Mt_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt % difference', 'micro-sec', gatewidth_compare[0], dMt_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2single_pass == True and dFs_Y2single_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2single_compare, marker_size, plot_titles, '', y_unc=dFs_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Fs % difference', 'micro-sec', gatewidth_compare[0], Fs_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs % difference', 'micro-sec', gatewidth_compare[0], dFs_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2single_pass == True and dkp_Y2single_pass == True:
        plot_scatter_gatewidth(file_descriptions,'kp', 'micro-sec', gatewidth_compare, kp_Y2single_compare, marker_size, plot_titles, '', y_unc=dkp_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'kp % difference', 'micro-sec', gatewidth_compare[0], kp_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp % difference', 'micro-sec', gatewidth_compare[0], dkp_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2single_pass == True and dkeff_Y2single_pass == True:
        plot_scatter_gatewidth(file_descriptions,'keff', 'micro-sec', gatewidth_compare, keff_Y2single_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'keff % difference', 'micro-sec', gatewidth_compare[0], keff_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff % difference', 'micro-sec', gatewidth_compare[0], dkeff_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2double1_pass == True and dMl_Y2double1_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2double1_compare, marker_size, plot_titles, '', y_unc=dMl_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Ml % difference', 'micro-sec', gatewidth_compare[0], Ml_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl % difference', 'micro-sec', gatewidth_compare[0], dMl_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2double1_pass == True and dMt_Y2double1_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2double1_compare, marker_size, plot_titles, '', y_unc=dMt_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Mt % difference', 'micro-sec', gatewidth_compare[0], Mt_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt % difference', 'micro-sec', gatewidth_compare[0], dMt_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2double1_pass == True and dFs_Y2double1_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2double1_compare, marker_size, plot_titles, '', y_unc=dFs_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Fs % difference', 'micro-sec', gatewidth_compare[0], Fs_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs % difference', 'micro-sec', gatewidth_compare[0], dFs_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2double1_pass == True and dkp_Y2double1_pass == True:
        plot_scatter_gatewidth(file_descriptions,'kp', 'micro-sec', gatewidth_compare, kp_Y2double1_compare, marker_size, plot_titles, '', y_unc=dkp_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'kp % difference', 'micro-sec', gatewidth_compare[0], kp_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp % difference', 'micro-sec', gatewidth_compare[0], dkp_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2double1_pass == True and dkeff_Y2double1_pass == True:
        plot_scatter_gatewidth(file_descriptions,'keff', 'micro-sec', gatewidth_compare, keff_Y2double1_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'keff % difference', 'micro-sec', gatewidth_compare[0], keff_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff % difference', 'micro-sec', gatewidth_compare[0], dkeff_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2double2_pass == True and dMl_Y2double2_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2double2_compare, marker_size, plot_titles, '', y_unc=dMl_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Ml % difference', 'micro-sec', gatewidth_compare[0], Ml_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl % difference', 'micro-sec', gatewidth_compare[0], dMl_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2double2_pass == True and dMt_Y2double2_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2double2_compare, marker_size, plot_titles, '', y_unc=dMt_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Mt % difference', 'micro-sec', gatewidth_compare[0], Mt_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt % difference', 'micro-sec', gatewidth_compare[0], dMt_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2double2_pass == True and dFs_Y2double2_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2double2_compare, marker_size, plot_titles, '', y_unc=dFs_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Fs % difference', 'micro-sec', gatewidth_compare[0], Fs_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs % difference', 'micro-sec', gatewidth_compare[0], dFs_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2double2_pass == True and dkp_Y2double2_pass == True:
        plot_scatter_gatewidth(file_descriptions,'kp', 'micro-sec', gatewidth_compare, kp_Y2double2_compare, marker_size, plot_titles, '', y_unc=dkp_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'kp % difference', 'micro-sec', gatewidth_compare[0], kp_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp % difference', 'micro-sec', gatewidth_compare[0], dkp_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2double2_pass == True and dkeff_Y2double2_pass == True:
        plot_scatter_gatewidth(file_descriptions,'keff', 'micro-sec', gatewidth_compare, keff_Y2double2_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'keff % difference', 'micro-sec', gatewidth_compare[0], keff_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff % difference', 'micro-sec', gatewidth_compare[0], dkeff_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2double_both_pass == True and dMl_Y2double_both_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dMl_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Ml % difference', 'micro-sec', gatewidth_compare[0], Ml_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMl % difference', 'micro-sec', gatewidth_compare[0], dMl_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2double_both_pass == True and dMt_Y2double_both_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dMt_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Mt % difference', 'micro-sec', gatewidth_compare[0], Mt_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dMt % difference', 'micro-sec', gatewidth_compare[0], dMt_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2double_both_pass == True and dFs_Y2double_both_pass == True:
        plot_scatter_gatewidth(file_descriptions,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dFs_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'Fs % difference', 'micro-sec', gatewidth_compare[0], Fs_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dFs % difference', 'micro-sec', gatewidth_compare[0], dFs_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2double_both_pass == True and dkp_Y2double_both_pass == True:
        plot_scatter_gatewidth(file_descriptions,'kp', 'micro-sec', gatewidth_compare, kp_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dkp_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'kp % difference', 'micro-sec', gatewidth_compare[0], kp_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkp % difference', 'micro-sec', gatewidth_compare[0], dkp_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2double_both_pass == True and dkeff_Y2double_both_pass == True:
        plot_scatter_gatewidth(file_descriptions,'keff', 'micro-sec', gatewidth_compare, keff_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'keff % difference', 'micro-sec', gatewidth_compare[0], keff_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions,'dkeff % difference', 'micro-sec', gatewidth_compare[0], dkeff_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=False, yaxis_log=yaxis_log)
    
    print('End combine_Y2_rate_results and summed Feynman histogram')
    print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
    
# compares combine_Y2_rate_results and summed Feynman histogram
if compare_individual_file_and_combine_Y2_rate_results_and_Feynman_sum == True:
    
    print('Compare individual files, combine_Y2_rate_results, and summed Feynman histogram')
    print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))
    
    current_save_path = output_subdirectory_paths(output_nested_subdirectories, save_path, 'Combine_Individual_Sum_Compare/Rates/', '', '', add_current_file=False, make_dirs=True)
    
    gatewidth_pass, gatewidth_compare, Y1_pass, Y1_compare, Y1_difference, dY1_pass, dY1_compare, dY1_difference, R1_pass, R1_compare, R1_difference, dR1_pass, dR1_compare, dR1_difference, Y2_pass, Y2_compare, Y2_difference, dY2_pass, dY2_compare, dY2_difference, Ym_pass, Ym_compare, Ym_difference, dYm_pass, dYm_compare, dYm_difference, R2_single_Y2_pass, R2_single_Y2_compare, R2_single_Y2_difference, dR2_single_Y2_pass, dR2_single_Y2_compare, dR2_single_Y2_difference, R2_double1_Y2_pass, R2_double1_Y2_compare, R2_double1_Y2_difference, dR2_double1_Y2_pass, dR2_double1_Y2_compare, dR2_double1_Y2_difference, R2_double2_Y2_pass, R2_double2_Y2_compare, R2_double2_Y2_difference, dR2_double2_Y2_pass, dR2_double2_Y2_compare, dR2_double2_Y2_difference,R2_double_both_Y2_pass, R2_double_both_Y2_compare, R2_double_both_Y2_difference, dR2_double_both_Y2_pass, dR2_double_both_Y2_compare, dR2_double_both_Y2_difference,R2_user_lifetime_Y2_pass, R2_user_lifetime_Y2_compare, R2_user_lifetime_Y2_difference, dR2_user_lifetime_Y2_pass, dR2_user_lifetime_Y2_compare, dR2_user_lifetime_Y2_difference, calc_eff_kn_pass, calc_eff_kn_compare, calc_eff_kn_difference, calc_eff_unc_kn_pass, calc_eff_unc_kn_compare, calc_eff_unc_kn_difference, Ml_Y2single_pass, Ml_Y2single_compare, Ml_Y2single_difference, dMl_Y2single_pass, dMl_Y2single_compare, dMl_Y2single_difference, Mt_Y2single_pass, Mt_Y2single_compare, Mt_Y2single_difference, dMt_Y2single_pass, dMt_Y2single_compare, dMt_Y2single_difference, Fs_Y2single_pass, Fs_Y2single_compare, Fs_Y2single_difference, dFs_Y2single_pass, dFs_Y2single_compare, dFs_Y2single_difference, kp_Y2single_pass, kp_Y2single_compare, kp_Y2single_difference, dkp_Y2single_pass, dkp_Y2single_compare, dkp_Y2single_difference, keff_Y2single_pass, keff_Y2single_compare, keff_Y2single_difference, dkeff_Y2single_pass, dkeff_Y2single_compare, dkeff_Y2single_difference, Ml_Y2double1_pass, Ml_Y2double1_compare, Ml_Y2double1_difference, dMl_Y2double1_pass, dMl_Y2double1_compare, dMl_Y2double1_difference, Mt_Y2double1_pass, Mt_Y2double1_compare, Mt_Y2double1_difference, dMt_Y2double1_pass, dMt_Y2double1_compare, dMt_Y2double1_difference, Fs_Y2double1_pass, Fs_Y2double1_compare, Fs_Y2double1_difference, dFs_Y2double1_pass, dFs_Y2double1_compare, dFs_Y2double1_difference, kp_Y2double1_pass, kp_Y2double1_compare, kp_Y2double1_difference, dkp_Y2double1_pass, dkp_Y2double1_compare, dkp_Y2double1_difference, keff_Y2double1_pass, keff_Y2double1_compare, keff_Y2double1_difference, dkeff_Y2double1_pass, dkeff_Y2double1_compare, dkeff_Y2double1_difference, Ml_Y2double2_pass, Ml_Y2double2_compare, Ml_Y2double2_difference, dMl_Y2double2_pass, dMl_Y2double2_compare, dMl_Y2double2_difference, Mt_Y2double2_pass, Mt_Y2double2_compare, Mt_Y2double2_difference, dMt_Y2double2_pass, dMt_Y2double2_compare, dMt_Y2double2_difference, Fs_Y2double2_pass, Fs_Y2double2_compare, Fs_Y2double2_difference, dFs_Y2double2_pass, dFs_Y2double2_compare, dFs_Y2double2_difference, kp_Y2double2_pass, kp_Y2double2_compare, kp_Y2double2_difference, dkp_Y2double2_pass, dkp_Y2double2_compare, dkp_Y2double2_difference, keff_Y2double2_pass, keff_Y2double2_compare, keff_Y2double2_difference, dkeff_Y2double2_pass, dkeff_Y2double2_compare, dkeff_Y2double2_difference, Ml_Y2double_both_pass, Ml_Y2double_both_compare, Ml_Y2double_both_difference, dMl_Y2double_both_pass, dMl_Y2double_both_compare, dMl_Y2double_both_difference, Mt_Y2double_both_pass, Mt_Y2double_both_compare, Mt_Y2double_both_difference, dMt_Y2double_both_pass, dMt_Y2double_both_compare, dMt_Y2double_both_difference, Fs_Y2double_both_pass, Fs_Y2double_both_compare, Fs_Y2double_both_difference, dFs_Y2double_both_pass, dFs_Y2double_both_compare, dFs_Y2double_both_difference, kp_Y2double_both_pass, kp_Y2double_both_compare, kp_Y2double_both_difference, dkp_Y2double_both_pass, dkp_Y2double_both_compare, dkp_Y2double_both_difference, keff_Y2double_both_pass, keff_Y2double_both_compare, keff_Y2double_both_difference, dkeff_Y2double_both_pass, dkeff_Y2double_both_compare, dkeff_Y2double_both_difference, Ml_Y2user_lifetime_pass, Ml_Y2user_lifetime_compare, Ml_Y2user_lifetime_difference, dMl_Y2user_lifetime_pass, dMl_Y2user_lifetime_compare, dMl_Y2user_lifetime_difference, Mt_Y2user_lifetime_pass, Mt_Y2user_lifetime_compare, Mt_Y2user_lifetime_difference, dMt_Y2user_lifetime_pass, dMt_Y2user_lifetime_compare, dMt_Y2user_lifetime_difference, Fs_Y2user_lifetime_pass, Fs_Y2user_lifetime_compare, Fs_Y2user_lifetime_difference, dFs_Y2user_lifetime_pass, dFs_Y2user_lifetime_compare, dFs_Y2user_lifetime_difference, kp_Y2user_lifetime_pass, kp_Y2user_lifetime_compare, kp_Y2user_lifetime_difference, dkp_Y2user_lifetime_pass, dkp_Y2user_lifetime_compare, dkp_Y2user_lifetime_difference, keff_Y2user_lifetime_pass, keff_Y2user_lifetime_compare, keff_Y2user_lifetime_difference, dkeff_Y2user_lifetime_pass, dkeff_Y2user_lifetime_compare, dkeff_Y2user_lifetime_difference = compare_individual_combine_sum(combine_Y2_rate_results_filepath, sum_histogram_filepath,current_save_path, calculation_type, perform_Y2_single_fit, perform_Y2_double_fit, use_user_specified_lifetime, individual_filepath_and_filename)
    
    
    gatewidth_compare.reverse()
    
    file_descriptions = ('Individual File','Combined Split Files','Feynman Histogram Sum')
    file_descriptions_reverse = file_descriptions[::-1]
    
    if gatewidth_pass == True and Y1_pass == True and dY1_pass == True:    
        Y1_compare.reverse()
        dY1_compare.reverse()
        Y1_difference.reverse()
        dY1_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Y1', 'micro-sec', gatewidth_compare, Y1_compare, marker_size, plot_titles, '', y_unc=dY1_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dY1', 'micro-sec', gatewidth_compare, dY1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Y1 % difference', 'micro-sec', gatewidth_compare[:-1], Y1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dY1 % difference', 'micro-sec', gatewidth_compare[:-1], dY1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R1_pass == True and dR1_pass == True:
        R1_compare.reverse()
        dR1_compare.reverse()
        R1_difference.reverse()
        dR1_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse, 'R1', 'micro-sec', gatewidth_compare, R1_compare, marker_size, plot_titles, '', y_unc=dR1_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse, 'dR1', 'micro-sec', gatewidth_compare, dR1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'R1 % difference', 'micro-sec', gatewidth_compare[:-1], R1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dR1 % difference', 'micro-sec', gatewidth_compare[:-1], dR1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Y2_pass == True and dY2_pass == True:
        Y2_compare.reverse()
        dY2_compare.reverse()
        Y2_difference.reverse()
        dY2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Y2', 'micro-sec', gatewidth_compare, Y2_compare, marker_size, plot_titles, '', y_unc=dY2_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dY2', 'micro-sec', gatewidth_compare, dY2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Y2 % difference', 'micro-sec', gatewidth_compare[:-1], Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dY2 % difference', 'micro-sec', gatewidth_compare[:-1], dY2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ym_pass == True and dYm_pass == True:
        Ym_compare.reverse()
        dYm_compare.reverse()
        Ym_difference.reverse()
        dYm_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Ym', 'micro-sec', gatewidth_compare, Ym_compare, marker_size, plot_titles, '', y_unc=dYm_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dYm', 'micro-sec', gatewidth_compare, dYm_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Ym % difference', 'micro-sec', gatewidth_compare[:-1], Ym_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dYm % difference', 'micro-sec', gatewidth_compare[:-1], dYm_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_single_Y2_pass == True and dR2_single_Y2_pass == True:
        R2_single_Y2_compare.reverse()
        dR2_single_Y2_compare.reverse()
        R2_single_Y2_difference.reverse()
        dR2_single_Y2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse, 'R2', 'micro-sec', gatewidth_compare, R2_single_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_single_Y2_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse, 'dR2', 'micro-sec', gatewidth_compare, dR2_single_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'R2 % difference', 'micro-sec', gatewidth_compare[:-1], R2_single_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dR2 % difference', 'micro-sec', gatewidth_compare[:-1], dR2_single_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_double1_Y2_pass == True and dR2_double1_Y2_pass == True:
        R2_double1_Y2_compare.reverse()
        dR2_double1_Y2_compare.reverse()
        R2_double1_Y2_difference.reverse()
        dR2_double1_Y2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse, 'R2', 'micro-sec', gatewidth_compare, R2_double1_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_double1_Y2_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse, 'dR2', 'micro-sec', gatewidth_compare, dR2_double1_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'R2 % difference', 'micro-sec', gatewidth_compare[:-1], R2_double1_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dR2 % difference', 'micro-sec', gatewidth_compare[:-1], dR2_double1_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_double2_Y2_pass == True and dR2_double2_Y2_pass == True:
        R2_double2_Y2_compare.reverse()
        dR2_double2_Y2_compare.reverse()
        R2_double2_Y2_difference.reverse()
        dR2_double2_Y2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse, 'R2', 'micro-sec', gatewidth_compare, R2_double2_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_double2_Y2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse, 'dR2', 'micro-sec', gatewidth_compare, dR2_double2_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'R2 % difference', 'micro-sec', gatewidth_compare[:-1], R2_double2_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dR2 % difference', 'micro-sec', gatewidth_compare[:-1], dR2_double2_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_double_both_Y2_pass == True and dR2_double_both_Y2_pass == True:
        R2_double_both_Y2_compare.reverse()
        dR2_double_both_Y2_compare.reverse()
        R2_double_both_Y2_difference.reverse()
        dR2_double_both_Y2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse, 'R2', 'micro-sec', gatewidth_compare, R2_double_both_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_double_both_Y2_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse, 'dR2', 'micro-sec', gatewidth_compare, dR2_double_both_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'R2 % difference', 'micro-sec', gatewidth_compare[:-1], R2_double_both_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dR2 % difference', 'micro-sec', gatewidth_compare[:-1], dR2_double_both_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and R2_user_lifetime_Y2_pass == True and dR2_user_lifetime_Y2_pass == True:
        R2_user_lifetime_Y2_compare.reverse()
        dR2_user_lifetime_Y2_compare.reverse()
        R2_user_lifetime_Y2_difference.reverse()
        dR2_user_lifetime_Y2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse, 'R2', 'micro-sec', gatewidth_compare, R2_user_lifetime_Y2_compare, marker_size, plot_titles, '', y_unc=dR2_user_lifetime_Y2_compare, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse, 'dR2', 'micro-sec', gatewidth_compare, dR2_user_lifetime_Y2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'R2 % difference', 'micro-sec', gatewidth_compare[:-1], R2_user_lifetime_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dR2 % difference', 'micro-sec', gatewidth_compare[:-1], dR2_user_lifetime_Y2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_user_lifetime', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and calc_eff_kn_pass == True and calc_eff_unc_kn_pass == True:
        calc_eff_kn_compare.reverse()
        calc_eff_unc_kn_compare.reverse()
        calc_eff_kn_difference.reverse()
        calc_eff_unc_kn_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Efficiency', 'micro-sec', gatewidth_compare, calc_eff_kn_compare, marker_size, plot_titles, '', y_unc=calc_eff_unc_kn_compare, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dEfficiency', 'micro-sec', gatewidth_compare, calc_eff_unc_kn_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Efficiency % difference', 'micro-sec', gatewidth_compare[:-1], calc_eff_kn_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dEfficiency % difference', 'micro-sec', gatewidth_compare[:-1], calc_eff_unc_kn_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path, mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2single_pass == True and dMl_Y2single_pass == True:
        Ml_Y2single_compare.reverse()
        dMl_Y2single_compare.reverse()
        Ml_Y2single_difference.reverse()
        dMl_Y2single_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2single_compare, marker_size, plot_titles, '', y_unc=dMl_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Ml % difference', 'micro-sec', gatewidth_compare[:-1], Ml_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMl % difference', 'micro-sec', gatewidth_compare[:-1], dMl_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2single_pass == True and dMt_Y2single_pass == True:
        Mt_Y2single_compare.reverse()
        dMt_Y2single_compare.reverse()
        Mt_Y2single_difference.reverse()
        dMt_Y2single_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2single_compare, marker_size, plot_titles, '', y_unc=dMt_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Mt % difference', 'micro-sec', gatewidth_compare[:-1], Mt_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMt % difference', 'micro-sec', gatewidth_compare[:-1], dMt_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2single_pass == True and dFs_Y2single_pass == True:
        Fs_Y2single_compare.reverse()
        dFs_Y2single_compare.reverse()
        Fs_Y2single_difference.reverse()
        dFs_Y2single_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2single_compare, marker_size, plot_titles, '', y_unc=dFs_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Fs % difference', 'micro-sec', gatewidth_compare[:-1], Fs_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dFs % difference', 'micro-sec', gatewidth_compare[:-1], dFs_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2single_pass == True and dkp_Y2single_pass == True:
        kp_Y2single_compare.reverse()
        dkp_Y2single_compare.reverse()
        kp_Y2single_difference.reverse()
        dkp_Y2single_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'kp', 'micro-sec', gatewidth_compare, kp_Y2single_compare, marker_size, plot_titles, '', y_unc=dkp_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'kp % difference', 'micro-sec', gatewidth_compare[:-1], kp_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkp % difference', 'micro-sec', gatewidth_compare[:-1], dkp_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2single_pass == True and dkeff_Y2single_pass == True:
        keff_Y2single_compare.reverse()
        dkeff_Y2single_compare.reverse()
        keff_Y2single_difference.reverse()
        dkeff_Y2single_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'keff', 'micro-sec', gatewidth_compare, keff_Y2single_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2single_compare, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2single_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'keff % difference', 'micro-sec', gatewidth_compare[:-1], keff_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkeff % difference', 'micro-sec', gatewidth_compare[:-1], dkeff_Y2single_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_single_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2double1_pass == True and dMl_Y2double1_pass == True:
        Ml_Y2double1_compare.reverse()
        dMl_Y2double1_compare.reverse()
        Ml_Y2double1_difference.reverse()
        dMl_Y2double1_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2double1_compare, marker_size, plot_titles, '', y_unc=dMl_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Ml % difference', 'micro-sec', gatewidth_compare[:-1], Ml_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMl % difference', 'micro-sec', gatewidth_compare[:-1], dMl_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2double1_pass == True and dMt_Y2double1_pass == True:
        Mt_Y2double1_compare.reverse()
        dMt_Y2double1_compare.reverse()
        Mt_Y2double1_difference.reverse()
        dMt_Y2double1_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2double1_compare, marker_size, plot_titles, '', y_unc=dMt_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Mt % difference', 'micro-sec', gatewidth_compare[:-1], Mt_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMt % difference', 'micro-sec', gatewidth_compare[:-1], dMt_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2double1_pass == True and dFs_Y2double1_pass == True:
        Fs_Y2double1_compare.reverse()
        dFs_Y2double1_compare.reverse()
        Fs_Y2double1_difference.reverse()
        dFs_Y2double1_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2double1_compare, marker_size, plot_titles, '', y_unc=dFs_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Fs % difference', 'micro-sec', gatewidth_compare[:-1], Fs_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dFs % difference', 'micro-sec', gatewidth_compare[:-1], dFs_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2double1_pass == True and dkp_Y2double1_pass == True:
        kp_Y2double1_compare.reverse()
        dkp_Y2double1_compare.reverse()
        kp_Y2double1_difference.reverse()
        dkp_Y2double1_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'kp', 'micro-sec', gatewidth_compare, kp_Y2double1_compare, marker_size, plot_titles, '', y_unc=dkp_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'kp % difference', 'micro-sec', gatewidth_compare[:-1], kp_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkp % difference', 'micro-sec', gatewidth_compare[:-1], dkp_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2double1_pass == True and dkeff_Y2double1_pass == True:
        keff_Y2double1_compare.reverse()
        dkeff_Y2double1_compare.reverse()
        keff_Y2double1_difference.reverse()
        dkeff_Y2double1_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'keff', 'micro-sec', gatewidth_compare, keff_Y2double1_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2double1_compare, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2double1_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'keff % difference', 'micro-sec', gatewidth_compare[:-1], keff_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkeff % difference', 'micro-sec', gatewidth_compare[:-1], dkeff_Y2double1_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double1_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2double2_pass == True and dMl_Y2double2_pass == True:
        Ml_Y2double2_compare.reverse()
        dMl_Y2double2_compare.reverse()
        Ml_Y2double2_difference.reverse()
        dMl_Y2double2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2double2_compare, marker_size, plot_titles, '', y_unc=dMl_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Ml % difference', 'micro-sec', gatewidth_compare[:-1], Ml_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMl % difference', 'micro-sec', gatewidth_compare[:-1], dMl_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2double2_pass == True and dMt_Y2double2_pass == True:
        Mt_Y2double2_compare.reverse()
        dMt_Y2double2_compare.reverse()
        Mt_Y2double2_difference.reverse()
        dMt_Y2double2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2double2_compare, marker_size, plot_titles, '', y_unc=dMt_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Mt % difference', 'micro-sec', gatewidth_compare[:-1], Mt_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMt % difference', 'micro-sec', gatewidth_compare[:-1], dMt_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2double2_pass == True and dFs_Y2double2_pass == True:
        Fs_Y2double2_compare.reverse()
        dFs_Y2double2_compare.reverse()
        Fs_Y2double2_difference.reverse()
        dFs_Y2double2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2double2_compare, marker_size, plot_titles, '', y_unc=dFs_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Fs % difference', 'micro-sec', gatewidth_compare[:-1], Fs_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dFs % difference', 'micro-sec', gatewidth_compare[:-1], dFs_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2double2_pass == True and dkp_Y2double2_pass == True:
        kp_Y2double2_compare.reverse()
        dkp_Y2double2_compare.reverse()
        kp_Y2double2_difference.reverse()
        dkp_Y2double2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'kp', 'micro-sec', gatewidth_compare, kp_Y2double2_compare, marker_size, plot_titles, '', y_unc=dkp_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'kp % difference', 'micro-sec', gatewidth_compare[:-1], kp_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkp % difference', 'micro-sec', gatewidth_compare[:-1], dkp_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2double2_pass == True and dkeff_Y2double2_pass == True:
        keff_Y2double2_compare.reverse()
        dkeff_Y2double2_compare.reverse()
        keff_Y2double2_difference.reverse()
        dkeff_Y2double2_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'keff', 'micro-sec', gatewidth_compare, keff_Y2double2_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2double2_compare, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2double2_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'keff % difference', 'micro-sec', gatewidth_compare[:-1], keff_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkeff % difference', 'micro-sec', gatewidth_compare[:-1], dkeff_Y2double2_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double2_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Ml_Y2double_both_pass == True and dMl_Y2double_both_pass == True:
        Ml_Y2double_both_compare.reverse()
        dMl_Y2double_both_compare.reverse()
        Ml_Y2double_both_difference.reverse()
        dMl_Y2double_both_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Ml', 'micro-sec', gatewidth_compare, Ml_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dMl_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMl', 'micro-sec', gatewidth_compare, dMl_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Ml % difference', 'micro-sec', gatewidth_compare[:-1], Ml_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMl % difference', 'micro-sec', gatewidth_compare[:-1], dMl_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Mt_Y2double_both_pass == True and dMt_Y2double_both_pass == True:
        Mt_Y2double_both_compare.reverse()
        dMt_Y2double_both_compare.reverse()
        Mt_Y2double_both_difference.reverse()
        dMt_Y2double_both_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Mt', 'micro-sec', gatewidth_compare, Mt_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dMt_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dMt', 'micro-sec', gatewidth_compare, dMt_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Mt % difference', 'micro-sec', gatewidth_compare[:-1], Mt_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dMt % difference', 'micro-sec', gatewidth_compare[:-1], dMt_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and Fs_Y2double_both_pass == True and dFs_Y2double_both_pass == True:
        Fs_Y2double_both_compare.reverse()
        dFs_Y2double_both_compare.reverse()
        Fs_Y2double_both_difference.reverse()
        dFs_Y2double_both_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'Fs', 'micro-sec', gatewidth_compare, Fs_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dFs_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dFs', 'micro-sec', gatewidth_compare, dFs_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'Fs % difference', 'micro-sec', gatewidth_compare[:-1], Fs_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dFs % difference', 'micro-sec', gatewidth_compare[:-1], dFs_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and kp_Y2double_both_pass == True and dkp_Y2double_both_pass == True:
        kp_Y2double_both_compare.reverse()
        dkp_Y2double_both_compare.reverse()
        kp_Y2double_both_difference.reverse()
        dkp_Y2double_both_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'kp', 'micro-sec', gatewidth_compare, kp_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dkp_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkp', 'micro-sec', gatewidth_compare, dkp_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'kp % difference', 'micro-sec', gatewidth_compare[:-1], kp_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkp % difference', 'micro-sec', gatewidth_compare[:-1], dkp_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
    if gatewidth_pass == True and keff_Y2double_both_pass == True and dkeff_Y2double_both_pass == True:
        keff_Y2double_both_compare.reverse()
        dkeff_Y2double_both_compare.reverse()
        keff_Y2double_both_difference.reverse()
        dkeff_Y2double_both_difference.reverse()
        plot_scatter_gatewidth(file_descriptions_reverse,'keff', 'micro-sec', gatewidth_compare, keff_Y2double_both_compare, marker_size, plot_titles, '', y_unc=dkeff_Y2double_both_compare, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse,'dkeff', 'micro-sec', gatewidth_compare, dkeff_Y2double_both_compare, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'keff % difference', 'micro-sec', gatewidth_compare[:-1], keff_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
        plot_scatter_gatewidth(file_descriptions_reverse[:-1],'dkeff % difference', 'micro-sec', gatewidth_compare[:-1], dkeff_Y2double_both_difference, marker_size, plot_titles, '', y_unc=None, x_div=1000, show=False, save=current_save_path+'_double_both_fit', mult_files=True, yaxis_log=yaxis_log)
#    
    print('End compare individual files, combine_Y2_rate_results, and summed Feynman histogram')
    print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

print('Script complete')
print(strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime()))

