import json
import pymysql

class stu_temp_data():
    def get_all(stu_num):
        mydb = pymysql.connect(host="127.0.0.1", user="root", passwd="zkfelqlxkww01", database="capstonedb", charset='utf8')
        db_cursor = mydb.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT * FROM daytempdb WHERE stu_num = %s ORDER BY time DESC"
        if stu_num == 'admin':
            sql = "SELECT * FROM daytempdb"
            db_cursor.execute(sql, {})
            temp_lists = db_cursor.fetchall()
            return temp_lists
        
        db_cursor.execute(sql, [stu_num])
        temp_lists = db_cursor.fetchall()

        return temp_lists