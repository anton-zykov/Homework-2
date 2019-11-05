from flask import Flask, render_template, request
import csv
import json
import sqlite3

app = Flask(__name__)
filename = 'results.csv'


def draw_statistics():
    import pandas as pd
    columns = ['Language', 'Coat', 'Gloves', 'Scarf', 'Shoes']
    df = pd.read_csv('results.csv', names=columns)
    out = "{% extends \"stats.html\" %}\n\n{% block content %}\n" + df.sort_values(
        by=['Language']).to_html() + "\n{% endblock %}"
    f = open("templates/extends.html", "w+", encoding="utf-8")
    f.write(out)
    f.close()


@app.route('/')
def main_page():
    return render_template("index.html")


@app.route('/thanks', methods=['POST'])
def save_to_csv():
    if request.method == 'POST':
        lang = request.form['lang']
        coat = request.form['coat']
        gloves = request.form['gloves']
        scarf = request.form['scarf']
        shoes = request.form['shoes']
        fin_form = 'Your answer has been recorded. Thank you!'
        fieldnames = ['lang', 'coat', 'gloves', 'scarf', 'shoes']
        with open(filename, 'a+', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'lang': lang, 'coat': coat, 'gloves': gloves,
                             'scarf': scarf, 'shoes': shoes})
        conn = sqlite3.connect('results.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS result (lang text, coat text, gloves text, scarf text, shoes text)")
        c.execute("INSERT INTO result VALUES (?, ?, ?, ?, ?)", (lang, coat, gloves, scarf, shoes))
        conn.commit()
        conn.close()
        return render_template("thanks.html", fin_form=fin_form)


@app.route('/search')
def do_search():
    return render_template("search.html")


@app.route('/results', methods=['POST'])
def show_result():
    dict_csv = {}
    if request.method == 'POST':
        what = request.form['what_search']
        fieldnames = ['lang', 'coat', 'gloves', 'scarf', 'shoes']
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            counter = 0
            for row in reader:
                if (row['lang'] == what or row['coat'] == what or row['gloves'] == what or
                        row['scarf'] == what or row['shoes'] == what):
                    name = row['lang']
                    counter += 1
                    dict_csv[name + str(counter)] = json.loads(json.dumps(row))
    return render_template("results.html", result=dict_csv)


@app.route('/stats')
def show_stats():
    draw_statistics()
    return render_template("extends.html")


if __name__ == '__main__':
    app.run(debug=True)
