# app.py
import io
from flask import Flask, render_template
from basketball.matchup_analysis import week_analysis
app = Flask(__name__)

@app.route('/')
def index():

    matchups = week_analysis()

    def df2html(df):
        """wrapper for getting html strings for table from df"""
        str_io = io.StringIO()
        df.to_html(buf=str_io,
                   classes='table matchup-table')
        return(str_io.getvalue())
        
    matchups_html = [df2html(i) for i in matchups]
    
    context = {
        'matchups': matchups_html,
    }
    
    return render_template('index.html', matchups=matchups_html)

