from scipy.io import loadmat
alt = loadmat('alt_landing.mat')['alt'][:, 0]
# lon = x['lon']
# lat = x['lat']
# # one-liner to read a single variable
# lon = loadmat('test.mat')['lon']
print()

# 'LineNo'
# 'TimeUS'
# 'Status'
# 'GMS'
# 'GWk'
# 'NSats'
# 'HDop'
# 'Lat'
# 'Lng'
# 'Alt'
# 'Spd'
# 'GCrs'
# 'VZ'
# 'Yaw'
# 'U'
