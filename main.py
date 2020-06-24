import mysql.connector
import subprocess
import os
import sys
from io import StringIO
from mysql.connector.errors import Error

LANGUAGE = 'python'

if (LANGUAGE == 'sql'):
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="school"
    )


    cursor = mydb.cursor()


def query_mysql(query, undo, template):
    cursor.execute(query)

    output = ""
    try:
        results = cursor.fetchall()

        if len(results) > 0:
            widths = []
            columns = []
            tavnit = '|'
            separator = '+' 

            for i in range(len(cursor.description)):
                cd = cursor.description[i]
                max_col_length = max(  len(str(x[i])) for x in results  )
                widths.append(max(max_col_length, len(cd[0])))
                columns.append(cd[0])

            for w in widths:
                tavnit += " %-"+"%ss |" % (w,)
                separator += '-'*w + '--+'

            output += separator + "\n"
            output += tavnit % tuple(columns)+ "\n"
            output += separator+ "\n"
            for row in results:
                output += tavnit % row+ "\n"
            output += separator
        else:
            output = "Empty Set"
    except mysql.connector.errors.InterfaceError:
        output = "No output"

    template = template.replace("<output>", output)

    if undo != "":
        print(f"Executing undo - {undo}")
        cursor.execute(undo)
        try:
            cursor.fetchall()
        except mysql.connector.errors.InterfaceError:
            pass
    return template

def query_python(query, tests, template, header):
    old_std_out = sys.stdout
    
    exec(header+ "\n"+ query, globals())

    output=""
    result = None
    count = 0

    for test in tests.split(';'):
        if test.strip() == '': continue
        if test[0] == '/':
            test = test[1:]
            for line in test.split("\n"):
                count+=1 
                if not line:
                    continue
                output += f">>> {line}\n"
                redir = sys.stdout = StringIO()
                exec(line, globals())
                output += redir.getvalue()
        else:
            output += f">>> {test.strip()}\n"
            result = eval(test, globals())
        output += str(result if result != None else "") + "\n"

    sys.stdout = old_std_out
    template = template.replace("<output>", output)
    return template

def main():
    with open(f'queries-{LANGUAGE}.txt', 'r', encoding='utf-8') as queries, open(f'template-{LANGUAGE}.tex', 'r', encoding='utf-8') as template_file:
        template_og = template_file.read()
        n = 1
        while question:=queries.readline():

            if question == "#--\n": break
            question = question[1:-1]
            template = template_og
            template= template.replace('<aim>', question)
            template= template.replace('<prog>', str(n))
            template=template.replace("_", "\\textunderscore ")
            query = ""
            undo = ""
            py_header = ""

            while True:
                curr_pos = queries.tell()
                next_line = queries.readline()
                if next_line.strip() == "":
                    continue

                elif next_line.lstrip()[0] == '#':
                    queries.seek(curr_pos)
                    break
                elif next_line.lstrip()[0] == ':':
                    undo += next_line.lstrip()[1:]
                elif next_line.lstrip()[0] == '?':
                    py_header += next_line.lstrip()[1:-1]
                else:
                    query += next_line
            
            query = query[:-1]

            template= template.replace("<query>", query)

            if os.path.exists(f'pdfs/{LANGUAGE}/{n}.pdf'): 
                n+=1
                continue

            print(f"Now executing: #{n} - {question[:50]} - {query[:50]}")


            template = query_mysql(query, undo, template) if LANGUAGE == 'sql' else query_python(query, undo, template, py_header)
            

            with open("temp.tex", "w") as temp:
                temp.write(template)

            subprocess.check_output(["xelatex", "--shell-escape", "temp.tex"])

            os.rename("temp.pdf", f"pdfs/{LANGUAGE}/{n}.pdf")
            n += 1
    
    print("Done.")

main()