# coding: utf-8
import sqlite3


class DatabaseManager:
    def __init__(self):
        if 'data' not in __import__('os').listdir('.'):
            __import__('os').mkdir('data')

        self.connection = sqlite3.connect("data/alisa_users.db", isolation_level=None)
        cursor = self.connection.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS users '
                       '(user_id TEXT PRIMARY KEY NOT NULL, last_char TEXT, already_used_words TEXT,'
                       'current_score INT, max_score INT)')
        cursor.close()

    def __del__(self):
        self.connection.close()

    def add_user(self, user_id: str, last_char: str = '', already_used_words: str = '',
                 current_score: int = 0, max_score: int = 0) -> bool:
        cursor = self.connection.cursor()
        try:
            if not self.get_entry(user_id):
                cursor.execute("""INSERT INTO users 
                                VALUES(:user_id, :last_char, :already_used_words,
                                :current_score, :max_score)""", {
                    'user_id': user_id, 'last_char': last_char, 'already_used_words': already_used_words,
                    'current_score': current_score, 'max_score': max_score
                })
                print('Пользователь {} добавлен.'.format(user_id))
            else:
                print('Пользователь {} уже существует!'.format(user_id))
                cursor.close()
                return False
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def update(self, user_id: str, new_last_char: str, used_words: str,
                 current_score: int = 0, max_score: int = 0) -> bool:
        cursor = self.connection.cursor()
        try:
            exist_entry = self.get_entry(user_id)
            if not exist_entry:
                print('Пользователь с номером {} не существует!'.format(user_id))
                return False
            else:
                print(exist_entry, ' - exist entry;;;    branch else in update')
                comma = ',' if len(exist_entry[0][2]) > 0 else ''
                cursor.execute("""UPDATE users
                                SET last_char = :last_char, 
                                already_used_words = :already_used_words,
                                current_score = :current_score,
                                max_score = :max_score
                                WHERE user_id == :user_id""",
                               {
                                   'user_id': user_id, 'last_char': new_last_char,
                                   'already_used_words': used_words,
                                   'current_score': current_score, 'max_score': max_score

                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def get_entry(self, user_id: str) -> list:
        cursor = self.connection.cursor()
        result = []
        try:
            cursor.execute("""SELECT * FROM users
                            WHERE user_id = :user_id""",
                           {
                               'user_id': user_id,
                           })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        else:
            result = cursor.fetchall()
        cursor.close()
        return result

    def get_all_entries(self) -> list:
        cursor = self.connection.cursor()
        result = []
        try:
            cursor.execute("""SELECT * FROM users
                           """)
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
        else:
            # self.connection.commit()
            result = cursor.fetchall()
        cursor.close()
        return result

    def delete_user(self, user_id: str) -> bool:
        cursor = self.connection.cursor()
        try:
            exist_entry = self.get_entry(user_id)
            if not exist_entry:
                print('Пользователь с номером {} не существует!'.format(user_id))
                return False
            else:
                cursor.execute("""DELETE FROM users
                                WHERE user_id = :user_id""",
                               {
                                   'user_id': user_id
                               })
        except sqlite3.DatabaseError as error:
            print('Error: ', error)
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def make_leaderboard(self, size_of_table: int = 10) -> list:
        values_list = self.get_all_entries()  # [('1', '', '', 0, 0), ('2', 'н', 'таракан', 0, 0)]
        result = sorted(values_list, key=lambda inner_list: inner_list[4], reverse=True)
        size_of_board = len(result) if len(result) < size_of_table else size_of_table
        return [(i, result[1], result[4]) for i in range(size_of_board)]
