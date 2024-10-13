from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

# Database connection parameters
DATABASE_URL = 'postgresql://postgres.uvamvatffkoqvcghnsph:nbutOY2d52MiEi7B@aws-0-ap-south-1.pooler.supabase.com:6543/postgres'

@app.route('/')
def hello():
    return "Hello, World!!"

@app.route('/data')
def get_data():
    try:
        # Connect to the Supabase PostgreSQL database
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        # Execute the query
        cursor.execute("SELECT * FROM qtell.test;")
        rows = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Return the results as JSON
        return jsonify(rows)

    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
