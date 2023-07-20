# script for plotting results


from matplotlib import pyplot as plt
from scipy import stats
import numpy as np
import sys
import os


def plot_scatter_gatewidth(file_descriptions, plot_name, units, x, y, marker_size, plot_titles, title,  y_unc=None, x_div=False, show=True, save=False, mult_files=False, fit1=False, fit2=False, yaxis_log=False):
    
    if mult_files == True:
        for j in range(0,len(x)):
            series_x = x[j]
            series_y = y[j]
            if type(fit1) != bool:
                fit1_xy = fit1[j]
                fit1_x_old = fit1_xy[0]
                fit1_y = fit1_xy[1]
            if type(fit2) != bool:
                fit2_xy = fit2[j]
                fit2_x_old = fit2_xy[0]
                fit2_y = fit2_xy[1]
            if y_unc != None:
                series_y_unc = y_unc[j]
            
            if file_descriptions is not None and len(file_descriptions) > 0:
                series_name = file_descriptions[j]
            else:
                series_name = None
            
            if x_div != False:
                new_x = [entry/x_div for entry in series_x]
                if type(fit1) != bool:
                    fit1_x = [entry/x_div for entry in fit1_x_old]
                if type(fit2) != bool:
                    fit2_x = [entry/x_div for entry in fit2_x_old]
            else:
                new_x = series_x
                if type(fit1) != bool:
                    fit1_x = fit1_x_old
                if type(fit2) != bool:
                    fit2_x = fit2_x_old
                
                
            plt.scatter(new_x,series_y,marker_size,label=series_name) 
            
            colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
            
            if y_unc != None:
                
                y_unc_min = []
                y_unc_max = []
                for k in range(0,len(series_y_unc)):
                    y_unc_min.append(series_y[k]-series_y_unc[k])
                    y_unc_max.append(series_y[k]+series_y_unc[k])
                
                if len(x) < len(colors):
                    plt.fill_between(new_x, y_unc_min, y_unc_max, facecolor=colors[j], alpha=0.5)
                else:
                    plt.fill_between(new_x, y_unc_min, y_unc_max, alpha=0.5)
                #plt.errorbar(new_x,series_y, yerr=series_y_unc, fmt="o", ms=marker_size)
                
            if type(fit1) != bool:
                if len(x) < len(colors):
                    plt.plot(fit1_x,fit1_y, linestyle="--", color=colors[j], linewidth=2, alpha=0.6)
                else:
                    plt.plot(fit1_x,fit1_y, linestyle="--", linewidth=2, alpha=0.6)
            if type(fit2) != bool:
                if len(x) < len(colors):
                    plt.plot(fit2_x,fit2_y, linestyle=":", color=colors[j], linewidth=2, alpha=0.6)
                else:
                    plt.plot(fit2_x,fit2_y, linestyle=":", linewidth=2, alpha=0.6)
            
    else:
        series_x = x
        series_y = y
        series_y_unc = y_unc
        
        if x_div != False:
            new_x = [entry/x_div for entry in series_x]
            if type(fit1) != bool:
                fit1_x = [entry/x_div for entry in fit1[0]]
            if type(fit2) != bool:
                fit2_x = [entry/x_div for entry in fit2[0]]
        else:
            new_x = series_x
            if type(fit1) != bool:
                fit1_x = fit1[0]
            if type(fit2) != bool:
                fit2_x = fit2[0]
    
        plt.scatter(new_x,series_y,marker_size) 
    
        if y_unc != None:
            
            colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
            
            y_unc_min = []
            y_unc_max = []
            for k in range(0,len(series_y_unc)):
                y_unc_min.append(series_y[k]-series_y_unc[k])
                y_unc_max.append(series_y[k]+series_y_unc[k])
            
            plt.fill_between(new_x, y_unc_min, y_unc_max, facecolor=colors[0], alpha=0.5)
            #plt.errorbar(new_x,series_y, yerr=series_y_unc, fmt="o", ms=marker_size)
            
        if type(fit1) != bool:
            plt.plot(fit1_x,fit1[1], linestyle="--", color='k', linewidth=2, label="Single fit", alpha=0.8)
        if type(fit2) != bool:
            plt.plot(fit2_x,fit2[1], linestyle=":", color='r', linewidth=2, label="Double fit", alpha=0.8)
        
    
    plt.grid()
    plt.xlabel('Gate-width ('+units+')')
    plt.ylabel(plot_name)

    if plot_titles == True:
        plt.title(title)
    
    if yaxis_log == True:
        plt.yscale("log")  
    
    if mult_files == True:
        if file_descriptions is not None:
            if len(file_descriptions) > 0 or type(fit1) != bool or type(fit2) != bool:
                plt.legend()
        if save != False and type(save) == str:
            plt.savefig(save+'_'+plot_name+'_vs_gatewidth.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
            plt.savefig(save+'_'+plot_name+'_vs_gatewidth.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)
    else:
        if save != False and type(save) == str:
                plt.savefig(save+'_'+plot_name+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
                plt.savefig(save+'_'+plot_name+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    if show:
        plt.show()
    else:
        plt.clf()


def plot_scatter(x_name, y_name, x, y, marker_size, y_unc=None, show=True, save=False, yaxis_log=False):
       
    plt.scatter(x,y,marker_size) 

    if y_unc != None:
        
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        
        # y_unc_min = []
        # y_unc_max = []
        # for k in range(0,len(y_unc)):
        #     y_unc_min.append(y[k]-y_unc[k])
        #     y_unc_max.append(y[k]+y_unc[k])
        
        # plt.fill_between(x, y_unc_min, y_unc_max, facecolor=colors[0], alpha=0.5)
        plt.errorbar(x,y, yerr=y_unc, fmt="o", ms=marker_size)
    
    plt.grid()
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    
    if yaxis_log == True:
        plt.yscale("log")  
    
    if save != False and type(save) == str:
            plt.savefig(save+y_name+'_'+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
            plt.savefig(save+y_name+'_'+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    if show:
        plt.show()
    else:
        plt.clf()
    
        
def plot_scatter_with_stats(x_name, y_name, x, y, y_avg, y_sd, y_unc_avg, marker_size, y_unc=None, show=True, save=False, yaxis_log=False, show_avg=False, show_sd=False, show_unc_avg=False):
       
    plt.scatter(x,y,marker_size) 

    if y_unc != None:
        
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        if show_avg == True or show_unc_avg == True or show_sd == True:
            plt.errorbar(x,y, yerr=y_unc, fmt="o", ms=marker_size, alpha = 0.8)
        else:
            plt.errorbar(x,y, yerr=y_unc, fmt="o", ms=marker_size)
    
    if show_avg == True:
        plt.axhline(y_avg,label='Weighted Average',color='r') 
    
    if show_sd == True:
        plt.axhline(y_avg+y_sd,label='+1sd',color='fuchsia', linestyle=":") 
        plt.axhline(y_avg-y_sd,label='-1sd',color='fuchsia', linestyle=":") 
        plt.axhline(y_avg+2*y_sd,label='+2sd',color='lime', linestyle=":") 
        plt.axhline(y_avg-2*y_sd,label='-2sd',color='lime', linestyle=":") 
    
    if show_unc_avg == True:
        plt.axhline(y_avg+y_unc_avg,label='+1unc',color='indigo', alpha = 0.8) 
        plt.axhline(y_avg-y_unc_avg,label='-1unc',color='indigo', alpha = 0.8) 
        plt.axhline(y_avg+2*y_unc_avg,label='+2unc',color='darkgreen', alpha = 0.8) 
        plt.axhline(y_avg-2*y_unc_avg,label='-2unc',color='darkgreen', alpha = 0.8) 
    
    if show_avg == True or show_sd == True or show_unc_avg == True:
        plt.legend(bbox_to_anchor=(1.05,1))
    
    plt.grid()
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    
    if yaxis_log == True:
        plt.yscale("log")  
    
    if save != False and type(save) == str:
            plt.savefig(save+y_name+'_'+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
            plt.savefig(save+y_name+'_'+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    if show:
        plt.show()
    else:
        plt.clf()


def plot_scatter_stat_percent(x_name, y_name, x, y, y_avg, y_sd, y_unc_avg, marker_size, x_div=False, show=True, save=False, yaxis_log=False, show_unc=False):
    
    series_x = x
    series_y = y
    
    if x_div != False:
        new_x = [entry/x_div for entry in series_x]
    else:
        new_x = series_x
    
    one_sd_in_counter_list = []
    two_sd_in_counter_list = []
    three_sd_in_counter_list = []
    one_unc_in_counter_list = []
    two_unc_in_counter_list = []
    three_unc_in_counter_list = []
    for i in range(0,len(new_x)):
        y_current = y[i]
        if show_unc == True:
            y_unc_avg_current = y_unc_avg[i]
            y_avg_current = y_avg[i]
            y_sd_current = y_sd[i] 
        else:
            y_avg_current = np.average(y_current)
            y_sd_current = np.std(y_current, ddof=1)
        one_sd_in_counter = 0
        two_sd_in_counter = 0
        three_sd_in_counter = 0
        one_unc_in_counter = 0
        two_unc_in_counter = 0
        three_unc_in_counter = 0
        for entry in y_current:
            if entry >= y_avg_current-y_sd_current and entry <= y_avg_current+y_sd_current:
                one_sd_in_counter += 1
            if entry >= y_avg_current-2*y_sd_current and entry <= y_avg_current+2*y_sd_current:
                two_sd_in_counter += 1
            if entry >= y_avg_current-3*y_sd_current and entry <= y_avg_current+3*y_sd_current:
                three_sd_in_counter += 1
            if show_unc == True:
                if entry >= y_avg_current-y_unc_avg_current and entry <= y_avg_current+y_unc_avg_current:
                    one_unc_in_counter += 1
                if entry >= y_avg_current-2*y_unc_avg_current and entry <= y_avg_current+2*y_unc_avg_current:
                    two_unc_in_counter += 1
                if entry >= y_avg_current-3*y_unc_avg_current and entry <= y_avg_current+3*y_unc_avg_current:
                    three_unc_in_counter += 1
        one_sd_in_counter_list.append(100*one_sd_in_counter/len(y_current))
        two_sd_in_counter_list.append(100*two_sd_in_counter/len(y_current))
        three_sd_in_counter_list.append(100*three_sd_in_counter/len(y_current))
        if show_unc == True:
            one_unc_in_counter_list.append(100*one_unc_in_counter/len(y_current))
            two_unc_in_counter_list.append(100*two_unc_in_counter/len(y_current))
            three_unc_in_counter_list.append(100*three_unc_in_counter/len(y_current))
            
        
    plt.scatter(new_x,one_sd_in_counter_list, marker_size, label='1sd',color='lightblue', marker="x")
    plt.scatter(new_x,two_sd_in_counter_list, marker_size, label='2sd',color='lime', marker="x")
    plt.scatter(new_x,three_sd_in_counter_list, marker_size, label='3sd',color='red', marker="x")
    if show_unc == True:
        plt.scatter(new_x,one_unc_in_counter_list, marker_size, label='1unc',color='dodgerblue', alpha = 0.8)
        plt.scatter(new_x,two_unc_in_counter_list, marker_size, label='2unc',color='darkgreen', alpha = 0.8)
        plt.scatter(new_x,three_unc_in_counter_list, marker_size, label='3unc',color='maroon', alpha = 0.8)

    plt.axhline(68.2689492, label='Expected 1', color='blue', linestyle=":") 
    plt.axhline(95.4499736, label='Expected 2', color='mediumaquamarine', linestyle=":") 
    plt.axhline(99.7300204, label='Expected 3', color='tomato', linestyle=":") 
    
    xmin, xmax, ymin, ymax = plt.axis()
    if ymin >= 50:
        plt.ylim(bottom=50)
        
    
    plt.legend(bbox_to_anchor=(1.05,1))

    plt.grid()
    plt.xlabel('Gate-width ('+x_name+')')
    plt.ylabel(y_name+' % of data')
    
    if yaxis_log == True:
        plt.yscale("log")  

    if save != False and type(save) == str:
        plt.savefig(save+'_'+y_name+'_stat_pct.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
        plt.savefig(save+'_'+y_name+'_stat_pct.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    if show:
        plt.show()
    else:
        plt.clf()
        

def plotHistogram_multi(file_descriptions, current_gatewidth, x,y,P,show=True, save=False, log=False, normalize=False, title=False):
       
    # note that if Normalize = True, then y and P are already normalized from previous operations
    
    x_list = []
    for current in x:
        x_list.append([i for i in current])
    
    figure, axis = plt.subplots()
    
    if normalize == True:
        y_no_zero = [[ele for ele in sub if ele !=0] for sub in y]
        P_no_zero = [[ele for ele in sub if ele !=0] for sub in P]
        y_no_zero_value = 1e5
        for current_y in y_no_zero:
            y_no_zero_value = np.min([y_no_zero_value,np.min(current_y)])
    
    axis.set_xlabel('Multiplet, n')
    if normalize == True:
        axis.set_ylabel('Probability, pn')
    else:
        axis.set_ylabel('Frequency, Cn')
    
    for m in range(0,len(x)):
        
        if len(file_descriptions) > 0:
            series_name = file_descriptions[m]
        else:
            series_name = None
        
        axis.bar(x_list[m], y[m], alpha=0.5, width=0.8, label=series_name)
        axis.plot(x_list[m], P[m])
        
        ymin_data, ymax_data = axis.get_ylim()
            
    if log == True:
        axis.set_yscale("log")
        if normalize == True:
            axis.set_ylim(bottom=y_no_zero_value, top=ymax_data)
        else:
            axis.set_ylim(bottom=1e-1, top=ymax_data)
          
    if title != False:
        plt.title(title)
    
    # Note: removed step limit from histogram multi, as it was causing issues. Will add back in if needed.
        
    if len(file_descriptions) > 0:
        plt.legend()

    if save != False and type(save) == str:
        plt.savefig(save+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
        plt.savefig(save+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    if show:
        figure.show()
    else:
        figure.clear()


def plotHistogram_single(current_gatewidth, x,y,P,show=True, limit_step=False, save=False, log=False,xmin=False, xmax=False, ymin=False, ymax=False, normalize=False, title=False):
       
#    x_list = []
#    for current in x:
#        x_list.append([i for i in current])
    
    figure, axis = plt.subplots()
    
    if normalize == True:
        y = [element/sum(y) for element in y]
        y_no_zero = [element for element in y if element != 0]
    
    axis.set_xlabel('Multiplet, n')
    if normalize == True:
        axis.set_ylabel('Probability, pn')
    else:
        axis.set_ylabel('Frequency, Cn')
    
#    for m in range(0,len(x)):
    
    axis.bar(x, y, alpha=0.5, width=0.8)
        
    if normalize == True:
        ymin_data = np.min(y_no_zero)
        ymax_data = np.max(y)
    else:
        ymin_data, ymax_data = axis.get_ylim()
    
    axis.plot(x, P, 'r-')    
    ymin_pos, ymax_pos = axis.get_ylim()
    
    if type(xmin) == int or type(xmin) == float:
        axis.set_xlim(left=xmin, right=xmax)
        axis.set_ylim(top=ymax)
    else:
        axis.set_ylim(top=np.max([ymax_data,ymax_pos]))
    
    if log == True:
        axis.set_yscale("log")
        if normalize == True:
            if type(xmin) == int or type(xmin) == float:
                axis.set_ylim(bottom=ymin)
            else:
                axis.set_ylim(bottom=ymin_data)
        else:
            axis.set_ylim(bottom=1e-1)
    else:
        if type(xmin) == int or type(xmax) == float:
            axis.set_ylim(bottom=ymin)
        else:
            axis.set_ylim(bottom=ymin_data)
        
    if title != False:
        plt.title(title)
    
    # The 10 here is somewhat arbitrary, but this ensures that the x-axis doesn't have so many ticks that it is unreadable.
    step_limit = 10
    if limit_step == True and len(x) > step_limit:
        axis.set_xticks(np.arange(0,x[len(x)-1], step=int(x[len(x)-1]/step_limit)))

    if save != False and type(save) == str:
        plt.savefig(save+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
        plt.savefig(save+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    if show:
        figure.show()
    else:
        plt.close(figure)
    

def plotResiduals_xml(gatewidth_list, Y2_distribution_value, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, gaussianBins: int = 100, show=False, save=False):
    """Creates residual plots comparing residual vs gatewidths and histogram of residuals

        Arguments:
            show: Defaults to displaying the figure
            gaussianBins: The amount of bins desired for histogram of residuals

        Returns:
              figure: Variable containing figure with subplots
              axis  : Variable used to control aspects of figure and subplots
    """
    figure, axis = plt.subplots(2, 1)
    if perform_Y2_single_fit == True:
        try:
            log1_result = fit1LogDistribution
            residual1 = [row[0] - row[1] for row in zip(Y2_distribution_value, log1_result)]
            axis[0].plot(gatewidth_list, residual1, markerfacecolor="None", color='k', marker="o", linestyle='None',
                         label="single term")
            hist1, bin1 = np.histogram(residual1, gaussianBins)
            axis[1].plot((bin1[1:] + bin1[:-1]) / 2, hist1, color='k', drawstyle='steps-mid', label="single term")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 1-log fit prevents inclusion in the plot \n")

    if perform_Y2_double_fit_continue == True:
        try:
            log2_result = fit2LogDistribution
            residual2 = [row[0] - row[1] for row in zip(Y2_distribution_value, log2_result)]
            axis[0].plot(gatewidth_list, residual2, color='r', marker="x", linestyle='None', label="double term")
            hist2, bin2 = np.histogram(residual2, gaussianBins)
            axis[1].plot((bin2[1:] + bin2[:-1]) / 2, hist2, color='r', drawstyle='steps-mid', label="double term")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 2-log fit prevents fit prevents inclusion in the plot \n")

    axis[0].set_xlabel('Gate Width [ns]', fontsize=16)
    axis[0].set_ylabel('Residual', fontsize=16)
    axis[0].legend()
    axis[0].set_xscale("log")

    axis[1].set_xlabel('Residual', fontsize=16)
    axis[1].set_ylabel('Counts', fontsize=16)
    axis[1].legend()

    figure.tight_layout()

    if show:
        figure.show()
    
    if save != False and type(save) == str:
        plt.savefig(save+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
        plt.savefig(save+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)
    
    plt.close(figure)
    
    return figure, axis

def plotY2_xml(gatewidth_list, Y2_distribution_value, fit1LogDistribution, fit2LogDistribution, perform_Y2_single_fit, perform_Y2_double_fit_continue, residuals=False, gaussianBins=50, show=False, save=False):
    """Creates a plot of the Y2 distribution
       User can specify if they want fits overlaying and if the residual figure appears

        Arguments:
            fits: User defines if they want the fits overlaying the raw calculation, does 1log and 2log
            residuals: User defines if they want to see figure of residuals
            gaussianBins: The amount of bins desired for histogram of residuals
            show: Defaults to displaying all figures
            
        Returns:
              figure: Variable containing Rossi figure
              axis : Variable used to control aspects of Rossi figure
              if residuals is True: figure and axis for residuals
    """
    figure, axis = plt.subplots()
    axis.plot(gatewidth_list, Y2_distribution_value, color='#00aaffff', label="Raw Calculation",
              drawstyle='steps-mid', linewidth=2)
    axis.set_xlabel('Gate Width [ns]', fontsize=16)
    axis.set_ylabel('Counts', fontsize=16)
    axis.set_yscale("log")
    axis.set_xscale("log")
    
    if perform_Y2_single_fit == True:
        try:
            fit1 = fit1LogDistribution
            axis.plot(gatewidth_list, fit1, label="log1", color='k', linestyle="--", linewidth=2)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 1-log fit prevents the calculation from occurring \n")

    if perform_Y2_double_fit_continue == True:
        try:
            fit2 = fit2LogDistribution
            axis.plot(gatewidth_list, fit2, label="log2", color='r', linestyle=":", linewidth=2)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print(e)
            print("Poor 2-log fit prevents the calculation from occurring \n")

    axis.legend()
    figure.tight_layout()
    if show:
        figure.show()
    
    if save != False and type(save) == str:
        plt.savefig(save+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
        plt.savefig(save+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    plt.close(figure)
    
    return (figure, axis, plotResiduals(gaussianBins, show=show)) if residuals else (figure, axis, None, None)


def plotHistogram_vs_gaussian(plot_name, current_gatewidth, y, y_avg, y_sd, y_unc_avg, show=True, limit_step=False, save=False, log=False, title=False, show_gaussian=False, show_avg=False, show_sd=False, show_unc_avg=False):
    
    """ Function for plotting a histogram of data (y).
    If arguments are set to True, then it will also plot vertical lines for average, standard deviation, and uncertainty average.
    If set to True, it will also plot a Gaussian distribution."""
    
    figure, axis = plt.subplots()
    
    axis.set_xlabel(plot_name)
    axis.set_ylabel('Frequency')
    
    n, bins, patches = axis.hist(y, density=1, alpha = 0.5, label='Data')
            
    if show_avg == True:
        plt.axvline(y_avg,label='Weighted Average',color='r') 
    
    if show_sd == True:
        plt.axvline(y_avg+y_sd,label='+1sd',color='fuchsia', linestyle=":") 
        plt.axvline(y_avg-y_sd,label='-1sd',color='fuchsia', linestyle=":") 
        plt.axvline(y_avg+2*y_sd,label='+2sd',color='lime', linestyle=":") 
        plt.axvline(y_avg-2*y_sd,label='-2sd',color='lime', linestyle=":") 
    
    if show_unc_avg == True:
        plt.axvline(y_avg+y_unc_avg,label='+1unc',color='indigo', alpha = 0.8) 
        plt.axvline(y_avg-y_unc_avg,label='-1unc',color='indigo', alpha = 0.8) 
        plt.axvline(y_avg+2*y_unc_avg,label='+2unc',color='darkgreen', alpha = 0.8) 
        plt.axvline(y_avg-2*y_unc_avg,label='-2unc',color='darkgreen', alpha = 0.8) 
    
    if show_gaussian == True:
        gauss_x = np.linspace(y_avg-3*y_sd, y_avg+3*y_sd, num=10000)
        gaussian_y = ((1 / (np.sqrt(2 * np.pi) * y_sd)) * np.exp(-0.5 * (1 / y_sd * (gauss_x - y_avg))**2))
        plt.plot(gauss_x, gaussian_y, label='Gaussian',color='black')
    
    xmin_data, xmax_data = axis.get_xlim()
    axis.set_xlim(right=xmax_data+4*y_sd)
    
    
    plt.legend(loc='upper right')
    
    if log == True:
        axis.set_yscale("log")
        
    if title != False:
        plt.title(title)
        
    # The 10 here is somewhat arbitrary, but this ensures that the x-axis doesn't have so many ticks that it is unreadable.
    step_limit = 10
    if limit_step == True and len(x) > step_limit:
        axis.set_xticks(np.arange(0,x[len(x)-1], step=int(x[len(x)-1]/step_limit)))

    if save != False and type(save) == str:
        plt.savefig(save+plot_name+'_.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
        plt.savefig(save+plot_name+'_.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)

    if show:
        figure.show()
    else:
        plt.close(figure)
        



# test data

#y  = [0.43717400320390265, 0.4423211269357723, 0.4537949245722819, 0.434338263546016, 0.4421627496383962, 0.43377795979623235, 0.43994894407603224, 0.4479724570569925, 0.4441574396347838, 0.4303857557900739, 0.43183750751145045, 0.43143597488141583, 0.444018166919417, 0.4406699336637323, 0.43139551020865685, 0.4358172722549196, 0.4333168654385351, 0.438926866403057, 0.44591338983330053, 0.4431487783058419, 0.43786558850137114, 0.4433557394405838, 0.4338285187073596, 0.45134896816482906, 0.4308952954129657, 0.44189589689402453, 0.4337246285865475, 0.44398460894588276, 0.43784118646915604, 0.4515765348263392, 0.43771146288325635, 0.45275018013969537, 0.4443426048097141, 0.43441961323961675, 0.44859336152480367, 0.44416291802136243] 
#y_avg = 0.44010608647570965 
#y_sd = 0.006676302016861342 
#y_unc_avg = 0.007611462353575006
#plot_name = 'Y'
#current_gatewidth = 2048000
#save = r'C:\Data\NeSO_combined\output\Combined\Stat_Plots/'
#plotHistogram_vs_gaussian(plot_name, current_gatewidth, y, y_avg, y_sd, y_unc_avg, show=True, limit_step=False, save=False, log=False, title=False, show_gaussian=True, show_avg=False, show_sd=False, show_unc_avg=False)

# y= [341.1803203, 337.5218147, 343.06125, 339.8791985, 339.8729403, 340.944647, 338.6555547, 340.9402998, 341.6770752, 339.8999972, 340.6457404, 338.7356192, 342.3043324, 337.5520425, 339.6759356, 340.1660653, 340.4473581, 341.4010661, 339.2916939, 342.5116978, 340.3995969, 341.1889563, 339.6250821, 342.8239952, 340.337402, 342.2744174, 339.9845594, 341.2586691, 339.998399, 340.1461997, 341.088844, 341.7036603, 338.9556718, 339.6962977, 342.8369837, 341.7063245, 342.3438227, 341.699768, 342.8734612, 339.6590097, 341.9237707, 339.1001162, 339.3757689, 340.1466163, 341.0670331, 341.7484791, 342.3632288, 342.6381853, 343.4156466, 339.8374393, 342.3667488, 339.1118729, 338.0912888, 340.5011315, 339.2462413, 340.5899041, 341.8856017, 339.7727268, 341.065724, 337.9344643, 340.8046029, 340.9110322, 339.3857654, 341.1691126, 340.5452991, 340.1803143, 339.917373, 339.8615004, 339.9736859, 341.0168986, 341.5612003, 340.6435807, 341.2708718, 340.6903349, 340.548102, 340.9139834, 339.6604721, 340.4509032, 342.5826951, 337.9556357, 339.6577254, 341.0259573, 340.5670901, 341.2615353, 340.9702965, 342.0640133, 341.9322255, 341.6407676, 341.7648079, 340.9749514, 341.6606235, 341.7046885, 338.733404, 339.8966377, 339.653415, 340.4176622, 337.7048774, 338.1811682, 341.5423351, 340.2050864, 338.4848454, 341.5825109, 341.6668847, 339.6356842, 338.6206975, 339.4803822, 341.6052687, 339.5958678, 343.9936964, 338.2251507, 340.3573945, 341.398237, 339.8777438, 343.9547732, 339.2128952, 337.8661767, 342.941355, 340.1936886, 339.8235111, 340.1556942, 340.6516282, 340.8745808, 341.2231742, 338.714743, 340.4551863, 341.6829941, 340.1898025, 339.17185, 340.1887911, 338.870855, 335.951491, 341.4848699, 342.5625665, 341.288488, 342.2335259, 341.1378746, 341.1110858, 339.9530528, 343.4157238, 342.0360797, 342.2573003, 341.4115414, 341.1024723, 341.0676104, 341.0224609, 340.2745547, 340.6673828, 338.3294513, 341.0561449, 341.8751402, 340.0314499, 338.7929903, 340.8469011, 342.5592647, 341.1701032, 341.1613737, 341.3127009, 338.7131748, 342.4103383, 340.6185014, 337.6467371, 341.8935392, 341.1589545, 338.8817631, 340.3995016, 341.0817832, 341.4494152, 341.8533979, 343.158337, 340.9679664, 339.6410837, 339.8344806, 340.790956, 340.3999759, 342.9584097, 337.098238, 339.5802115, 339.9806572, 339.9528407, 339.042141, 339.8887962, 342.9658824, 339.1825702, 340.6950209, 341.3036211, 338.128421, 342.2051352, 341.2235108, 341.8366806, 341.717297, 338.2557841, 339.2987258]
# y_avg = 340.55289629531205
# y_sd = 1.3839009373383697
# y_unc_avg = 1.2787390228201836
# plot_name = 'Y'
# current_gatewidth = 2048000
# save = r'C:\Data\NeSO_combined\output\Combined\Stat_Plots/'
# plotHistogram_vs_gaussian(plot_name, current_gatewidth, y, y_avg, y_sd, y_unc_avg, show=False, limit_step=False, save=save, log=False, title=False, show_gaussian=True, show_avg=False, show_sd=False, show_unc_avg=False)


## # random w/ scaling = 1
#y_avg = 1
#y_sd = 0.5
#y_unc_avg = y_sd*0.95
#y = y_avg+y_sd*np.random.randn(1000)
#plot_name = 'Y'
#current_gatewidth = 2048000
#save = r'C:\Data\NeSO_combined\output\Combined\Stat_Plots/'
#plotHistogram_vs_gaussian(plot_name, current_gatewidth, y, y_avg, y_sd, y_unc_avg, show=True, limit_step=False, save=False, log=False, title=False, show_gaussian=True, show_avg=False, show_sd=False, show_unc_avg=False)
#
#
## # random w/ scaling = 100
#y_avg = 100
#y_sd = 5
#y_unc_avg = y_sd*0.95
#y = y_avg+y_sd*np.random.randn(100)
#plot_name = 'Y'
#current_gatewidth = 2048000
#save = r'C:\Data\NeSO_combined\output\Combined\Stat_Plots/'
#plotHistogram_vs_gaussian(plot_name, current_gatewidth, y, y_avg, y_sd, y_unc_avg, show=True, limit_step=False, save=False, log=False, title=False, show_gaussian=True, show_avg=False, show_sd=False, show_unc_avg=False)
#
#
## # random w/ scaling = 0.001
#y_avg = 0.001
#y_sd = 0.00001
#y_unc_avg = y_sd*0.95
#y = y_avg+y_sd*np.random.randn(1000)
#plot_name = 'Y'
#current_gatewidth = 2048000
#save = r'C:\Data\NeSO_combined\output\Combined\Stat_Plots/'
#plotHistogram_vs_gaussian(plot_name, current_gatewidth, y, y_avg, y_sd, y_unc_avg, show=True, limit_step=False, save=False, log=False, title=False, show_gaussian=True, show_avg=False, show_sd=False, show_unc_avg=False)
