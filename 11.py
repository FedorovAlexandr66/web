from flask import Flask
from flask import render_template
from flask import Response
import sqlite3
import random
import io

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


def get_top_inquiry(job_titles: tuple[str, str], count: int = 15):
    inquiry = (f"SELECT LOWER(qualification) as 'qualification', count(*) as 'count' FROM works "
             f"WHERE qualification IS NOT NULL AND "
             f"(LOWER(jobTitle) like '%{job_titles[0]}%' OR LOWER(jobTitle) like '%{job_titles[1]}%')"
             f"GROUP BY LOWER(qualification) "
             f"ORDER BY count DESC LIMIT {count}")
    return inquiry


def get_con():
    con = sqlite3.connect('works.sqlite')
    con.row_factory = lambda cursor, row: {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
    return con


app = Flask(__name__)


@app.route("/")
def cv_number():
    cvs = get_cv()
    result = ""
    for i, cv in enumerate(cvs):
        result += f"<h1>{i + 1})</h1>"
        result += f"<p>Желаемая зарплата: {cv['salary']}.</p>"
        result += f"<p>Образование: {cv['educationType']}.</p>"

    return result


@app.route("/dashboard")
def dashboard():
    con = get_con()
    result = list(con.execute("SELECT COUNT(*) as 'count', strftime('%Y', dateModify) as 'year' "
                   "FROM works WHERE year IS NOT NULL GROUP BY year"))
    con.close()
    data = [r["count"] for r in result]
    labels = [r["year"] for r in result]
    return render_template('d1.html', cvs=result, data=data, labels=labels)


def dict_factory(cursor, row):
    # обертка для преобразования
    # полученной строки. (взята из документации)
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def get_cv():
    con = sqlite3.connect('works.sqlite')
    con.row_factory = dict_factory
    result = list(con.execute('select * from works limit 20'))
    con.close()
    return result


@app.route('/plot.png')
def plot_png():
    fig = create_figure()
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


def create_figure():
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    xs = range(100)
    ys = [random.randint(1, 50) for x in xs]
    axis.plot(xs, ys)
    return fig

app.run()