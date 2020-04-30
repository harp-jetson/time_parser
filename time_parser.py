#!/usr/bin/env python

# import everything needed
import yaml
import datetime
import argparse

# declare things needed
calendar = []

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type = str, help = "string to yaml file to be parsed")
args = parser.parse_args()
if args.file == None:
    args.file = "time.yaml"

# open the yaml
with open(args.file, 'r') as stream:
    
    # load all yaml docs
    all_days = yaml.safe_load_all(stream)
    
    # loop through each yaml doc
    for day in all_days:
        
        # reset activities for the day
        activities = {}

        # loop through each activity
        for activity, times in day.items():
            
            # date is the outlier, doesn't use time, so pick it out, it's always first anyways
            if activity == 'Date':
                month = int(times[0])
                day = int(times[1])
                year = int(times[2])+2000 
                date = datetime.date(year, month, day)
                
                # add it to the daily dictionary
                activities[activity] = date

            # if it's not date oriented, it's time related
            else: 
                activities[activity] = {}
                activities[activity]['duration'] = datetime.timedelta(0)

                # every entry has a start and stop time so we can go by twos
                for i in range(0, len(times), 2):

                    # have to convert to string to split out last two digits (minutes) of time
                    start_min = int(str(times[i])[-2:])
                    
                    # the hour time can start at 0 so there is nothing left to take, have to check for that
                    if str(times[i])[:-2] != '':
                        start_hour = int(str(times[i])[:-2])
                    else:
                        start_hour = 0 

                    # do the same thing for end time
                    end_min = int(str(times[i+1])[-2:])
                    end_hour = int(str(times[i+1])[:-2])
                    
                    # datetime doesn't accept 2400 as midnight
                    if end_hour == 24:
                        end_hour = 23
                        end_min = 59
                    
                    # convert to datetime times
                    start_time = datetime.time(start_hour, start_min, 0)
                    end_time = datetime.time(end_hour, end_min, 0)
                    
                    # have to combine dates and times to be able to subtract them
                    start_datetime = datetime.datetime.combine(activities['Date'], start_time)
                    end_datetime = datetime.datetime.combine(activities['Date'], end_time)
                    
                    # find the duration of each activity
                    activity_duration = end_datetime - start_datetime
                    start_time_key = 'start time ' + str(int(i/2+1))
                    end_time_key = 'end time ' + str(int(i/2+1))
                    # save to the daily dict
                    activities[activity][start_time_key] = start_time
                    activities[activity][end_time_key] = end_time
                    activities[activity]['duration'] += activity_duration

        # add the daily dictionary to a list
        calendar.append(activities.copy())

# print everything by day 
for day in calendar:
    for key, value in day.items():
        if key != 'Date':
            print(key)
            for key2, value2 in value.items():
                print(key2, value2)
        else:
            print(key, value)
    print("\n")

# TODO:
#   tally daily, weekly, monthly, yearly, total totals   
        