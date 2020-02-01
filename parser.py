from bs4 import BeautifulSoup as bs
import json
import re
import requests

LINK = "https://www.reg.uci.edu/cob/prrqcgi?dept=COMPSCI&term=202003&action=view_all#112"
CATALOGUE = {}

def parse():
    result = requests.get(LINK)
    soup = bs(result.content, "lxml")
    all_course = soup.find_all("td", {"class": "course"})
    all_prereq = soup.find_all("td", {"class": "prereq"})
    course_list = [re.sub(' +', ' ', course.get_text()).strip() for course in all_course]

    prereq_list = []
    for prereq in all_prereq:
        raw_content = re.sub(' +', ' ', prereq.get_text()).strip()
        raw_content = re.sub('UPPER DIVISION STANDING ONLY', 'UPDIV', raw_content).strip()
        raw_content = re.sub('NO REPEATS ALLOWED IF GRADE = C OR BETTER', '@', raw_content).strip()
        raw_content = re.sub('\( coreq \)', '+', raw_content).strip()
        raw_content = re.sub('\( recommended \)', '*', raw_content).strip()
        tokens = raw_content.split("AND")
        tokens = [token.strip("\n") for token in tokens if token != '\n']
        i = 0 
        for item in tokens:
            class_list = [ elem.strip() for elem in item.split("OR")]
            if len(class_list) > 1:
                class_list[0] = class_list[0][2:].strip()
                class_list[-1] = class_list[-1][:-1].strip()
            j = 0
            for each_class in class_list:
                if "( min" in each_class:
                    grade = each_class.split(" ")
                    index_of_eq = grade.index("=")
                    grade = grade [index_of_eq + 1]
                    each_class = each_class [0 :each_class.index("( min")].strip()
                    lst = [each_class, grade]
                    class_list[j] = lst
                j+= 1
            tokens [i] = class_list
            i += 1
        prereq_list.append(tokens)

    CATALOGUE = dict(zip(course_list, prereq_list))

    return json.dumps(CATALOGUE)

if __name__=="__main__":
    print(parse())
