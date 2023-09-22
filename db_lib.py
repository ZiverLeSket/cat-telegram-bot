from mysql.connector.pooling import PooledMySQLConnection, MySQLConnection

import json

class DataBase():
    def __init__(self, connection: PooledMySQLConnection | MySQLConnection) -> None:
            self.connnection = connection
            self.cursor =  self.connnection.cursor()

    def create_db(self, dbname: str) -> None:
        self.cursor.execute(f'create database {dbname}')

    def create_table(self, tabletag: str, tableparams: list[str]) -> None:
        params = ''
        for param in tableparams:
            params += param + ', '
        self.cursor.execute(f'create table {tabletag} ({params})')

    def insert_data_to_table(self, tabletag: str, data: list[list[str]]) -> None:
        for items in data:
            params = ''
            for  param in items:
                if param == items[-1]:
                    params += param
                else:
                    params += param + ', '
            print(f'insert into {tabletag} values ({params})')
            self.cursor.execute(f'insert into {tabletag} values ({params})')
        self.connnection.commit()
    
    def export_json(self, tabletag: str) -> json:
        self.cursor.execute(f"select {tabletag}")
        result = self.cursor.fetchall()
        return json(result)
    
    def sort_by_rating(self, tabletag: str) -> json:
        self.cursor.execute("select *, "
                            f"((`{tabletag}`.`likes` - `{tabletag}`.`dislikes`) / `{tabletag}`.`views`) as `rating` "
                            f"from `{tabletag}` "
                            "order by `rating` "
                            "limit 0, 100")
        result = self.cursor.fetchall()
        return result

    def increment_counter(self, tabletag: str, counter: str, id: str) -> None:
        self.cursor.execute(f"select cat_id "
                            f"from {tabletag} "
                            f" where cat_id='{id}' "
        )
        selected_line = json(self.cursor.fetchall())
        counters_dist = {
            'views': 2,
            'likes': 3,
            'dislikes': 4,
        }
        counter_param = selected_line[counters_dist[counter]]
        self.cursor.execute(f"update {tabletag} "
                            f"set {counter} = {counter_param+1} "
                            f"where cat_id='{id}'"
        )