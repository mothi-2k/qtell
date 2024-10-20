import traceback
from flask import Flask, jsonify, request, redirect, url_for, render_template, make_response
import jwt
import datetime
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
import bcrypt

load_dotenv(override=True)

class UserError(Exception):
    pass

class UserBase:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(f'postgresql://postgres.uvamvatffkoqvcghnsph:{os.getenv("DB_PASSWORD")}@aws-0-ap-south-1.pooler.supabase.com:6543/postgres')
            self.cursor = self.conn.cursor()
        except Exception:
            traceback.print_exc()
            raise UserError()            
        
    def in_userbase(self, username):
        try: 
            self.cursor.execute("SELECT username FROM qtell.users where username = %s", (username,))
            if self.cursor.fetchone():
                return True 
            return False
        except Exception: 
            traceback.print_exc()
            self.conn.rollback()
            raise UserError()

    def signup(self, username, password):
        try: 
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.cursor.execute("INSERT INTO qtell.users (username, password) VALUES (%s, %s)", 
                (username, hashed_password.decode('utf-8')))
            self.conn.commit()
            return True
        except Exception:
            traceback.print_exc()
            self.conn.rollback()
            raise UserError()

    def login(self, username, password):
        try:
            self.cursor.execute("SELECT password FROM qtell.users WHERE username = %s limit 1", (username,))  
            hashed_password = self.cursor.fetchone()   
            if hashed_password and bcrypt.checkpw(password.encode('utf-8'), hashed_password[0].encode('utf-8')):
                return True 
            return False 
        except Exception:
            traceback.print_exc()
            self.conn.rollback()
            raise UserError()    
        
    def close_connection(self):
        self.conn.close()
        