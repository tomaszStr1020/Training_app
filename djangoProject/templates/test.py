import cx_Oracle

userpwd = "PROJEKTprojekt##11" # Obtain password string from a user prompt or environment variable
connection = cx_Oracle.connect(user="ADMIN", password=userpwd,
                               dsn="db202112131719_high",
                               encoding="UTF-8")

kur = connection.cursor()
for row in kur.execute("select * from trenerzy"):
    print(row)