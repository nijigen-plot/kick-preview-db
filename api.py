import os

from flask import Flask, jsonify, request
import boto3
import mysql.connector
from dotenv import load_dotenv

from logger_setup import setup_logger

logger = setup_logger()
load_dotenv()

mariadb_user = os.getenv('MARIADB_USER') 
mariadb_pw = os.getenv('MARIADB_PASSWORD')
aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_SECRET_KEY')

app = Flask(__name__)

@app.route('/api/get-content', methods=['GET'])
def get_content():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user=mariadb_user,
            password=mariadb_pw,
            database='kick_preview'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT title, audio_content_uri, image_content_uri FROM tracks ORDER BY RAND() LIMIT 1;")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result is not None:
            title = result[0]
            audio_uri = result[1]
            image_uri = result[2]
            res = jsonify({
                    "title" : title,
                    "audio_uri" : audio_uri,
                    "image_uri" : image_uri
                })
            logger.info(res)
            return res
        else:
            res = jsonify({"error": "Not found data. Please check kick_preview table."})
            logger.error(res)
            return res
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}", exc_info=True)
        return jsonify({"error":f"{e}"})

@app.route('/api/put-content', methods=['PUT'])
def put_content():
    try:
        data = request.get_json()
        print(data)
        conn = mysql.connector.connect(
            host='localhost',
            user=mariadb_user,
            password=mariadb_pw,
            database='kick_preview'
        )n
        # cursor = conn.cursor()
        # conn.start_transaction()
        # conn.execute(f"INSERT INTO tracks (title, audio_content_uri, image_content_uri, link) VALUES ({}, {}, {}, {}) ")
        # conn.commit()
        return jsonify({"message": "Data inserted successfully"}), 200
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}", exc_info=True)
        return jsonify({"error":f"{e}"})

@app.errorhandler(404)
def page_not_found(error):
    logger.error(f"Page not found: {request.url}, error: {error}")
    return jsonify({"error": "Page not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server error: {error}, URL: {request.url}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
