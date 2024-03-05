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
from urllib.parse import urlparse
from dotenv import load_dotenv
from datetime import date
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index_page():
    return render_template('index.html')


@app.get('/urls')
def render_add_page():
    messages = get_flashed_messages(with_categories=True)
    if (messages):
        return render_template('index.html', messages=messages,)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM urls')
    urls = cursor.fetchall()
    urls.reverse()
    cursor.close()
    return render_template('view_pages.html', urls=urls,)


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
    cursor.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'view_page.html',
        messages=messages,
        url=url,
        id=id
    )
