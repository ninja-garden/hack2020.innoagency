import numpy as np
import pandas as pd
class predict_model():
    def __init__(self, books_neigh_csv_name, clients_neigh_csv_name, conn_csv_name):
        print('Загрузка файла метрик книг')
        self.books_neighbors = pd.read_csv(books_neigh_csv_name).fillna('')
        self.books_neighbors['id'] = self.books_neighbors['id'].astype('str')
        self.books_neighbors = self.books_neighbors.set_index('id')
        print('Загрузка файла метрик пользователей')
        self.clients_neighbors = pd.read_csv(clients_neigh_csv_name).fillna('')
        self.clients_neighbors['id'] = self.clients_neighbors['id'].astype('str')
        self.clients_neighbors = self.clients_neighbors.set_index('id')
        print('Загрузка истории пользователей')
        self.connect = pd.read_csv(conn_csv_name, sep=';')
        self.connect['userid'] = self.connect['userid'].astype('int').astype('str')
        self.connect = self.connect.set_index('userid')
    def predict(self, user_ids, top):
        RESULT = []
        for c_p_ind in user_ids:
            try:
                likely_clients = np.array(list(self.clients_neighbors.loc[c_p_ind]['neighbors'].split(','))+[c_p_ind])
                likely_clients = likely_clients[likely_clients!='']
                bad_list = self.connect.loc[c_p_ind]['bookid']
                booklist = ''
                for userid in likely_clients:
                    booklist += (self.connect.loc[userid]['bookid'] + ',')
                result = booklist
                for bid in booklist[:-1].split(','):
                    try:
                        result += (self.books_neighbors.loc[bid]['neighbors'] + ',')
                    except:
                        continue
                result = pd.Series(result[:-1].split(','))
                result = result[[(book not in bad_list) for book in result]]
                result_vc = result.value_counts()
                result_vc = result_vc[:top]
                result_vc /= result_vc.max()
                RESULT.append(result_vc)
            except:
                #Клиента нет в базе
                RESULT.append(np.nan)
        return RESULT
