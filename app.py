from models import *
from user import *
from movie_manage import *
from reporting import *
from topup import *

@app.route('/')
def home():
    return 'welcome'



if __name__ == '__main__':
    app.run(debug=False)