from flask import (
    Flask,
    render_template,
    request,
    flash,
    get_flashed_messages,
    redirect,
    url_for
)
import psycopg2
import os
import validators
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
from datetime import date
from bs4 import BeautifulSoup
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index_page():
    return render_template('index.html')


def normalize_data(item):
    converted_values = list(map(lambda val: (val if val else ''), item))
    return converted_values


@app.get('/urls')
def render_add_page():
    messages = get_flashed_messages(with_categories=True)
    if (messages):
        return render_template('index.html', messages=messages,)
    cursor = conn.cursor()
    cursor.execute("""SELECT urls.id, urls.name, MAX(url_checks.created_at),
                      MAX(status_code) FROM urls LEFT JOIN url_checks ON
                      urls.id=url_checks.url_id GROUP BY urls.id ORDER BY
                      urls.id DESC""")
    urls = cursor.fetchall()
    normalized_urls = list(map(normalize_data, urls))
    cursor.close()
    return render_template('view_pages.html', urls=normalized_urls)


@app.post('/urls')
def add_page():
    url = request.form.to_dict().get('url', '')
    url_max_len = 255
    cursor = conn.cursor()
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    cursor.execute('SELECT id FROM urls WHERE name=%s', (normalized_url,))
    id = cursor.fetchone()
    if (validators.url(url) and len(url) <= url_max_len and not id):
        cursor.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
            (normalized_url, date.today()))
        cursor.execute('SELECT id FROM urls WHERE name=%s', (normalized_url,))
        id = cursor.fetchone()[0]
        cursor.close()
        flash('Страница успешно добавлена', 'success')
        return redirect(url_for('render_url_page', id=id))
    elif (len(url) > url_max_len):
        flash('URL превышает 255 символов', 'error')
        return redirect(url_for('render_add_page'))
    elif (id):
        flash('Страница уже существует', 'info')
        return redirect(url_for('render_url_page', id=id[0]))
    else:
        flash('Некорректный URL', 'error')
        return redirect(url_for('render_add_page'))


@app.route('/urls/<id>')
def render_url_page(id):
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
    url = cursor.fetchone()[0]
    cursor.execute("""SELECT id, status_code, h1, title, description,
                   created_at FROM url_checks WHERE url_id=%s
                   ORDER BY id DESC""",
                   (id,))
    checks = cursor.fetchall()
    normalized_checks = list(map(normalize_data, checks))
    print(normalized_checks)
    cursor.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'view_page.html',
        messages=messages,
        url=url,
        id=id,
        checks=normalized_checks
    )


@app.post('/urls/<id>/checks')
def check_page(id):
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
    url = cursor.fetchone()[0]
    r = requests.get(url)
    html = BeautifulSoup(r.text)
    cursor.execute(
        """INSERT INTO url_checks (url_id, status_code, created_at)
        VALUES (%s, %s, %s);""",
        (id, r.status_code, date.today()))
    cursor.execute("SELECT id FROM url_checks")
    ids = cursor.fetchall()
    check_id = ids[len(ids) - 1][0]
    if (html.h1):
        cursor.execute(
            "UPDATE url_checks SET h1=%s WHERE id=%s",
            (html.h1.string, check_id))
    if (html.title):
        cursor.execute(
            "UPDATE url_checks SET title=%s WHERE id=%s",
            (html.title.string, check_id))
    if (html.meta):
        cursor.execute(
            "UPDATE url_checks SET description=%s WHERE id=%s",
            (html.find(attrs={"name": "description"})['content'], check_id))
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('render_url_page', id=id))
