from embed_persist import EmbedPersist
from history_persist import HistoryPersist
from qtell_bot import QtellBot
from user_base import UserBase
import traceback
from flask import Flask, jsonify, request, redirect, url_for, render_template, make_response
import jwt
import datetime
import tempfile
import os
from dotenv import load_dotenv
from werkzeug.exceptions import RequestEntityTooLarge

load_dotenv(override=True)

app = Flask(__name__)
app.secret_key = os.getenv('JWT_SECRET_KEY') 
app.config['JWT_EXPIRATION'] = 30  
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

# Ensure the uploads directory exists
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_token(username):
    token = jwt.encode({
        'sub': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=app.config['JWT_EXPIRATION'])
    }, app.secret_key, algorithm='HS256')
    return token

def decode_token(token):
    try:
        return jwt.decode(token, app.secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/login', methods=['POST'])
def login():
    try:
        user_obj = None
        user_obj = UserBase()
        auth = request.json
        if auth and 'username' in auth and 'password' in auth:
            username = auth['username']
            password = auth['password']
            
            if user_obj.login(username, password):
                token = create_token(username)
                response = make_response(jsonify({'message': 'Login successful!'}), 200)
                response.set_cookie('jwt', token, httponly=True, secure=True)  
                return response
                
        return jsonify({'message': 'Invalid credentials'}), 401
    except Exception: 
        traceback.print_exc()
    finally:
        if user_obj:
            user_obj.close_connection()

@app.route('/logout', methods=['POST'])
def logout():
    try:
        response = make_response(jsonify({'message': 'Logged out successfully'}), 200)
        response.set_cookie('jwt', '', expires=0)  # Clear the cookie
        return response
    except Exception:
        traceback.print_exc()      

@app.route('/home', methods=['GET'])
def home():
    try:
        user_obj = UserBase()
        history_obj = HistoryPersist()
        token = request.cookies.get('jwt')  
        if token:
            decoded = decode_token(token)
            if decoded and user_obj.in_userbase(decoded['sub']):
                return render_template('temp.html', history=history_obj.get_history(decoded['sub']))
        return redirect(url_for('index')) 
    except Exception:
        traceback.print_exc()
    finally:
        if user_obj:
            user_obj.close_connection()
        if history_obj:
            history_obj.close_connection()

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_obj = None 
        user_obj = UserBase()
        history_obj = HistoryPersist()
        token = request.cookies.get('jwt') 
        if token:
            decoded = decode_token(token)
            if decoded and user_obj.in_userbase(decoded['sub']):  
                user_message = request.json.get('message')
                qtell = QtellBot(EmbedPersist(decoded['sub']).get_retriever())
                answer = qtell.ask_question(user_message, history_obj.get_history(decoded['sub']))
                response_message = f"{answer}"
                history_obj.insert_history(decoded['sub'], {'user': user_message, 'bot': response_message})
                return jsonify({'message': response_message})
        return jsonify({'status': 'error'}), 401  
    except Exception:
        traceback.print_exc()
        return jsonify({'message': 'Sorry we\'re out of free tokens today 😭 please try after sometime'}), 200
    finally:
        if user_obj:
            user_obj.close_connection()
        if history_obj:
            history_obj.close_connection()

@app.route('/upload', methods=['POST'])
def upload_file():
    try: 
        user_obj = None 
        user_obj = UserBase()
        token = request.cookies.get('jwt') 
        if token:
            decoded = decode_token(token)
            if decoded and user_obj.in_userbase(decoded['sub']):    
                print(request.form.to_dict())      
                if 'files' not in request.files:
                    return jsonify({'error': 'No files uploaded'}), 400

                uploaded_files = request.files.getlist('files')     
                
                embed_obj = EmbedPersist(decoded['sub']) 
                for uploaded_file in uploaded_files:
                    if uploaded_file.filename == '':    
                        continue                     
                    embed_obj.add_to_pg(uploaded_file)

                return jsonify({'message': 'Files processed successfully'}), 200
        return jsonify({'status': 'error'}), 401          
    except RequestEntityTooLarge:
        traceback.print_exc()
        return jsonify({'error': 'File too large (max size - 3MB) / internal error'}), 413 
    except Exception:
        return jsonify({'error': 'Internal error / please try after sometime :('}), 500
    finally:
        if user_obj: 
            user_obj.close_connection()        
        
@app.route('/clear', methods=['POST'])
def clear():
    try:
        user_obj = None 
        user_obj = UserBase()
        history_obj = HistoryPersist()
        token = request.cookies.get('jwt') 
        if token:
            decoded = decode_token(token)
            if decoded and user_obj.in_userbase(decoded['sub']):  
                history_obj.delete_history(decoded['sub'])
                embed_obj = EmbedPersist(decoded['sub'])
                embed_obj.delete_from_pg()
                return jsonify({'message': 'Chat history deleted'})
        return jsonify({'status': 'error'}), 401  
    except Exception:
        traceback.print_exc()
    finally:
        if user_obj:
            user_obj.close_connection()
        if history_obj:
            history_obj.close_connection()


@app.route('/signup', methods=['GET', 'POST'])
def signup(): 
    try:
        user_obj = None
        user_obj = UserBase()
        if request.method == 'POST':
            auth = request.json
            username = auth.get('username')
            password = auth.get('password')

            if not user_obj.in_userbase(username) and user_obj.signup(username, password):
                print('signup success')
                # return redirect(url_for('index', message='Signup successful! Please log in.'))
                jsonify({'message': 'Signup successful! Please log in.'}), 200
            else:
                return jsonify({'message': 'Username already exists'}), 400
        print('came here')
        return render_template('signup.html')
    except Exception: 
        traceback.print_exc()
    finally:
        if user_obj: 
            user_obj.close_connection()

if __name__ == '__main__':
    app.run(debug=True)


