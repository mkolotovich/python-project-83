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
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute("""SELECT urls.id, urls.name, MAX(url_checks.created_at)
                      , MAX(status_code) FROM urls LEFT JOIN url_checks ON
                      urls.id=url_checks.url_id GROUP BY urls.id ORDER BY
                      urls.id DESC""")
        urls = cursor.fetchall()
        normalized_urls = list(map(normalize_data, urls))
    return render_template('view_pages.html', urls=normalized_urls)


@app.post('/urls')
def add_page():
    url = request.form.to_dict().get('url', '')
    url_max_len = 255
    parsed_url = urlparse(url)
    normalized_url = f"{parsed_url.scheme}://{parsed_url.hostname}"
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM urls WHERE name=%s', (normalized_url,))
        id = cursor.fetchone()
        if (not validators.url(url) or len(url) > url_max_len):
            if (len(url) > url_max_len):
                flash('URL превышает 255 символов', 'error')
            else:
                flash('Некорректный URL', 'error')
            messages = get_flashed_messages(with_categories=True)
            return render_template('index.html', messages=messages), 422
        if (not id):
            cursor.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s);",
                (normalized_url, date.today()))
            cursor.execute('SELECT id FROM urls WHERE name=%s',
                           (normalized_url,))
            id = cursor.fetchone()[0]
            conn.commit()
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('render_url_page', id=id))
        else:
            flash('Страница уже существует', 'info')
            return redirect(url_for('render_url_page', id=id[0]))


@app.route('/urls/<int:id>')
def render_url_page(id):
    conn = psycopg2.connect(DATABASE_URL)
    with conn.cursor() as cursor:
        cursor.execute('SELECT name, created_at FROM urls WHERE id=%s', (id,))
        url, date = cursor.fetchone()
        cursor.execute("""SELECT id, status_code, h1, title, description,
                    created_at FROM url_checks WHERE url_id=%s
                    ORDER BY id DESC""", (id,))
        checks = cursor.fetchall()
        normalized_checks = list(map(normalize_data, checks))
        messages = get_flashed_messages(with_categories=True)
        return render_template(
            'view_page.html',
            messages=messages,
            url=url,
            id=id,
            date=date,
            checks=normalized_checks
        )


@app.post('/urls/<int:id>/checks')
def check_page(id):
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    with conn.cursor() as cursor:
        cursor.execute('SELECT name FROM urls WHERE id=%s', (id,))
        url = cursor.fetchone()[0]
        try:
            r = requests.get(url)
            if (not r.raise_for_status()):
                html = BeautifulSoup(r.text)
                cursor.execute(
                    """INSERT INTO url_checks
                    (url_id, status_code, h1, title, description, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s);""",
                    (id, r.status_code, html.h1.string, html.title.string,
                     html.find(attrs={"name": "description"})['content'],
                     date.today()))
                flash('Страница успешно проверена', 'success')
                return redirect(url_for('render_url_page', id=id))
            else:
                flash('Произошла ошибка при проверке', 'danger')
                return redirect(url_for('render_url_page', id=id))
        except Exception:
            flash('Произошла ошибка при проверке', 'danger')
            return redirect(url_for('render_url_page', id=id))
