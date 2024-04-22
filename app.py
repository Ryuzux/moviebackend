from models import *
from user import *
from movie_manage import *
from reporting import *
from topup import *


if __name__ == '__main__':
    app.run(host="127.0.0.1", port = 5000, debug=True)