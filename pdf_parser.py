file = "./pdf_files/file_25.pdf"
groups = [["ВМ-123","СКТ-123","ТФ-123","ЛНОФ-123","ЭЭП-123"],["ВМ-222","СТФИ-222","ТФ-222","ЛНОФ-222","ЭЭП-222"]]
days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]


from pdfminer.layout import LAParams, LTTextBox
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
import os
import re


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


def find_column_boxes(objects, arrays_of_groups, days):
    cnt = 0
    course, day, day_box, date = None,None,None,None
    group_boxes = {}
    t_objects = iter(objects)
    for obj in t_objects:
        if course is None:
            for i in range(len(arrays_of_groups)):
                word = to_standard(objects[obj])
                if word in arrays_of_groups[i]:
                    course = i
                    cnt += 1
                    group_boxes[obj] = word
                elif to_standard(objects[obj].split()[-1]) in arrays_of_groups[i]:
                    course = i
                    cnt += 1
                    group_boxes[((obj[1]+obj[0])/2, obj[1], obj[2], obj[3])] = to_standard(objects[obj].split()[-1])
        else:
            word = to_standard(objects[obj])
            if word in arrays_of_groups[course]:
                group_boxes[obj] = word
                cnt += 1
            elif to_standard(objects[obj].split()[-1]) in arrays_of_groups[course]:
                cnt += 1
                group_boxes[((obj[1] + obj[0]) / 2, obj[1], obj[2], obj[3])] = to_standard(objects[obj].split()[-1])

        if day is None:
            word = to_cyrillic(objects[obj].split()[0].lower())
            if word in days:
                day = word
                day_box = obj
                if len(objects[obj].split()) > 1:
                    date = objects[obj].split()[1]
                else:
                    if find_date(objects[obj].split()[0].lower()) is None:
                        date_box = next(t_objects, None)
                        date = objects[date_box]
                    else:
                        date = find_date(objects[obj].split()[0].lower())
                cnt += 1
            else:
                for d in days:
                    if d.find(word) == 0 and len(word) > 3:
                        end = objects[next(t_objects, None)]
                        #print(objects[obj].lower()+end.split()[0], objects[obj].lower(), end.split()[0], end.split()[1])
                        if word+end.split()[0] in days:
                            day = word+end.split()[0]
                            day_box = obj
                            date = end.split()[1]
                            cnt += 1
                            break
        if course is not None and cnt == len(arrays_of_groups[course])+1:
            return group_boxes, day_box, day, date, course, False
    return group_boxes, day_box, day, date, course, True
    #return group_boxes, day_box, day, date, course


def parse_pdf(file, groups, days, logging=False):
    fp = open(file, 'rb')
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    pages = PDFPage.get_pages(fp)
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
        group_boxes,day_box, day, date, course, error = find_column_boxes(objects, groups, days)
        if logging:
            for obj in group_boxes:
                print(obj, group_boxes[obj])
            print(day_box, day, "\n", date, "\n")
        if error:
            raise Exception

if __name__ == "__main__":
    #"""
    for f in os.listdir("./pdf_files/"):
        print(f)
        #if f!="file_25.pdf":
        parse_pdf("./pdf_files/"+f, groups, days, logging=True)
    #"""
    #parse_pdf(file, groups, days, logging=False)
"""
At (156.9, 359.4870000000001, 334.003, 348.413) is text: Методы численного решения уравнений
At (199.9, 316.53299999999996, 321.303, 335.713) is text: гиперболического типа
At (217.7, 298.89099999999996, 296.003, 322.827) is text: В.М. Головизнин аудитория - 3047

At (563.6, 804.8629999999999, 334.003, 348.413) is text: Встреча с научными руководителями ВНИИЭФ

At (62.6, 125.443, 334.003, 373.927) is text: понедельник 
04.09
09.00 – 10.35
"""