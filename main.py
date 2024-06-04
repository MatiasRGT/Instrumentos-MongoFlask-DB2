from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import json
from datetime import datetime
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Replace with mongo db atlas string ---> .env
# Load environment variables from .env file
load_dotenv()
# Retrieve the MongoDB URI from environment variables
uri = os.getenv("mongo_srv")


client = MongoClient(uri)
db = client['instrumentos']
students_collection = db['estudiantes']

def format_dates(result):
    for key, value in result.items():
        if isinstance(value, dict):
            format_dates(value)
        elif isinstance(value, list):
            for item in value:
                format_dates(item)
        elif key.endswith('fechaOficializacion') or key.endswith('fechaSolicitud'):
            result[key] = datetime.strptime(value['$date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d')
    return result

@app.route("/", methods=('GET', 'POST'))
def index():
    query_result = None
    error = None
    if request.method == 'POST':
        query_str = request.form['query']
        try:
            query = json.loads(query_str)
            query_result = list(students_collection.find(query))
            query_result = [format_dates(result) for result in query_result]
        except Exception as e:
            error = str(e)
    
    return render_template('index.html', query_result=query_result, error=error)

@app.route("/students")
def view_students():
    all_students = list(students_collection.find())
    return render_template('students.html', students=all_students)

@app.post("/<id>/delete/")
def delete(id):
    students_collection.delete_one({"_id": ObjectId(id)})
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)