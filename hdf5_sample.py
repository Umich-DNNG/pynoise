    @staticmethod
    def WriteData(dataArrays, fileName, fileFormat='hdf5', metaData=None):
        """
        Save a list of numpy arrays to a file in the specified format.

        Parameters:
            dataArrays (list of np.array): List of data arrays to be written.
            fileName (str): Base name of the file to save data.
            fileFormat (str, optional): Format to save the file ('txt',
                                                                 'bin',
                                                                 'hdf5').
                                        Defaults to 'hdf5'.
            metaData (list of str or str, optional): Metadata labels for the
                                                     data arrays. Can be a
                                                     list of strings, a single
                                                     string to be applied to
                                                     all, or None to
                                                     auto-generate.
                                                     Defaults to None.

        Returns:
            None
        """
        if metaData is None:
            metaData = [f'Data_{i}' for i in range(len(dataArrays))]
        elif isinstance(metaData, str):
            metaData = [metaData] * len(dataArrays)
        elif len(metaData) != len(dataArrays):
            raise ValueError(
                "Length of metaData does not match length of dataArrays")

        if fileFormat == 'txt':
            fileName += '.txt'
            dataArray = np.column_stack(dataArrays)
            np.savetxt(fileName, dataArray, delimiter='\t')
            print(f'Data saved as {fileName} and written in .txt format.')
        elif fileFormat == 'bin':
            dataArray = np.column_stack(dataArrays)
            dataArray.tofile(fileName)
            print(f'Data saved as {fileName} and written in .bin format.')
        elif fileFormat == 'hdf5':
            fileName += '.h5'
            with h5py.File(fileName, 'w') as file:
                for i, (array, meta) in enumerate(zip(dataArrays, metaData)):
                    file.create_dataset(meta, data=array)
            print(f'Data saved as {fileName} and written in .h5 format.')
        else:
            print('Invalid format. Please use "txt", "bin", or "hdf5".')

    @staticmethod
    def ReadData(fileName, fileFormat='hdf5', metaDataKeys=None,
                 delimiter=None, numColumns=1):
        """
        Read data from a file in the specified format and return the data
        along with any metadata.

        Parameters:
            fileName (str): Name of the file to read data from.
            fileFormat (str, optional): Format of the file to read ('txt',
                                                                    'bin',
                                                                    'hdf5').
                                        Defaults to 'hdf5'.
            metaDataKeys (list of str, optional): List of metadata keys to
                                                  retrieve from the file.
                                                  Defaults to None.
            delimiter (str, optional): Delimiter used in the text file if
                                       reading 'txt' format. Defaults to None.
            numColumns(int, optional): Number of columns for binary reading.

        Returns:
            data (dict): Dictionary containing data arrays and any metadata
            retrieved from the file.
        """

        data = {}

        if fileFormat == 'txt':
            dataArray = np.loadtxt(fileName, delimiter=delimiter)
            data['arrays'] = [dataArray[:, i]
                              for i in range(dataArray.shape[1])]
        elif fileFormat == 'bin':
            dataArray = np.fromfile(fileName).reshape(-1, numColumns)
            data['arrays'] = [dataArray[:, i]
                              for i in range(dataArray.shape[1])]
        elif fileFormat == 'hdf5':
            with h5py.File(fileName, 'r') as f:
                for key in f.keys():
                    data[key] = f[key][()]

                if metaDataKeys is None:
                    dataGroup = f.get('metadata')
                    if dataGroup is not None:
                        for key, value in dataGroup.attrs.items():
                            data[key] = value
                else:
                    dataGroup = f.get('metadata')
                    if dataGroup is not None:
                        for key in metaDataKeys:
                            if key in dataGroup.attrs:
                                data[key] = dataGroup.attrs[key]
        else:
            print('Invalid format. Please use "txt", "bin", or "hdf5".')
            return None

        return data