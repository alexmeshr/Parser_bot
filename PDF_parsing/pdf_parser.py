import os
import re
import datetime

import bot_init
from PDF_parsing.Day_schedule import Day_schedule
from datetime import date, datetime, timedelta
from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from bot_init import groups, course_counts


error_list = []

def to_cyrillic(s):
    # защита от рукожопов, которые путают раскладки(Да не бомбит у меня)
    s = s.replace("c", "с")
    s = s.replace("e", "е")
    s = s.replace("y", "у")
    s = s.replace("a", "а")
    s = s.replace("x", "х")
    s = ''.join(filter(str.isalpha, s))
    return s


def to_standard(s):
    # защита от еще больших рукожопов.
    s = s.replace("C", "С")
    s = s.replace("T", "Т")
    s = s.replace("B", "В")
    s = s.replace("M", "М")
    s = s.replace(" ", "")
    return s

def find_date(s):
    # сраные рукожопы.
    m = re.search(r"\d", s)
    if m:
        return s[m.start():]
    else:
        return None


def find_time(s):
    f = re.search(r"[0-9]+.[0-9]+", s)
    s = f[0] if f is not None else  ""
    return s

def find_column_boxes(objects, arrays_of_groups, days, course_counts):
    cnt = 0
    to_del = []
    course, day, day_box, date_str = 0, None, None, None
    group_boxes = {}
    t_objects = iter(objects)
    for obj in t_objects:
        if course is None:
                word = to_standard(objects[obj])
                if word in arrays_of_groups:
                    course = 0 if arrays_of_groups.index(word)<= course_counts[0] else 1
                    cnt += 1
                    group_boxes[word] = obj
                    to_del.append(obj)
                elif to_standard(objects[obj].split()[-1]) in arrays_of_groups:
                    word = to_standard(objects[obj].split()[-1])
                    course = 0 if arrays_of_groups.index(word)<= course_counts[0] else 1
                    cnt += 1
                    group_boxes[word] = ((obj[1]+obj[0])/2, obj[1], obj[2], obj[3])
                    to_del.append(obj)
        else:
            word = to_standard(objects[obj])
            if word in arrays_of_groups:
                group_boxes[word] = obj
                cnt += 1
                to_del.append(obj)
            elif to_standard(objects[obj].split()[-1]) in arrays_of_groups:
                cnt += 1
                group_boxes[to_standard(objects[obj].split()[-1])] = ((obj[1] + obj[0]) / 2, obj[1], obj[2], obj[3])
                to_del.append(obj)

        if day is None:
            word = to_cyrillic(objects[obj].split()[0].lower())
            if word in days:
                day = word
                day_box = obj
                if len(objects[obj].split()) > 1:
                    date_str = objects[obj].split()[1]
                else:
                    if find_date(objects[obj].split()[0].lower()) is None:
                        date_box = next(t_objects, None)
                        date_str = objects[date_box]
                    else:
                        date_str = find_date(objects[obj].split()[0].lower())
                cnt += 1
            else:
                for d in days:
                    if d.find(word) == 0 and len(word) > 3:
                        end = objects[next(t_objects, None)]
                        #print(objects[obj].lower()+end.split()[0], objects[obj].lower(), end.split()[0], end.split()[1])
                        if word+end.split()[0] in days:
                            day = word+end.split()[0]
                            day_box = obj
                            date_str = end.split()[1]
                            cnt += 1
                            break
        if cnt == course_counts[course]+1:
            for k in to_del:
                objects.pop(k, None)
            return group_boxes, day_box, day, date_str, course, False
    for k in to_del:
        objects.pop(k, None)
    return group_boxes, day_box, day, date_str, course, True


def set_col_coords(day_box, group_boxes, groups):
    coords = [[day_box[0], day_box[1]]]
    for _ in range(len(groups)):
        coords.append([0, 0])
    for idx, g in enumerate(groups):
        if g in group_boxes:
            coords[idx+1][0] = group_boxes[g][0]
            coords[idx][1] = group_boxes[g][0]
        else:
            prev = group_boxes[groups[idx-1]][0] if idx > 0 else day_box[0]
            next = group_boxes[groups[idx+1]][0] if idx < len(groups)-1 else 10000
            med = (prev + next)/2
            coords[idx + 1][0] = med
            coords[idx][1] = med
    coords[-1][1]=10000
    return coords


def parse_columns(col_coords, groups, objects):
    columns = {"times": []}
    for g in groups:
        columns[g] = []
    for obj in objects:
        for idx, (x1, x2) in enumerate(col_coords):
            if obj[0]>= x1 and obj[0]<=x2 or obj[1]>= x1 and obj[1]<=x2:
                col = "times"
                if idx > 0:
                    col = groups[idx-1]
                columns[col].append([objects[obj], obj[0], obj[1], obj[2], obj[3]])
    return columns


def set_row_coords(column, times):
    time_boxes = {t:[0] for t in times}
    for r in column:
        for t in times:
            str = find_time(r[0])
            if str in t and len(str)>=4:
                time_boxes[t].extend([r[3], r[4]])
    for t in time_boxes:
        if len(time_boxes[t]) == 0:
            prev = max(time_boxes[times[times.index(t)-1]]) if times.index(t)>0 else 1000
            next = max(time_boxes[times[times.index(t)+1]]) if times.index(t)<len(times)-1 else 0
            coord = (prev+next)/2
            time_boxes[t].append(coord)
    coords = [max(time_boxes[t]) for t in time_boxes]
    coords.append(0)
    row_coords = [(coords[i], coords[i+1]) for i in range(len(coords)-1)]
    return row_coords


def create_schedule(columns, times, row_coords, delta=2):
    schedule = {}
    columns.pop("times", None)
    for c in columns:
        schedule[c] = {t:[] for t in times}
        for idx, t in enumerate(times):
            for obj in columns[c]:
                if obj[4]-delta<=row_coords[idx][0] and obj[3]+delta>=row_coords[idx][1]:
                    schedule[c][t].append(obj)
        for t in times:
            schedule[c][t].sort(key=lambda x: -x[3])
            for i in range(len(schedule[c][t])-1):
                if schedule[c][t][i][3]==schedule[c][t][i+1][4]:
                    schedule[c][t][i], schedule[c][t][i+1] = schedule[c][t][i+1], schedule[c][t][i]
    return schedule


def parse_pdf(nearest_scedule, file, groups, logging=False):
    days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
    times = [t.replace("-", "").replace(" ", "") for t in bot_init.times]
        #["09.0010.35", "10.4512.20", "12.3014.05", "15.0016.35", "16.4518.20", "18.3020.05"]
    fp = open(file, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)
    pgnum = 0
    for page in pages:
        objects = {}
        interpreter.process_page(page)
        layout = device.get_result()
        for lobj in layout:
            if isinstance(lobj, LTTextBox):
                x1,y1, x2,y2, text = lobj.bbox[0],lobj.bbox[1],lobj.bbox[2], lobj.bbox[3], lobj.get_text()
                lines = list(filter(None, text.split('\n')))
                if len(lines) > 1:
                    all_height = y2-y1
                    i_height = all_height/len(lines)
                    for i in range(len(lines)):
                        #print('     At %r is text: %s' % ((x1, x2, y1+i*(i_height), y1+(i+1)*(i_height)), lines[i]))
                        objects[(x1, x2, y1+i*(i_height), y1+(i+1)*(i_height))] = lines[i]
                else:
                    objects[(x1, x2, y1, y2)] = lines[0]
        group_boxes, day_box, day, date_str, course, error_c = find_column_boxes(objects, groups, days, course_counts)
        g_start = 0 if course==0 else sum(course_counts[i] for i in range(course))
        cur_groups = groups[g_start:g_start+course_counts[course]]
        #time_boxes, error_r = find_row_boxes(objects, times)
        if logging:
            for obj in group_boxes:
                print(obj, group_boxes[obj])
            print(day_box, day, "\n", date, "\n")
        if error_c:# or error_r:
            global error_list
            error_list.append(file+" " + str(pgnum)+" c" if error_c else " r")
        columns = None
        pgnum += 1
        col_coords=[]
        if date is not None:
            d, m = [int(x) for x in date_str.split('.')]
            y = datetime.now().year if m >= datetime.now().month else datetime.now().year + 1
            td = date(y, m, d)
            if td.timetuple().tm_yday not in nearest_scedule: #надо будет починить, не сработает для предъянварских дней
                print("passed")
                continue
            col_coords = set_col_coords(day_box, group_boxes, cur_groups)
            columns = parse_columns(col_coords, cur_groups, objects)
            row_coords = set_row_coords(columns["times"], times)
            schedule = create_schedule(columns, times, row_coords)
            nearest_scedule[td.timetuple().tm_yday] = schedule


if __name__ == "__main__":
    print("11.3 - 34.6")
    #file = "./pdf_files/file_10.pdf"
    #parse_pdf(file, groups, days, logging=False)
    nearest_scedule = {(datetime.today().timetuple().tm_yday + i): [] for i in range(14-datetime.today().weekday())}
    for f in os.listdir("./pdf_files/"):
        print(f)
        parse_pdf(nearest_scedule, "./pdf_files/"+f, groups, logging=False)
    print(error_list)

"""
At (156.9, 359.4870000000001, 334.003, 348.413) is text: Методы численного решения уравнений
At (199.9, 316.53299999999996, 321.303, 335.713) is text: гиперболического типа
At (217.7, 298.89099999999996, 296.003, 322.827) is text: В.М. Головизнин аудитория - 3047

At (563.6, 804.8629999999999, 334.003, 348.413) is text: Встреча с научными руководителями ВНИИЭФ

At (62.6, 125.443, 334.003, 373.927) is text: понедельник 
04.09
09.00 – 10.35
10.45 – 12.20
12.30 – 14.05
15.00 – 16.35
16.45 – 18.20
18.30 - 20.05
"""

