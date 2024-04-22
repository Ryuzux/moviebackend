from flask import  jsonify
from models import *
from user import *
from sqlalchemy import create_engine, text


engine = create_engine('postgresql://postgres:1234@localhost/movie')

@app.route('/topmovie', methods=['GET'])
@User.admin_or_user_required
def most_popular_movie(current_user):
    with engine.connect() as con:
        sql_query = text("""
        SELECT
            m.id,
            m.name,
            COUNT(t.id) AS ticket
        FROM movie m
        JOIN schedule s ON m.id = s.movie_id
        JOIN transaction t ON s.id = t.schedule_id
        GROUP BY m.id
        ORDER BY ticket DESC
        LIMIT 5;
        """)
        
        result = con.execute(sql_query)
        top_movies = [
        {
        "id": row[0],
        "movie": row[1],
        "ticket_count": row[2]
        }for row in result]
        
        return jsonify(top_movies), 200 


