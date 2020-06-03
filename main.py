import mysql.connector
import subprocess
import os

mydb = mysql.connector.connect(
host="localhost",
user="root",
passwd="root",
database="school"
)

cursor = mydb.cursor()

def main():
    with open('queries.txt', 'r', encoding='utf-8') as queries, open('template.tex', 'r', encoding='utf-8') as template_file:
        template_og = template_file.read()
        n = 1
        while question:=queries.readline():

            if question == "#--\n": break
            question = question[1:-1]
            template = template_og
            template= template.replace('<aim>', question)
            template= template.replace('<prog>', str(n))
            query = ""
            undo = ""

            while True:
                curr_pos = queries.tell()
                next_line = queries.readline()
                if next_line.lstrip()[0] == '#':
                    queries.seek(curr_pos)
                    break
                elif next_line.lstrip()[0] == ':':
                    undo += next_line.lstrip()
                else:
                    query += next_line
            
            query = query[:-1]
            undo = undo[1:-1]
            template= template.replace("<query>", query)

            if os.path.exists(f'pdfs/{n}.pdf'): 
                n+=1
                continue

            print(f"Now executing: #{n} - {question} - {query}")

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

            except mysql.connector.errors.InterfaceError as e:
                output = "No output"

            template = template.replace("<output>", output)

            if undo != "":
                print(f"Executing undo - {undo}")
                cursor.execute(undo)
                try:
                    cursor.fetchall()
                except mysql.connector.errors.InterfaceError:
                    pass

            with open("temp.tex", "w") as temp:
                temp.write(template)

            subprocess.check_output(["xelatex", "temp.tex"])

            os.rename("temp.pdf", f"pdfs/{n}.pdf")
            n += 1
    
    print("Done.")

main()