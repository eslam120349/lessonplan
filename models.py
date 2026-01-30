# models.py
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.password = user_data.get('password')  # Plain password (NOT RECOMMENDED!)
    
    @staticmethod
    def get_by_id(user_id):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('users').select("*").eq('id', user_id).single().execute()
            return User(response.data) if response.data else None
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('users').select("*").eq('email', email).execute()
            if response.data and len(response.data) > 0:
                return User(response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def create(name, email, password):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            
            password_hash = generate_password_hash(password)
            
            # Insert into public.users table
            # WARNING: Storing plain password is a SECURITY RISK!
            response = supabase.table('users').insert({
                'name': name,
                'email': email,
                'password_hash': password_hash,
                'password': password  # Plain password (NOT RECOMMENDED!)
            }).execute()
            
            return User(response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update(self, **kwargs):
        """Update user fields"""
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            update_data = {}
            
            # Only update fields that are provided
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    update_data[key] = value
            
            # If password is being updated, also update password_hash
            if 'password' in update_data:
                update_data['password_hash'] = generate_password_hash(update_data['password'])
            
            if update_data:
                response = supabase.table('users').update(update_data).eq('id', self.id).execute()
                return response.data[0] if response.data else None
            return None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

class Lesson:
    def __init__(self, lesson_data):
        self.id = lesson_data.get('id')
        self.user_id = lesson_data.get('user_id')
        self.grade_level = lesson_data.get('grade_level')
        self.topic = lesson_data.get('topic')
        self.teaching_strategy = lesson_data.get('teaching_strategy')
        self.language = lesson_data.get('language')
        self.generated_plan = lesson_data.get('generated_plan')
        self.gpt_plan = lesson_data.get('gpt_plan')
        self.date_created = lesson_data.get('date_created')
        self.date_modified = lesson_data.get('date_modified')
    
    @staticmethod
    def create(user_id, grade_level, topic, teaching_strategy, language, generated_plan=None, gpt_plan=None):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('lessons').insert({
                'user_id': user_id,
                'grade_level': grade_level,
                'topic': topic,
                'teaching_strategy': teaching_strategy,
                'language': language,
                'generated_plan': generated_plan,
                'gpt_plan': gpt_plan
            }).execute()
            return Lesson(response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error creating lesson: {e}")
            return None
    
    @staticmethod
    def get_all_by_user(user_id):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('lessons').select("*").eq('user_id', user_id).order('date_created', desc=True).execute()
            return [Lesson(item) for item in response.data]
        except Exception as e:
            print(f"Error getting lessons: {e}")
            return []
    
    @staticmethod
    def get_by_id(lesson_id):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('lessons').select("*").eq('id', lesson_id).single().execute()
            return Lesson(response.data) if response.data else None
        except Exception as e:
            print(f"Error getting lesson: {e}")
            return None
    
    def update(self, **kwargs):
        """Update lesson fields"""
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            update_data = {}
            
            # Only update fields that are provided
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    update_data[key] = value
            
            if update_data:
                response = supabase.table('lessons').update(update_data).eq('id', self.id).execute()
                return response.data[0] if response.data else None
            return None
        except Exception as e:
            print(f"Error updating lesson: {e}")
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'grade_level': self.grade_level,
            'topic': self.topic,
            'teaching_strategy': self.teaching_strategy,
            'language': self.language,
            'generated_plan': self.generated_plan,
            'gpt_plan': self.gpt_plan,
            'date_created': self.date_created,
            'date_modified': self.date_modified
        }

class Presentation:
    def __init__(self, presentation_data):
        self.id = presentation_data.get('id')
        self.lesson_id = presentation_data.get('lesson_id')
        self.file_path = presentation_data.get('file_path')
        self.date_created = presentation_data.get('date_created')
    
    @staticmethod
    def create(lesson_id, file_path):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('presentations').insert({
                'lesson_id': lesson_id,
                'file_path': file_path
            }).execute()
            return Presentation(response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error creating presentation: {e}")
            return None
    
    @staticmethod
    def get_by_lesson(lesson_id):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('presentations').select("*").eq('lesson_id', lesson_id).execute()
            return [Presentation(item) for item in response.data]
        except Exception as e:
            print(f"Error getting presentations: {e}")
            return []
    
    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'file_path': self.file_path,
            'date_created': self.date_created
        }