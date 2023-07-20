# uses the total number of counts per channel to create a channel plot
# this is very specific to the NOMAD/MC-15 detector system and is not general for all lmx files with other systems

# version history
# v01: 01/26/2021: initial version
# v02: 01/27/2021: forced placement of legend to bottom-right. Also modified output filename format.
# v03: 02/10/2023: outputs pdf instead of eps now


# standard imports
from matplotlib import pyplot as plt
import glob
import numpy as np
import sys



def channel_plot(file, fname, use_title, title_prefix):

    count_sum =[]
    det_sum = []
    
    # get total detector counts in each channel
    for i in range(1,33):
        count_sum.append(file.detectorCounts(i))
    
    # split into channels 1-15 (detector 1) and 17-31 (detector 2)
    count_det1 = count_sum[0:15]
    count_det2 = count_sum[16:31]
    
    # determine the number of counts in detector 1 and 2
    det1_sum = 0
    for i in range(0,len(count_det1)):
        det1_sum += count_det1[i]
    if det1_sum > 0:
        det_sum.append(count_det1)
    det2_sum = 0
    for i in range(0,len(count_det2)):
        det2_sum += count_det2[i]
    if det2_sum > 0:
        det_sum.append(count_det2)
    if det1_sum+det2_sum == 0:
        sys.exit('There is no data')
    
    # creates a Momentum-style plot
    x = np.linspace(1,15,num=15)
    for i in range(0,len(det_sum)):
        neg_2nd_row = []
        neg_3rd_row = []
        plot_max = 1.1*np.max(det_sum[i])
        fig, ax = plt.subplots(2)
        plot_sum = det_sum[i]
        ax[0].bar(x[0:7],plot_sum[0:7],color='blue',edgecolor="aqua")
        for j in range(7,13):
            neg_2nd_row.append(-1*plot_sum[j])
        neg_2nd_row.append(0)
        for j in range(13,15):
            neg_3rd_row.append(-1*plot_sum[j ])
        ax[1].bar(x[7:14],neg_2nd_row,color='blue',edgecolor="aqua")
        ax[1].bar([9.5,11.5],neg_3rd_row,edgecolor="aqua",alpha=0.7)
        ax[0].set_ylim([0,plot_max])
        ax[1].set_xlim([6.5,14.5])
        ax[1].set_ylim([-1*plot_max,0])
        ax[0].grid(axis='y')
        ax[1].grid(axis='y')
        ax[0].set_ylabel("Counts")
        ax[1].set_ylabel("Counts")
        plt.xlabel("Channel")
        if use_title == True:
            ax[0].set_title(title_prefix+' '+str(i+1))
        if fname != False and type(fname) == str:
                plt.savefig(fname+'_Channel_Counts_Momentum-Style'+'Detector'+str(i+1)+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
                plt.savefig(fname+'_Channel_Counts_Momentum-Style'+'Detector'+str(i+1)+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)
        #plt.show
        plt.close()
    
    # creates a single plot with all three rows
    x = np.linspace(1,7,num=7)
    x_row2 = np.linspace(1.5,6.5,num=6)
    x_row3 = (3,5)
    for i in range(0,len(det_sum)):
        plot_sum = det_sum[i]
        plt.bar(x,plot_sum[0:7],edgecolor="black",alpha=0.7,label='Row 1')
        plt.bar(x_row2,plot_sum[7:13],edgecolor="black",alpha=0.7,label='Row 2')
        plt.bar(x_row3,plot_sum[13:15],edgecolor="black",alpha=0.7,label='Row 3')
        plt.ylim([0,plot_max])
        plt.grid(axis='y')
        plt.ylabel("Counts")
        plt.xticks([])
        plt.legend(loc='lower right')
        if use_title == True:
            plt.title(title_prefix+' '+str(i+1))
        if fname != False and type(fname) == str:
                plt.savefig(fname+'_Channel_Counts_'+'Detector'+str(i+1)+'.png',dpi=500,bbox_inches='tight',pad_inches=0.1)
                plt.savefig(fname+'_Channel_Counts_'+'Detector'+str(i+1)+'.pdf',dpi=500,bbox_inches='tight',pad_inches=0.1)
        #plt.show
        plt.close()

#for i in range(0,len(fname)):
#    file = readLMXFile(f_and_p_name[i])
#    plot_reults = channel_plot(file,fname[i])
