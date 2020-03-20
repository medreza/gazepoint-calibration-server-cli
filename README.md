# gazepoint-calibration-saver
Catch Gazepoint eye tracker 9 points calibration stream results and save it to *.csv file.
## Note on Results
The default gaze points results are in screen proportion and are divided into right and left gaze. However, in this project, the right and left gaze points are unified as one gaze point by taking midpoint as the new gaze point. Results are also converted into pixel, therefore passing screen resolution is needed.
## Usage
`$ python calibration.py -s=<SERVER> -p=<PORT> -sw=<SCREEN WIDTH> -sh='<SCREEEN HEIGHT>`