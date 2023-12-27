import glob
import os

def write_cachefile(cache_dir, data):
    pass

def generate(master_dir, from_time, to_time, cache_dir_fullpath):

    timeframes = []

    # read files
    files = glob.glob(master_dir + "/*.txt"):
    print(files)

    for fname in files:

        start = None
        end = None
        data = []

        # read file
        with open(fname) as f:
            first_line = True

            # iterate through csv #
            for line in f:

                # skip header
                if first_line:
                    first_line = False
                    continue

                # read the line #
                station_id, fulldate, dunno, temp, hum, dunno2 = line.split(";")

                # parse date #
                date = datetime.datetime.strptime(fulldate, "%y%m%d%H")

                # set start and end #
                if not start and date:
                    start = date
                elif date:
                    end = date

        # save values #
        timeframes.append((start, end, data))

    # find a fitting frame #
    for start, end, data in timeframes:
        if from_time >= start and to_time <= end:
            write_cachefile(cache_dir_fullpath, data)
            return

    raise ValueError("Keine Datei mit passenden Daten gefunden. Bitte Readme lesen")


    # generate a correct cache file from it return
    # if no suiteable file is found return an appropriate error
