#!/usr/bin/env python

# import everything needed
import yaml
import datetime
import argparse
from matplotlib.dates import date2num

# declare things needed
calendar = []
number_of_days = 0

# parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", type = str, help = "string to yaml file to be parsed")
parser.add_argument("-pd", "--print_daily", type = bool, help = "flag to print the daily log")
parser.add_argument("-pt", "--print_totals", type = bool, help = "flag to print the totals of every activity")
parser.add_argument("-pw", "--print_weekly", type = bool, help = "flag to print the week totals")
parser.add_argument("-py", "--print_yearly", type = bool, help = "flag to print the yearly totals")
parser.add_argument("-pa", "--print_totals_average", type = bool, help = "flag to print the daily averages")
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
                date = datetime.datetime(year, month, day, 0, 0, 0)
                
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
        number_of_days += 1

totals = {}
unsorted_weekly_duration = {}
list_of_unsorted_weekly_duration = []

# every day 
for day in reversed(calendar):
    unsorted_daily_duration = {}
    
    # every activity and time in each day
    for activity, times in day.items():
        
        # if it's a date, it's not going to have a time associated
        if activity == 'Date':
            if times.weekday() == 0:
                print(times.weekday())
                list_of_unsorted_weekly_duration.append(unsorted_weekly_duration.copy())
                unsorted_weekly_duration = {}

            # add the weekly dict totals to a list and reset 
            if args.print_daily:
                print("\t{}   {}".format(activity, times))            
        # the rest of the dict elements all have a start, stop, and duration time
        else:
            # to help add up the totals of every activity, add it to the dict
            if activity not in totals:
                totals[activity] = datetime.timedelta(0)
            if activity not in unsorted_weekly_duration:
                unsorted_weekly_duration[activity] = datetime.timedelta(0)
            # iterate over each activitys start, stop, and duration
            for description, time in times.items():
                
                # if it's duration, add it to a daily dictionary to later be sorted
                # easier to see everything sorted
                # also add it to the totals dict to be totaled and sorted later
                if description == 'duration':
                    unsorted_daily_duration[activity] = time
                    unsorted_weekly_duration[activity] += time
                    totals[activity] += time
                # print(unsorted_weekly_duration)
    if args.print_daily:
        sorted_daily_duration = sorted(unsorted_daily_duration.items(), key=lambda kv: kv[1], reverse = True)
        for element in sorted_daily_duration:
            print("{}     \t\t\t{}".format(element[0], element[1]))
        print("\n")
if args.print_weekly:
    # print(list_of_unsorted_weekly_duration)
    for week in list_of_unsorted_weekly_duration:
        sorted_weekly_duration = sorted(week.items(), key=lambda kv: kv[1], reverse = True)
    for element in sorted_weekly_duration:
        print("{}     \t\t\t{}".format(element[0], element[1]))
    print("\n")

sorted_totals = sorted(totals.items(), key=lambda kv: kv[1], reverse = True)
if args.print_totals:

    # hours = datetime.timedelta(0)
    # list_of_activities = []
    # list_of_times = []

    for active in sorted_totals:
        print("{}     \t\t {}".format(active[0], active[1]))

        # list_of_activities.append(active[0])
        # list_of_times.append(active[1])
        # hours += active[1]
    # print(list_of_times)
    # list_of_times = date2num(list_of_times)
    # matplotlib.pyplot.plot_date(list_of_times, list_of_activities)
    # print(number_of_days)
    # print(hours)
    # for activity, time_duration in totals.items():
        # print(activity, time_duration)
if args.print_totals_average:
    for active in sorted_totals:
        print("{}     \t\t {}".format(active[0], active[1]/number_of_days))
# TODO:
#   tally weekly, monthly, yearly totals   
#   sort daily by duration