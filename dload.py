import model as mod
import pandas as pd
import numpy as np
import requests
import json

def send_post(userid, like_books, pred_books, age):
    url = 'http://89.223.94.217:5000/api/v1/modify_users'
    headers = {'Content-type': 'application/json',  
               'Accept': 'text/plain',
               'Content-Encoding': 'utf-8'}
    data = {
        "id": userid,
        "likes_books": like_books,
        "suggestions_books": pred_books,
        "age": age
       }
    # Если по одному ключу находится несколько словарей, формируем список словарей
    answer = requests.post(url, data=json.dumps(data), headers=headers)
    response = answer.json()

def load_data():
    predictor = mod.predict_model('books_neighbors.csv', 'clients_neighbors.csv', 'usersid_booksid.csv')
    cat = pd.read_excel('каталог.xlsx')
    cat['doc_id'] = cat['doc_id'].astype('str')
    cat = cat.set_index('doc_id')
    conn = pd.read_csv('usersid_booksid.csv', sep=';')
    conn['userid'] = conn['userid'].astype('int').astype('str')
    conn = conn.set_index('userid')
    cnt = 200000
    users = []
    b_users = pd.read_csv('usersid_ages.csv', sep=';', encoding='utf-8')
    print("Catalogs loading finished... sending data to remote database")
    for userid in conn.index:
        curuser = int(userid)
        pred = predictor.predict([str(curuser)], 10)[0]
        if pred is np.nan:
            print(str(curuser)+' [ Error ]')
            continue
        like_books = ''
        for bid in conn.loc[str(curuser)]['bookid'].split(','):
            info = cat.loc[bid]
            if info['p100a'] is np.nan:
                info['p100a'] = ''
            if info['p245a'] is np.nan:
                info['p245a'] = ''
            if info['p650a'] is np.nan:
                info['p650a'] = ''
            like_books+='Автор: '+info['p100a']+' , Название: '+info['p245a']+',  Жанр: '+info['p650a']+';'
        names = [cat.loc[bid]['p245a'] for bid in pred.index][::-1]
        authors = [cat.loc[bid]['p100a'] for bid in pred.index][::-1]
        genres = [cat.loc[bid]['p650a'] for bid in pred.index][::-1]
        for i in range(len(names)):
            if names[i] is np.nan:
                names[i] = ''
            if authors[i] is np.nan:
                authors[i] = ''
            if genres[i] is np.nan:
                genres[i] = ''
        importances = pred.values
        indices = np.argsort(importances)
        pred_books = ''
        for i, val in enumerate(importances[indices]):
            if val >= 0.9:
                pred_books+='Автор: '+authors[i]+' , Название: '+names[i]+',  Жанр: '+genres[i]+';'

        send_post(curuser, like_books, pred_books, int(b_users.loc[b_users['userid'] == curuser]['age']))
        users.append(curuser)
        print(str(curuser)+' [ OK ]')
        cnt-=1
        if cnt <= 0:
            break
		
def main():
    print("Start loading data...")
    load_data()
    print("Finish")


if __name__ == '__main__':
    main()