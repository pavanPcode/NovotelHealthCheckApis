from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import configparser
import os

current_directory = os.path.dirname(__file__)
# Construct the path to the INI file
ini_file_path = os.path.join(current_directory, 'dbconfig.ini')

# Initialize configparser
config = configparser.ConfigParser()

# Read the INI file
config.read(ini_file_path)

app = Flask(__name__)
cors = CORS(app)

# MySQL database configuration
db_config = {
        'host': config['mysql_conn']['host'],
        'user': config['mysql_conn']['username'],
        'password': config['mysql_conn']['password'],
        'database': config['mysql_conn']['database'],
    }

@app.route('/Novotel/Create_HealthCheck', methods=['POST'])
def insert_data():
    # Extract data from the request
    data = request.json

    # Connect to MySQL database
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Insert data into the Novotelhealthcheck table
        cursor.execute("""
            INSERT INTO Novotelhealthcheck (DateOfTransaction, EntryCount, ExitCount, InAndOutTotal, InAndOutFind, Type, Message)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['DateOfTransaction'],
            data['EntryCount'],
            data['ExitCount'],
            data['InAndOutTotal'],
            data['InAndOutFind'],
            data['Type'],
            data['Message']
        ))

        # Commit the transaction
        connection.commit()

        return jsonify({'message': 'Data inserted successfully'}), 200

    except mysql.connector.Error as error:
        return jsonify({'error': str(error)}), 500

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/Novotel/get_healthcheck', methods=['GET'])
def get_data():
    try:
        # Extract date parameter from the request
        date_param = request.args.get('date')

        # Connect to MySQL database
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Execute query to fetch data from Novotelhealthcheck table for the specified date
        cursor.execute("SELECT * FROM Novotelhealthcheck WHERE DATE(DateOfTransaction) = %s order by id desc", (date_param,))

        # Fetch all rows
        rows = cursor.fetchall()

        # Create a list to store JSON objects representing each row
        data = []
        for row in rows:
            data.append({
                'id': row[0],
                'DateOfTransaction': row[1].strftime('%Y-%m-%d %H:%M:%S'),
                'EntryCount': row[2],
                'ExitCount': row[3],
                'InAndOutTotal': row[4],
                'InAndOutFind': row[5],
                'Type': row[6],
                'Message': row[7]
            })
        data = {'Status':True,'ResultData':data}

        return jsonify(data), 200

    except mysql.connector.Error as error:
        return jsonify({'Status':False,'ResultData': str(error)}), 500

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()




if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8765,debug=True)
