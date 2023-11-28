import numpy as np
import time
from scipy.signal import welch
import h5py
import os 

'''
This function calculated the chunks of data to avoid crashes as the data takes
steps in magnitude, and bloats the bin sizes. It finds changes in data greater
tha a given threshold in % value. It then takes that index and seperates the
data.
'''
def find_large_relative_changes(data, threshold_percent, datasize=25000):
    change_indices = []
    
    for i in range(1, len(data)):
        change_percentage = abs(data[i] - data[i - 1]) / data[i - 1] * 100
        if change_percentage > threshold_percent:
            change_indices.append(i)
    chunks = []
    start_idx = 0
    
    for end_idx in change_indices:
        chunk = data[start_idx:end_idx]
        chunks.append(chunk)
        start_idx = end_idx
    
    # Add the last chunk (from the last change index to the end of the data)
    if start_idx < len(data):
        last_chunk = data[start_idx:]
        chunks.append(last_chunk)
    # Further split chunks into smaller ones
    smaller_chunks = []
    for chunk in chunks:
        if len(chunk) <= datasize:
            smaller_chunks.append(chunk)
        else:
            num_subchunks = len(chunk) // datasize
            remaining_data = chunk
            for _ in range(num_subchunks):
                subchunk = remaining_data[:datasize]
                smaller_chunks.append(subchunk)
                remaining_data = remaining_data[datasize:]
            if remaining_data.size > 0:
                smaller_chunks.append(remaining_data)
            smaller_chunks = smaller_chunks
    return chunks, smaller_chunks

'''
This is the main function that operates on the data. It calculates the bin
sizes and takes the histogram of the data chunk. It calculates the frequency
and does the Welch approximation. Finally, it stores the Welch data, and the
chunk index for writing to an HDF5 file.
'''


def process_chunk(chunk_index, chunk_data, dwell_time_ms, nperseg_m):
    # Create the histogram
    bin_width_ps = dwell_time_ms * 1e9  # Convert ms to ps
    # Define explicit bin edges
    bin_edges = np.arange(min(chunk_data), max(chunk_data) + bin_width_ps,
                          bin_width_ps)
    hist, _ = np.histogram(chunk_data, bins=bin_edges)

    fs = round(1 / (dwell_time_ms / int(1000)))  # Frequency converting ns to s
    f, Pxx = welch(hist, fs, nperseg=nperseg_m, window='boxcar')
    result = {
        'chunk_index': chunk_index,
        'f': f,
        'Pxx': Pxx,
    }
    return result


'''
This takes the data from the previous function and a file name for the output.
It uses the chunk index to organize the dataset within the file as a group. It
then puts the Welch data inside of a dataset within the group.
'''
def write_chunk_to_hdf5(result, dwell_time_ms, hdf5_filename, save_interval=5):
    chunk_index = result['chunk_index']
    f = result['f']
    Pxx = result['Pxx']
    dwell_time_ms = dwell_time_ms

    with h5py.File(hdf5_filename, 'a') as hdf5_file:
        # Create a group (tree) for each chunk
        group_name = f'Chunk_{chunk_index}'
        group = hdf5_file.create_group(group_name)

        # Create datasets within the group
        group.create_dataset('f', data=f)
        group.create_dataset('Pxx', data=Pxx)
        group.create_dataset('Dwell', data=dwell_time_ms)
        print(f'Chunk {chunk_index} Completed')

        # Check if it's time to save the file
        if chunk_index % save_interval == 0:
            hdf5_file.flush()
            print(f'Saved HDF5 File at Chunk {chunk_index}')

'''
Function to format time into desired output. Some runs could take hours, and 
some could take seconds, so it is good to just make sure it can be presented 
as either or. 
'''

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    formatted_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    return formatted_time

'''
This is the start of the main file. The timer is started, and the directory
and desired file is chosen from a list using an index. The dwell time and
nperseg is selected.
'''

start_time = time.time()  # Start a timer for optimizing purposes

dirpath = '/Users/schuylertyler/Desktop/Test/MUSiC_Data/'
MUSiC_Data = ['1_n_times_RF3-24_90min.txt', 
              '2_n_times_RF3-30_86min.txt',
              '3_RF3-34_60min.txt',
              '4_RF3-38_60min.txt',
              '5_RF3-40_59min.txt',
              '6_RF3-42_60min.txt',
              '7_RF3-44_58min.txt']
MUSiC_Data = MUSiC_Data[-1]
path = dirpath + MUSiC_Data
data = np.loadtxt(path)  # Load in the data

# Define user variables
dwell_time_ms = 5e-7
nperseg_m = 2e5


'''
The chunks are created here. The threshold percent looks far large changes
that correspond to a new minute of measurements, as these files are all 
time combined into a single file. This is similar to just breaking it up into
minute by minute folder data. Sub chunks are made to a restricted size for
memory saving purposes during operation. 
'''

# Set the relative threshold percentage
threshold_percent = 0.2 # 0.2 for Cfig7
chunks, schunks = find_large_relative_changes(data, threshold_percent)
print(f'{len(chunks)} Chunks Created')
print(f'{len(schunks)} Sub Chunks Created (Memory Saving Option)')


'''
The HDF5 file is made in this section. If the name is already taken, a 
duplicate is made with a trailing _ and integer.
'''

# Define the HDF5 file name
hdf5_file_name = f'Configuration{MUSiC_Data[0]}.h5'
# Check if the file already exists
count = 1
while os.path.isfile(hdf5_file_name):
    # If the file exists, append a number to the end of the filename
    hdf5_file_name = f'Configuration{MUSiC_Data[0]}_{count}.h5'
    count += 1
# Create or open the HDF5 file in append mode
with h5py.File(hdf5_file_name, 'a'):
    pass  # Create the HDF5 file if it doesn't exist

print(f'{hdf5_file_name} created!')

'''
This is where the results are created. The chunks are added to a for loop and
processed into a histogram. The histogram is then operated on within process 
chunks, and the variables for PSD are appended. The results are written to 
the HDF5 file.
'''

# Process chunks and get results
for chunk_index, chunk_data in enumerate(chunks):
    result = process_chunk(chunk_index, chunk_data, dwell_time_ms, nperseg_m)
    write_chunk_to_hdf5(result, dwell_time_ms, hdf5_file_name)
   

# Stop the timer
end_time = time.time()
# Calculate and print the elapsed time in hh:mm:ss format
elapsed_time = end_time - start_time
formatted_elapsed_time = format_time(elapsed_time)
print(f"Elapsed time: {formatted_elapsed_time}")