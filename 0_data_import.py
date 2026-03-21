from re import search
from settings import OBSIDIAN_VAULT_PATH, DATA_OUTPUT_CSV

folder_path = OBSIDIAN_VAULT_PATH
md_files = list(folder_path.glob("*.md"))[2:]

# high school: md_files[0].name - 2024-07-24.md
# summer:      2024-07-25.md    - 2024-09-18.md
# college:     2024-10-07.md    - md_files[-1].name
# sleep tracking from 2024-04-24.md

date_i = "2024-10-07.md"
date_f = md_files[-2].name

data_dict = {}
for file in md_files:
    if date_i <= file.name <= date_f:  # data analysis range
        dictionary = {}

        with file.open('r', encoding='utf-8') as file_in:
            found_r = False
            found_m = False
            for line in file_in:

                match = search(r"week: (\d{4})-W(\d{2})", line)
                if match:
                    dictionary["week"] = int(match.group(2))

                match = search(r"day: (Mon|Tue|Wed|Thu|Fri|Sat|Sun)", line)
                if match:
                    dictionary["day"] = match.group(1)

                match = search(r'youtube: "(\d+)"', line)
                if match:
                    dictionary["yt"] = int(match.group(1))

                match = search(r'sleep: "(\d+)"', line)
                if match:
                    dictionary["sleep"] = int(match.group(1))

                match = search(r"reading:\s*(true||false)", line)
                if match:
                    found_r = True
                    if match.group(1) == "true":
                        dictionary["read"] = 1
                    else:
                        dictionary["read"] = 0
                if not found_r:
                    dictionary["read"] = 0

                match = search(r"music:\s*(true||false)", line)
                if match:
                    found_m = True
                    if match.group(1) == "true":
                        dictionary["music"] = 1
                    else:
                        dictionary["music"] = 0
                if not found_m:
                    dictionary["music"] = 0

                match = search(r'study deficit: "(\d)"', line)
                if match:
                    dictionary["sd"] = int(match.group(1))

                if file.name >= "2024-10-07.md":
                    # the template exists from before,
                    # but the actual tracking starts from 2024-10-07
                    match = search(r"Completion:: (\d+)/(\d+)", line)
                    if match:
                        dictionary["compl"] = int(match.group(1))
                        dictionary["tasks"] = int(match.group(2))

                # deprecated
                match = search(r"homework:\s*(true||false)", line)
                if match:
                    if match.group(1) == "true":
                        dictionary["hwork"] = 1
                    else:
                        dictionary["hwork"] = 0

                match = search(r"info:\s*(true||false)", line)
                if match:
                    if match.group(1) == "true":
                        dictionary["info"] = 1
                    else:
                        dictionary["info"] = 0

                match = search(r"edu:\s*(true||false)", line)
                if match:
                    if match.group(1) == "true":
                        dictionary["edu"] = 1
                    else:
                        dictionary["edu"] = 0

                match = search(r"order:\s*(true||false)", line)
                if match:
                    if match.group(1) == "true":
                        dictionary["order"] = 1
                    else:
                        dictionary["order"] = 0

                match = search(r"gym:\s*(true||false)", line)
                if match:
                    if match.group(1) == "true":
                        dictionary["gym"] = 1
                    else:
                        dictionary["gym"] = 0

                match = search(r"swimming:\s*(true||false)", line)
                if match:
                    if match.group(1) == "true":
                        dictionary["swim"] = 1
                    else:
                        dictionary["swim"] = 0

        data_dict[file.name[:10]] = dictionary

keys = ["week", "day", "yt", "sleep", "read", "music", "sd", "compl", "tasks"]
# ,"hwork", "info", "edu", "order", "gym", "swim"] #deprecated, these are optional

with open(DATA_OUTPUT_CSV, "w+") as file_out:
    file_out.write("date,")
    file_out.write(f"{",".join(keys)}\n")

    for day, dictionary in data_dict.items():
        file_out.write(f"{day},")
        values = []
        for key in keys:
            try:
                values.append(str(dictionary[key]))
            except KeyError:
                values.append("/")
        file_out.write(f"{",".join(values)}\n")
    print("data successfully imported!")
