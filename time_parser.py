#!/usr/bin/env python

# import everything needed
import yaml
import datetime
import argparse
from matplotlib.dates import date2num
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

def main():
    # declare things needed
    calendar = []
    all_activities = []    
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type = str, help = "string to yaml file to be parsed")
    parser.add_argument("-pd", "--print_daily", type = bool, help = "flag to print the daily log")
    parser.add_argument("-pt", "--print_totals", type = bool, help = "flag to print the totals of every activity")
    parser.add_argument("-pw", "--print_weekly", type = bool, help = "flag to print the week totals")
    parser.add_argument("-py", "--print_yearly", type = bool, help = "flag to print the yearly totals")
    parser.add_argument("-pa", "--print_totals_average", type = bool, help = "flag to print the daily averages")
    parser.add_argument("-ptt", "--plot_totals", type = bool, help = "flag to plot the total summary in a pie graph")
    parser.add_argument("-ptd", "--plot_daily", type = bool, help = "flag to plot the daily summary over time in line graph")
    args = parser.parse_args()
    if args.file == None:
        args.file = "time.yaml"
    calendar, all_activities = put_everything_in_a_list_of_dicts(args.file, calendar, all_activities)

    if args.print_daily: #or args.plot_daily:
        print_daily(calendar, args.plot_daily)
    if args.print_weekly:
        print_weekly(calendar)
    # print_monthly()
    if args.print_totals or args.print_totals_average or args.plot_totals:
        print_totals(calendar, args.print_totals_average, args.plot_totals)
    
    if args.plot_daily:
        plot_daily(calendar, all_activities)
    # plot_weekly()
    # plot_monthly()
    # plot_totals()

def put_everything_in_a_list_of_dicts(file, calendar, all_activities):

    # open the yaml
    with open(file, 'r') as stream:
        
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
                    # get all the activities ever done, needed to make plotting easier
                    if activity not in all_activities:
                        all_activities.append(activity)

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

    return calendar, all_activities

def print_daily(calendar, plot_daily):
    print("\tDAILY SUMMARY")

    # every day, want to go through reversed so the most recent day is printed last
    for day in reversed(calendar):
        unsorted_daily_duration = {}
        
        # every activity and time in each day
        for activity, times in day.items():
            
            # if it's a date, it's not going to have a time associated
            if activity == 'Date':

                # add the weekly dict totals to a list and reset 
                print("\t{}   {}".format(activity, times))            

            # the rest of the dict elements all have a start, stop, and duration time
            else:

                # save the duration of each activity to be sorted later
                unsorted_daily_duration[activity] = times['duration']
    
        sorted_daily_duration = sorted(unsorted_daily_duration.items(), key=lambda kv: kv[1], reverse = True)
        for element in sorted_daily_duration:
            print("{}     \t\t\t{}".format(element[0], element[1]))
        print("\n")

def print_weekly(calendar):
    print("\tWEEKLY TOTALS")
    unsorted_weekly_duration = {}
    list_of_unsorted_weekly_duration = []

    # every day, want to go through reversed so the most recent day is printed last
    for day in reversed(calendar):
        
        # every activity and time in each day
        for activity, times in day.items():
            
            # if it's a date, it's not going to have a time associated
            if activity == 'Date':
                if times.weekday() == 0:
                    list_of_unsorted_weekly_duration.append(unsorted_weekly_duration.copy())
                    unsorted_weekly_duration = {}

                    # add the weekly dict totals to a list and reset 
                    print("\t{}   {}".format(activity, times))            

            # the rest of the dict elements all have a start, stop, and duration time
            else:

                # to help add up the totals of every activity, add it to the dict
                if activity not in unsorted_weekly_duration:
                    unsorted_weekly_duration[activity] = datetime.timedelta(0)

                unsorted_weekly_duration[activity] += times['duration']


    for week in list_of_unsorted_weekly_duration:
        sorted_weekly_duration = sorted(week.items(), key=lambda kv: kv[1], reverse = True)
    for element in sorted_weekly_duration:
        print("{}     \t\t\t{}".format(element[0], element[1]))
    print("\n")

def print_totals(calendar, average, plot_totals):
    print("\tTOTAL TIME SUMMARY")

    totals = {}

    # every day, want to go through reversed so the most recent day is printed last
    for day in reversed(calendar):
        
        # every activity and time in each day
        for activity, times in day.items():
            
            # # if it's a date, it's not going to have a time associated
            if activity == 'Date':
                pass

            # the rest of the dict elements all have a start, stop, and duration time
            else:

                # to help add up the totals of every activity, add it to the dict
                if activity not in totals:
                    totals[activity] = datetime.timedelta(0)

                # save the duration of each activity to be sorted later
                totals[activity] += times['duration']
    
    # sort the totals dict
    sorted_totals = sorted(totals.items(), key=lambda kv: kv[1], reverse = True)

    # print out the totals for each activity
    for active in sorted_totals:
        print("{}     \t\t {}".format(active[0], active[1]))

    # print out the average for each activity over the total number of days
    if average:
        print("\tAVERAGE TIME PER 7 DAYS")
        for active in sorted_totals:
            print("{}     \t\t {}".format(active[0], active[1]/len(calendar)))

    if plot_totals:
        labels = totals.keys()
        del totals['Sleep']
        del totals['Work']        
        durations = [time.total_seconds()/3600.0 for time in totals.values()]
        socials_index = list(totals.keys()).index('Socials')
        explode = []
        for i in range(len(durations)):
            explode.append(0) if i != socials_index else explode.append(0.1)

        fig1, ax1 = plt.subplots()
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        ax1.pie(durations, explode=explode, labels=labels, autopct='%1.0f%%')

        plt.show()

def plot_daily(calendar, all_activities):

    x_axis = []
    unsorted_daily_duration = {}
    all_durations = np.zeros((len(all_activities), len(calendar)))

    # every day, want to go through reversed so the most recent day is printed last
    for i, day in enumerate(reversed(calendar)):
        
        # every activity and time in each day
        for activity, times in day.items():

            # if it's a date, it's not going to have a time associated
            if activity == 'Date':
                x_axis.append(date2num(times))

            # the rest of the dict elements all have a start, stop, and duration time
            else:
                all_durations[all_activities.index(activity),i] = times['duration'].total_seconds()/3600                

    for i, row in enumerate(all_durations):
        plt.plot(x_axis, row, label = all_activities[i])
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%a %m/%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()
    plt.show()
# # TODO:
# #   tally monthly, yearly totals   

if __name__ == '__main__':
    main()