from replit import web
import flask
from flask import Response, Flask, request, jsonify, render_template
from flask_cors import CORS
import psycopg2
from tabulate import tabulate
import openai

app = Flask(__name__)
CORS(app)

openai.api_key = "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"


@app.route("/")
def index():
  html = render_template("index.html")
  return Response(html, content_type="text/html; charset=utf-8")


@app.route("/query", methods=["POST"])
def query():
  data = request.get_json()
  user_query = data["user_query"]

  # Connect to the database
  conn = psycopg2.connect(host="db.hhkvwfdkzdcaktrzyiww.supabase.co",
                          port="5432",
                          database="postgres",
                          user="postgres",
                          password="6yPGNCp#NcH9rm")

  cur = conn.cursor()

  # Translate natural language query to SQL using OpenAI API
  response = openai.Completion.create(
    # Your existing OpenAI code here
    model="text-davinci-003",
    prompt=
    f"""Create a Postgres request to user query from swim_table where columns are as follows:
       - result_rank, 
       - full_name, 
       - distance, 
       - event_desc, 
       - swimmer_age, 
       - TO_CHAR( time, 'MI:SS.MS' ) ts_to_char_result
       - standard_name, 
       - meet_name, 
       - TO_CHAR(swim_date, 'YYYY-MM-DD') AS swim_date, 
       - hytek_power_points, 
       - boys_girls
    
    FOR EXAMPLE "will modglin" is the same as "Modglin, William", "hermacinski" is the same as
    "Hermacinski, Annabel", "metzger" is the same as "Metzger, Ava". 
    
    FOR EXAMPLE, for question
    "show the results for all girls named Ava", use 
SELECT full_name, event_desc, swimmer_age, TO_CHAR(time, 'MI:SS.MS') AS ts_to_char_result, meet_name, standard_name, TO_CHAR(swim_date, 'YYYY-MM-DD') AS swim_date, boys_girls
FROM swim_table
WHERE LOWER(full_name) ILIKE '%ava%'
ORDER BY time ASC;

  FOR EXAMPLE, for this question "compare the results of hermacinski and hovyadinov in 100 FR", the resulting SQL query will be: 
    SELECT full_name, event_desc, swimmer_age, TO_CHAR( time, 'MI:SS.MS' ) as ts_to_char_result, meet_name, TO_CHAR(swim_date, 'YYYY-MM-DD') AS swim_date, standard_name, boys_girls
FROM swim_table
WHERE (LOWER(full_name) LIKE '%hovyadinov%' OR LOWER(full_name) LIKE '%hermacinski%')
AND (event_desc = '100 FR SCY' OR event_desc = '100 FR LCM' OR event_desc = '100 FR SCM')
ORDER BY time ASC;
    
    When asked to compare the performance of several swimmers in a specific event, make sure the query filters the event(s) with = , 
    and not LIKE to match the event description that contains the specified string (e.g. "200 IM SCY", "200 IM LCM", etc.).
    if asked to show the best time for a swimmer, limit your answer to one result per event.
    if asked to show ALL RESULTS, don't limit the outcome to 1. Show all. With all fields.  
    FOR EXAMPLE, "top 5 in 100 fr among girls" should result in 
    SELECT result_rank, full_name, swimmer_age, TO_CHAR(time, 'MI:SS.MS') AS time, meet_name, standard_name, TO_CHAR(swim_date, 'YYYY-MM-DD') AS swim_date, boys_girls
FROM swim_table
WHERE (event_desc = '100 FR SCY' OR event_desc = '100 FR LCM' OR event_desc = '100 FR SCM')
AND boys_girls = 'Girls'
ORDER BY time
LIMIT 3;

    {user_query} 
    """,
    temperature=0.6,
    max_tokens=300,
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    stop=["#", ";"])

  generated_query = response.choices[0].text.strip()

  cur.execute(generated_query)

  results = cur.fetchall()

  table = [[]]
  for row in results:
    table.append(list(row))

  cur.close()
  conn.close()

  return jsonify({"table": table})


if __name__ == '__main__':
  app.run('0.0.0.0')
