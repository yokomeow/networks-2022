from flask import Flask, request, abort, json
from flask_cors import CORS
import pymysql
from pymysql.cursors import DictCursor
import random
from json import loads
from collections import Counter

app = Flask(__name__)
CORS(app)

_PORT = 5555
_HOST = "0.0.0.0"
_WORDS = 3

def toFixed(num):
    return 0 if "NA" in str(num) else float("{0:.3f}".format(float(num)))

@app.route("/", methods=['GET'])
def get_plain():
    try:
        attempts = int(get_attempts(1)[0]['attempts'])
        words_count = int(get_words_count()[0]['count'])
        d = {}
        indecies = []

        if attempts <= 20:
            #отправляем случайные слова для формирования статистики
            for i in range(_WORDS):
                r = random.randint(0, words_count)
                indecies.append(r)
            word_l, letter_d = get_words(indecies)
            words = list(' '.join(word_l))
            d = {
                'attempts': attempts,
                'length': len(words),
                'words': words,
                'letters': letter_d
            }
        else:
            #отправляем слова, в которых наибольшее количество "проблемных" букв
             indecies = get_words_AI(1)
             word_l, letter_d = get_words(indecies)
             words = list(' '.join(word_l))
             d = {
                 'attempts': attempts,
                 'length': len(words),
                 'words': words,
                 'letters': letter_d
             }

        return app.response_class(
            json.dumps(d),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print('Что-то пошло не так:\n', e, flush=True)
        abort(400)

    return "Ok!"

@app.route("/get_stats", methods=['GET'])
def get_stats():
    try:
        r = get_user_letters(1)
        dd = []

        for i in r:
            dd.append(r[i])

        d = {'stats': dd}

        return app.response_class(
            json.dumps(d),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        print('Что-то пошло не так:\n', e, flush=True)
        abort(400)

    return "Ok!"


@app.route("/submit", methods=['POST'])
def submit():
    try:
        payload = loads(request.data)
        print('Received', payload, flush=True)
        update_letters(payload['letters'])
        update_mistakes(payload['mistakes'])
        update_letters_stat()
    except Exception as e:
        print('Что-то пошло не так:\n', e, flush=True)
        abort(400)

    return "Ok!"

def connect(commit=True):
    try:
        sql = pymysql.connect(
            host="mysql_web",
            user="root",
            password="muffin15",
            db="tt",
            port=3306,
            charset='utf8mb4',
            autocommit=commit,
            cursorclass=DictCursor
        )
        return sql
    except Exception as e:
        print('Ошибка подключения к базе')
        print(e)

def get_user_letters(user_id):
    sql = connect()
    cursor = sql.cursor()


    q = f""" 
        select a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u,v,w,x,y,z
        from users where user_id = {user_id};    
    """

    cursor.execute(q)
    letters = cursor.fetchall()
    letters = letters[0]
    sql.close()

    return letters

def get_indecies_by_words(words):
    sql = connect()
    cursor = sql.cursor()

    q = f""" 
        select id from words where word in ('{"','".join(words)}');
    """
    #print(q, flush=True)
    cursor.execute(q)
    inds = cursor.fetchall()
    print(inds, flush=True)
    inds = [ind['id'] for ind in inds]
    sql.close()

    return inds

def calc_weights(coefs):
    sql = connect()
    cursor = sql.cursor()

    q = f""" 
        select ({ ' '.join([str(coefs[c]) + '*' + c + ' +' for c in coefs])[:-1]}) as weight, word
        from words;    
    """
    cursor.execute(q)
    weights = cursor.fetchall()
    ws = {}
    print('Запрос в бд:\n', q, flush=True)
    for w in weights:
        ws[w['word']] = float(w['weight'])
    print('Слова с весами:\n', ws)
    sql.close()

    return ws

def get_words_AI(user_id):
    # получаем коэффициенты попаданий пользователя
    user_letters = get_user_letters(user_id)
    # 1-коэффициент попадания = коэффициаент промаха
    for ul in user_letters:
        user_letters[ul] = toFixed(1 - user_letters[ul])
    #считаем вес каждого слова
    weights = calc_weights(user_letters)
    #сортировка по убыванию
    words = []
    print('----------', sorted(weights.values(), reverse=True)[:_WORDS], flush=True)
    for v in sorted(weights.values(), reverse=True)[:_WORDS]:
        for i in weights:
            if weights[i]==v and len(words) < _WORDS and i not in words:
                words.append(i)
    #получаем индексы выбранных слов
    inds = get_indecies_by_words(words)

    return inds


def update_letters_stat():
    sql = connect()
    cursor = sql.cursor()

    q = f"""
        update users
        set
            { ','.join([letter + '= 1 - '+ letter +'_f / '+ letter +'_t' for letter in 'abcdefghijklmnopqrstuvwxyz']) },
            attempts = attempts+1
        where
            user_id = 1;
    """
    #print(q, flush=True)
    cursor.execute(q)
    sql.close()

def update_mistakes(mistakes):
    while ' ' in mistakes:
        mistakes.remove(' ')
    mistakes = set(mistakes)
    if len(mistakes) < 1:
        return
    c = Counter(mistakes)
    #print(c, flush=True)
    #print(mistakes, flush=True)
    sql = connect()
    cursor = sql.cursor()

    q = f"""
        update users
        set 
            {','.join([(letter + '_f=' + letter + '_f+' + str(c[letter])) for letter in mistakes])}
        where user_id = 1;
    """
    print(q, flush=True)
    cursor.execute(q)
    sql.close()

def update_letters(letters):
    sql = connect()
    cursor = sql.cursor()

    q = f"""
        update users
        set 
            {','.join([(letter + '_t=' + letter + '_t+' + str(letters[letter])) for letter in letters])}
        where user_id = 1;
    """
    #print(q, flush=True)
    cursor.execute(q)
    sql.close()


def get_words(ins):
    word_l = []
    letter_d = {letter:0 for letter in 'abcdefghijklmnopqrstuvwxyz'}

    sql = connect(False)
    cursor = sql.cursor()

    for i in ins:
        q = f"""
            select * from words where id = {i};    
        """
        cursor.execute(q)
        res = cursor.fetchall()
        d = res[0]
        word_l.append(d['word'])
        for l in letter_d:
            letter_d[l] += d[l]
        #print(res, flush=True)
    sql.close()

    return word_l, letter_d

def get_words_count():
    sql = connect()
    cursor = sql.cursor()

    q = f"""
            select count(*) as count from words;    
        """

    cursor.execute(q)
    count = cursor.fetchall()
    #print(attempts, flush=True)
    sql.close()

    return count


def get_attempts(user_id):
    sql = connect()
    cursor = sql.cursor()

    q = f"""
        select attempts from users where user_id = {user_id};    
    """

    cursor.execute(q)
    attempts = cursor.fetchall()
    #print(attempts, flush=True)
    sql.close()

    return attempts



if __name__ == "__main__":
    app.run(host=_HOST, port=_PORT)
