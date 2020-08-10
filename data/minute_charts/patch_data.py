import os


def get_all_cvs_in_folder(path):

    path += "/"
    file_array = []

    for r, d, f in os.walk(path):
        for file in f:
            if '.csv' in file:
                file_array.append({
                    "full_path": os.path.join(r, file),
                    "root": r,
                    "file_name": file,
                    "date": path
                }
                )

    return file_array


def create_backup(files):
    for file in files:
        if ".csv.bak" not in file["file_name"]:
            if not os.path.exists(file['full_path'] + ".bak"):
                print("Backup doesn't exist for: " + file['full_path'])
                source = open(file['full_path'], "r")
                dest = open(file['full_path'] + ".bak", "w")
                for line in source:
                    dest.write(line)
                source.close()
                dest.close()
            else:
                print("Backup exists: " + file['full_path'])


def fix_dataframe_format(files):
    for file in files:
        if os.path.exists(file['full_path'] + ".bak"):
            source = open(file['full_path'] + ".bak", "r")
            dest = open(file['full_path'], "w")
            header = True
            for line in source:
                if header:
                    dest.write("date,open,close,high,low,volume\n")
                    header = False
                    continue
                if line.startswith("2020"):
                    dest.write(line)
                else:
                    tokens = line.split(",")
                    dest_line = ""
                    for i in range(1, len(tokens)):
                        dest_line += tokens[i] + ","
                    dest.write(dest_line[:-1])
            source.close()
            dest.close()


def generate_hours():

    expected_dates = {
        "09": range(30, 60),
        "10": range(0, 60),
        "11": range(0, 60),
        "12": range(0, 60),
        "13": range(0, 60),
        "14": range(0, 60),
        "15": range(0, 60),
    }

    return expected_dates


def parse_candle(candle_string):
    tokens = candle_string.split(",")
    data = {
        "date": tokens[0].strip(),
        "open": tokens[1].strip(),
        "close": tokens[2].strip(),
        "high": tokens[3].strip(),
        "low": tokens[4].strip(),
        "volume": tokens[5].strip()
    }
    return data


def candle_to_string(candle):

    return (candle["date"] + "," +
            candle["open"] + "," +
            candle["close"] + "," +
            candle["high"] + "," +
            candle["low"] + "," +
            candle["volume"]
            )


def patch_missing_candles(files):

    expected_hours = generate_hours()
    for file in files:
        if ".bak" in file['full_path']:
            continue

        print("Analysing " + file['full_path'], end="")
        header = True
        missing_hours = []
        data = []
        for hour in expected_hours:
            for min in expected_hours[hour]:
                source = open(file['full_path'], "r")
                hour_string = str(hour) + ":" + str(str(min).zfill(2)) + ":00"
                found = False
                for line in source:
                    if hour_string in line:
                        found = True
                        data.append(parse_candle(line))

                if found is False:
                    # print("Hour " + hour_string + " is missing")
                    missing_hours.append(hour_string)
                    data.append({
                        "date": file["date"][:-1] + " " + hour_string + "-04:00",
                        "open": None,
                        "close": None,
                        "high": None,
                        "low": None,
                        "volume": None,
                    })
                source.close()


        dest = open(file['full_path'], "w")
        dest.write("date,open,close,high,low,volume\n")

        for i in range(0, len(data)):
            if data[i]["open"] != None:
                dest.write(candle_to_string(data[i]) + "\n")
            else:
                if i != 0 and i != len(data) and data[i-1]["open"] != None and data[i+1]["open"] != None:
                    data[i]["open"] = data[i-1]["close"]
                    data[i]["close"] = data[i+1]["open"]

                    if float(data[i]["open"]) >= float(data[i]["close"]):
                        data[i]["high"] = data[i]["open"]
                        data[i]["low"] = data[i]["close"]
                    else:
                        data[i]["high"] = data[i]["close"]
                        data[i]["low"] = data[i]["open"]
                    data[i]["volume"] = str(int(
                        (float(data[i+1]["volume"]) + float(data[i-1]["volume"])) / 2)) + ".0"
                    dest.write(candle_to_string(data[i]) + "\n")
                else:
                    print(" ...missing first/last or consecutive elemnts ")
        dest.close()
        print(" ...fixed")
            
        # for hour in missing_hours:

        # for line in source:
        #     if header:
        #         header = False
        #         continue

        #     tokens = line.split(",")

        #     dates.append


files = get_all_cvs_in_folder("2020-07-03")
create_backup(files)
fix_dataframe_format(files)
patch_missing_candles(files)


