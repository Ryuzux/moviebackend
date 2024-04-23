from models import *
from user import *
from movie_manage import *
from reporting import *
from topup import *
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'welcome'



if __name__ == '__main__':
    app.run(debug=True)