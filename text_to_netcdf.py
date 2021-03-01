import netCDF4 as nc
import numpy as np
import argparse


def proceeding_zero(x):
    if len(x) == 1:
        return f'0{x}'
    else:
        return x
    

def info_from_file(infofile):
    info = [x.rstrip() for x in open(infofile).readlines()]
    for i, inf in enumerate(info):
        infr = inf.replace(',','')
        j = infr.split()
        if 'lon' in j:
            if 'lon' == j[2]:
                lon = float(j[0])
                lat = float(j[1])
            else:
                msg = f'Unexpected structure in line {i}'
                raise ValueError(msg)
        elif 'range' in j:
            continue 
        elif 'dx' in j:
            if 'dx' == j[3] and 'dy' == j[4] and 'dz' == j[5]:
                if '(km)' == j[6]:
                    dx = float(j[0]) * 1000
                    dy = float(j[1]) * 1000
                    dz = float(j[2]) * 1000
                elif '(m)' == j[6]:
                    dx = float(j[0])
                    dy = float(j[1])
                    dz = float(j[2])
                else:
                    msg = f'Unexpected structure in line {i}'
                    raise ValueError(msg)
            else:
                msg = f'Unexpected structure in line {i}'
                raise ValueError(msg)
        elif 'x' in j:
            if 'x' == j[3] and 'y' == j[4] and 'z' == j[5]:
                x = int(j[0])
                y = int(j[1])
                z = int(j[2])
            else:
                msg = f'Unexpected structure in line {i}'
                raise ValueError(msg)
        elif 'undef:' in j:
            if 'no' == j[3] and 'data' == j[4] and 'shadow' == j[5]:
                nodata = float(j[0])
                shadow = float(j[1])
            else:
                msg = f'Unexpected structure in line {i}'
                raise ValueError(msg)
        elif 'time' in j:
            if 'time' == j[6]:
                time = f'{j[0]}{proceeding_zero(j[1])}{proceeding_zero(j[2])}T{proceeding_zero(j[3])}{proceeding_zero(j[4])}{proceeding_zero(j[5])}'
            else:
                msg = f'Unexpected structure in line {i}'
                raise ValueError(msg)
        else:
            msg = f'Unexpected structure in line {i}'
            raise ValueError(msg)
    return x, y, z, dx, dy, dz, lon, lat, nodata, shadow, time
    

    
def convert_to_netcdf(textfile, outfile = None, x = 201, y = 201, z = 40, 
                      dx = 1000.0, dy = 1000.0, dz = 500.0, lon0 = 101.8330, 
                      lat0 = -3.9760, nodata = -99.0, shadow = -199.0, 
                      time = '20151123T000000'):
    # Create name for outfile if not given
    if outfile == None:
        outfile = f'{textfile[:-3]}nc'
        
    # Read data, check size, create array
    data = [x.rstrip() for x in open(textfile).readlines()]
    if (len(data) != y*z) or (len(data[0].replace('    ', ',').split(',')) != x):
        msg = "Unexpected size of data, exiting..."
        raise IOError(msg)
    data_array = np.empty((x,y,z))
    for k in range(data_array.shape[2]):
        for j in range(data_array.shape[1]):
            try:
                data_array[:,j,k] = data[j+k*data_array.shape[1]].replace('    ', ',').split(',')
            except:
                print(j,k)
                raise
            
    # Create and write netcdf file
    dataset = nc.Dataset(outfile, 'w', format='NETCDF4')
    nc_x = dataset.createDimension('x', x)
    nc_y = dataset.createDimension('y', y)
    nc_z = dataset.createDimension('z', z)

    xs = dataset.createVariable('x', 'f4', ('x',))
    ys = dataset.createVariable('y', 'f4', ('y',))
    zs = dataset.createVariable('z', 'f4', ('z',))
    reflectivity = dataset.createVariable('reflectivity', 'f4', ('x','y','z',))

    xs.units = 'm'
    ys.units = 'm'
    zs.units = 'm'
    reflectivity.units = 'dBZ'
    reflectivity.nodata = nodata
    reflectivity.shadowdata = shadow

    dataset.lon0 = lon0
    dataset.lat0 = lat0
    dataset.dx = dx
    dataset.dy = dy
    dataset.dz = dz
    dataset.time = time


    xvals = np.arange(-((x-1)/2)*dx, ((x-1)/2)*dx+0.1, dx)
    yvals = np.arange(-((y-1)/2)*dy, ((y-1)/2)*dy+0.1, dy)
    zvals = np.arange(dz, z*dz+1, dz)

    xs[:] = xvals
    ys[:] = yvals
    zs[:] = zvals
    reflectivity[:,:,:] = data_array[:,:,:]
    
    dataset.close()
    
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage = '%(prog)s textfile [options]', description = "Take text output from fortran code and convert to netcdf4 file")
    parser.add_argument("textfile", default = None, help = "Text file from output of fortran code")
    parser.add_argument("-f", "--information-file", dest = "infofile", default = None, help = "Information file with grid data from website. Not needed if grid data defined by options or matches defaults. If given, will override grid data defaults.")
    parser.add_argument("-o", "--output-file", dest = "outfile", default = None, help = "Output netcdf file. If not given, will be placed in the same location with the same name as the text file.")
    parser.add_argument("-i", "--x-grid-points", dest = "x", type = int, default = 201, help = "Number of grid points in x direction")
    parser.add_argument("-j", "--y-grid-points", dest = "y", type = int, default = 201, help = "Number of grid points in y direction")
    parser.add_argument("-k", "--z-grid-points", dest = "z", type = int, default = 40, help = "Number of grid points in z direction")
    parser.add_argument("-x", "--x-grid-space", dest = "dx", type = float, default = 1000.0, help = "Distance in x direction between grid points, metres")
    parser.add_argument("-y", "--y-grid-space", dest = "dy", type = float, default = 1000.0, help = "Distance in y direction between grid points, metres")
    parser.add_argument("-z", "--z-grid-space", dest = "dz", type = float, default = 500.0, help = "Distance in z direction between grid points, metres")
    parser.add_argument("-l", "--lon0", dest = "lon0", type = float, default = 101.8330, help = "Central longitude")
    parser.add_argument("-a", "--lat0", dest = "lat0", type = float, default = -3.9760, help = "Central latitude")
    parser.add_argument("-n", "--nodata", dest = "nodata", type = float, default = -99.0, help = "Value representing no data")
    parser.add_argument("-s", "--shadow", dest = "shadow", type = float, default = -199.0, help = "Value representing shadow data")
    parser.add_argument("-c", "--time", dest = "time", default = '20151123T000000', help = "Time in YYYYmmddTHHMMSS format")
    
    args = parser.parse_args()
    
    if args.textfile == None:
        raise ValueError("Text file with data output from fortran code must be given!")
    
    if args.infofile != None:
        args.x, args.y, args.z, args.dx, args.dy, args.dz, args.lon0, args.lat0, args.nodata, args.shadow, args.time = info_from_file(args.infofile)
        #raise NotImplementedError("Reading values from file is not yet implemented, please explicitly state grid data if different from the defaults.")
        
    if args.outfile == 'None':
        args.outfile = None
        
    convert_to_netcdf(args.textfile, outfile = args.outfile, x = args.x, y = args.y, z = args.z, dx = args.dx, dy = args.dy, dz = args.dz, lon0 = args.lon0, lat0 = args.lat0, nodata = args.nodata, shadow = args.shadow, time = args.time)
        
    