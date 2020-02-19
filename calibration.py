import argparse
import re
import socket
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup


def main(args):
    soup = None
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((args.server, int(args.port)))  # Gazepoint server
    except ConnectionRefusedError:
        print("ERROR: Connection refused by the server at " + args.server + ":" + str(args.port) + " or the server did not exist.\
                Please make sure to run Gazepoint software properly.")
    else:
        calibration_command = '<SET ID="CALIBRATE_SHOW" STATE="1" />\r\n' \
                        '<SET ID="CALIBRATE_START" STATE="1" />\r\n'
        client.sendall(calibration_command.encode('utf-8'))  # send calibration command to Gazepoint
        while True:
            from_server = client.recv(2203, socket.MSG_WAITALL)  # receive 2203 bytes data for 9 points calibration
            print(from_server)
            soup = BeautifulSoup(from_server, 'html.parser')
            soup = soup.find('cal', {"id": re.compile(r'calib_result\b', re.IGNORECASE)})
            if soup is not None:
                client.close()
                break

    try:
        calib_result = np.array(
            [[soup['rx1'], soup['rx2'], soup['rx3'], soup['rx4'], soup['rx5'], soup['rx6'], soup['rx7'],
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
    else:
        df = pd.DataFrame(np.transpose(calib_result),
                          columns=['R_GAZE_X', 'R_GAZE_Y', 'L_GAZE_X', 'L_GAZE_Y', 'CAL_X', 'CAL_Y']).astype(float)
        df[['R_GAZE_X', 'L_GAZE_X', 'CAL_X']] = df[['R_GAZE_X', 'L_GAZE_X', 'CAL_X']] * args.screen_width
        df[['R_GAZE_Y', 'L_GAZE_Y', 'CAL_Y']] = df[['R_GAZE_Y', 'L_GAZE_Y', 'CAL_Y']] * args.screen_height
        df['GAZE_X'] = (df['R_GAZE_X'] + df['L_GAZE_X']) / 2
        df['GAZE_Y'] = (df['R_GAZE_Y'] + df['L_GAZE_Y']) / 2
        df = df.round(0).astype(int)
        df = df.drop(['R_GAZE_X', 'R_GAZE_Y', 'L_GAZE_X', 'L_GAZE_Y'], 1)
        df = df[['GAZE_X', 'GAZE_Y', 'CAL_X', 'CAL_Y']]
        df.to_csv('calibration_result.csv')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run Gazepoint eye tracker calibration and export the result to CSV file')
    parser.add_argument(
        '-s',
        '--server',
        help='Server address of the Gazepoint server. Default is localhost (\'127.0.0.1\').',
        default='127.0.0.1',
        required=False
    )
    parser.add_argument(
        '-p',
        '--port',
        help='Port of Gazepoint server. Default is 4242.',
        default=4242,
        type=int,
        required=False
    )
    parser.add_argument(
        '-sw',
        '--screen_width',
        help='Screen width of the calibration display in pixel. Default is 1366.',
        default=1366,
        type=int,
        required=False
    )
    parser.add_argument(
        '-sh',
        '--screen_height',
        help='Screen height of the calibration display in pixel. Default is 768.',
        default=768,
        type=int,
        required=False
    )
    args = parser.parse_args()
    main(args)
