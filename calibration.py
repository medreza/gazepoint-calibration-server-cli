from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import socket

screen_width = 1366
screen_height = 768

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 4242))  # Gazepoint server
except ConnectionRefusedError:
    print("ERROR: Connection refused by the server or the server did not exist.\
            Please make sure to run Gazepoint software properly.")
while True:
    from_server = client.recv(2124, socket.MSG_WAITALL)  # receive 2124 bytes data for 9 points calibration
    print(from_server)
    soup = BeautifulSoup(from_server, 'html.parser')
    soup = soup.find('cal', {"id": re.compile(r'calib_result\b', re.IGNORECASE)})
    if soup is not None:
        client.close()
        break

try:
    calib_result = np.array([[soup['rx1'], soup['rx2'], soup['rx3'], soup['rx4'], soup['rx5'], soup['rx6'], soup['rx7'],
                              soup['rx8'], soup['rx9']],
                             [soup['ry1'], soup['ry2'], soup['ry3'], soup['ry4'], soup['ry5'], soup['ry6'], soup['ry7'],
                              soup['ry8'], soup['ry9']],
                             [soup['lx1'], soup['lx2'], soup['lx3'], soup['lx4'], soup['lx5'], soup['lx6'], soup['lx7'],
                              soup['lx8'], soup['lx9']],
                             [soup['ly1'], soup['ly2'], soup['ly3'], soup['ly4'], soup['ly5'], soup['ly6'], soup['ly7'],
                              soup['ly8'], soup['ly9']],
                             [soup['calx1'], soup['calx2'], soup['calx3'], soup['calx4'], soup['calx5'], soup['calx6'],
                              soup['calx7'], soup['calx8'], soup['calx9']],
                             [soup['caly1'], soup['caly2'], soup['caly3'], soup['caly4'], soup['caly5'], soup['caly6'],
                              soup['caly7'], soup['caly8'], soup['caly9']]])
except NameError:
    print("ERROR: Some results are missing. Make sure to use 9 points calibration \
            and do not close the calibration window while it's still running.")

df = pd.DataFrame(np.transpose(calib_result),
                  columns=['R_GAZE_X', 'R_GAZE_Y', 'L_GAZE_X', 'L_GAZE_Y', 'CAL_X', 'CAL_Y']).astype(float)
df[['R_GAZE_X', 'L_GAZE_X', 'CAL_X']] = df[['R_GAZE_X', 'L_GAZE_X', 'CAL_X']] * screen_width
df[['R_GAZE_Y', 'L_GAZE_Y', 'CAL_Y']] = df[['R_GAZE_Y', 'L_GAZE_Y', 'CAL_Y']] * screen_height
df['GAZE_X'] = (df['R_GAZE_X'] + df['L_GAZE_X']) / 2
df['GAZE_Y'] = (df['R_GAZE_Y'] + df['L_GAZE_Y']) / 2
df = df.round(0).astype(int)
df = df.drop(['R_GAZE_X', 'R_GAZE_Y', 'L_GAZE_X', 'L_GAZE_Y'], 1)
df = df[['GAZE_X', 'GAZE_Y', 'CAL_X', 'CAL_Y']]
df.to_csv('calibration_result.csv')
