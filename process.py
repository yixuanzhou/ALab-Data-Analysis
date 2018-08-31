import numpy as np

def readlvm(filename):
    """ Base lvm reader. Should be called from ``read``, only
    :param filename: filename of the lvm file
    :return lvm_data: lvm dict
    """
    lvm_data = dict()
    lvm_data['Decimal_Separator'] = '.'
    f = open(filename, 'r')
    data_channels_comment_reading = False
    data_reading = False
    segment = None
    first_column = 0
    nr_of_columns = 0
    segment_nr = 0
    for line in f:
        line = line.replace('\r', '')
        line_sp = line.replace('\n', '').split('\t')
        if line_sp[0] in ['***End_of_Header***', 'LabVIEW Measurement']:
            continue
        elif line in ['\n', '\t\n']:
            # segment finished, new segment follows
            segment = dict()
            lvm_data[segment_nr] = segment
            data_reading = False
            segment_nr += 1
            continue
        elif data_reading:#this was moved up, to speed up the reading
            seg_data.append([float(a.replace(lvm_data['Decimal_Separator'], '.') if a else 'NaN') for a in
                             line_sp[first_column:(nr_of_columns + 1)]])
        elif segment==None:
            if len(line_sp) is 2:
                key, value = line_sp
                lvm_data[key] = value
        elif segment!=None:
            if line_sp[0] == 'Channels':
                key, value = line_sp[:2]
                nr_of_columns = len(line_sp)-1
                segment[key] = eval(value)
                if nr_of_columns<segment['Channels']:
                    nr_of_columns = segment['Channels']
                data_channels_comment_reading = True
            elif line_sp[0] == 'X_Value':
                seg_data = []
                segment['data'] = seg_data
                if lvm_data['X_Columns'] == 'No':
                    first_column = 1
                segment['Channel names'] = line_sp[first_column:(nr_of_columns + 1)]
                data_channels_comment_reading = False
                data_reading = True
            elif data_channels_comment_reading:
                key, values = line_sp[0], line_sp[1:(nr_of_columns + 1)]
                if key in ['Delta_X', 'X0', 'Samples']:
                    segment[key] = [eval(val.replace(lvm_data['Decimal_Separator'], '.')) if val else np.nan for val in values]
                else:
                    segment[key] = values
            elif len(line_sp) is 2:
                key, value = line_sp
                segment[key] = value

    if not lvm_data[segment_nr-1]:
        del lvm_data[segment_nr-1]
        segment_nr -= 1
    lvm_data['Segments'] = segment_nr
    for s in range(segment_nr):
        lvm_data[s]['data'] = np.asarray(lvm_data[s]['data'])
    f.close()
    
    return lvm_data[s]['data']