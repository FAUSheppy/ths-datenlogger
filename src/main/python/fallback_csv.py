import glob
import datetime
import os

SKIP_LINES = 13

def cache_content(from_time, to_time, data, dtype):

    return_string = ""

    skip_count = 0

    for i in range(0, SKIP_LINES):
        return_string += "\n"

    for d in data:

        date, temp, hum = d

        # skip outside timeframe #
        if date < from_time or date > to_time:
            continue

        if dtype == "lufttemperatur-aussen":
            content_number = temp
        elif dtype == "luftfeuchte":
            content_number = hum
        else:
            raise ValueError("Bad dtype: {}".format(dtype))

        date_cache_format = date.strftime("%d.%m.%Y %H:%M")
        content_str = "{:1f}".format(content_number).replace(".",",")
        return_string += "{};{}\n".format(date_cache_format, content_str)

    return return_string

def generate(master_dir, from_time, to_time, cache_file, dtype):

    timeframes = []

    if not os.path.isdir(master_dir):
        os.mkdir(master_dir)

    # read files
    files = glob.glob(master_dir + "/produkt_tu_stunde*.txt")

    if not files:
        raise ValueError("Keine DWD_Datei in: {} gefunden. Bitte herunterladen und entpacken! https://www.dwd.de/DE/leistungen/klimadatendeutschland/klarchivstunden.html;jsessionid=C423E76B30D18F24C43F4E7E36744C8C.live21073?nn=16102")

    info_for_output_if_error = []

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
                date = datetime.datetime.strptime(fulldate, "%Y%m%d%H")

                # append data #
                data.append((date, float(temp), float(hum)))

                # set start and end #
                if "tu" in fname:
                    print(line, date)
                if not start and date:
                    start = date
                elif date:
                    end = date
                    if "tu" in fname:
                        print(end)

        # save values #
        timeframes.append((start, end, data))
        info_for_output_if_error.append("{}\n{} bis {}".format(fname, start, end))

    # find a fitting frame #
    for start, end, data in timeframes:
        if from_time >= start and to_time <= end:
            return cache_content(from_time, to_time, data, dtype)

    raise ValueError("Keine Datei mit passenden Daten gefunden. Bitte Readme lesen.\n\n" +
                        "Zeiträume gefunden:\n" +
                        "\n\n".join(info_for_output_if_error) +
                        "\nZeitraum benötigt:\n" + "{} bis {}".format(from_time, to_time))
