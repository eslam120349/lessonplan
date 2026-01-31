# models.py
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.name = user_data.get('name')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.password = user_data.get('password')
        self.role = user_data.get('role') or 'student'
        self.monthly_token_quota = user_data.get('monthly_token_quota')
        self.token_balance = user_data.get('token_balance')
        self.token_renewal_date = user_data.get('token_renewal_date')
    
    @staticmethod
    def get_by_id(user_id):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('users').select("*").eq('id', user_id).single().execute()
            user = User(response.data) if response.data else None
            if user:
                user.ensure_monthly_renewal()
            return user
        except Exception as e:
            print(f"Error getting user by id: {e}")
            return None
    
    @staticmethod
    def get_by_email(email):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            response = supabase.table('users').select("*").eq('email', email).execute()
            if response.data and len(response.data) > 0:
                user = User(response.data[0])
                user.ensure_monthly_renewal()
                return user
            return None
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None
    
    @staticmethod
    def create(name, email, password):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            
            password_hash = generate_password_hash(password)
            role = 'student'
            monthly_quota = RoleConfig.get_quota_for_role(role)
            now = datetime.now(timezone.utc).isoformat()
            
            response = supabase.table('users').insert({
                'name': name,
                'email': email,
                'password_hash': password_hash,
                'password': password,
                'role': role,
                'monthly_token_quota': monthly_quota,
                'token_balance': monthly_quota,
                'token_renewal_date': now
            }).execute()
            
            return User(response.data[0]) if response.data else None
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update(self, **kwargs):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            update_data = {}
            
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                    update_data[key] = value
            
            if 'password' in update_data:
                update_data['password_hash'] = generate_password_hash(update_data['password'])
            
            if update_data:
                response = supabase.table('users').update(update_data).eq('id', self.id).execute()
                return response.data[0] if response.data else None
            return None
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    def is_admin(self):
        return (self.role or '').lower() == 'admin'

    def _month_start(self):
        now = datetime.now(timezone.utc)
        return datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    def ensure_monthly_renewal(self):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            quota = self.monthly_token_quota or RoleConfig.get_quota_for_role(self.role or 'student')
            renew = self.token_renewal_date
            renew_dt = None
            if isinstance(renew, str) and renew:
                try:
                    renew_dt = datetime.fromisoformat(renew.replace('Z', '+00:00'))
                except Exception:
                    renew_dt = None
            if not renew_dt:
                renew_dt = self._month_start()
            if renew_dt < self._month_start():
                prev_balance = self.token_balance or 0
                self.token_balance = quota
                self.monthly_token_quota = quota
                self.token_renewal_date = datetime.now(timezone.utc).isoformat()
                supabase.table('users').update({
                    'token_balance': self.token_balance,
                    'monthly_token_quota': self.monthly_token_quota,
                    'token_renewal_date': self.token_renewal_date
                }).eq('id', self.id).execute()
                change = (self.token_balance or 0) - (prev_balance or 0)
                if change != 0:
                    TokenTransaction.create(self.id, change, 'monthly_renewal', 'system', None)
        except Exception as e:
            print(f"Error in monthly renewal: {e}")

    def deduct_tokens(self, amount, reason, source=None):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            balance = self.token_balance or 0
            if amount <= 0:
                return False
            if balance < amount:
                return False
            new_balance = balance - amount
            self.token_balance = new_balance
            supabase.table('users').update({'token_balance': new_balance}).eq('id', self.id).execute()
            TokenTransaction.create(self.id, -amount, reason, source or 'app', None)
            return True
        except Exception as e:
            print(f"Error deducting tokens: {e}")
            return False

    def add_tokens(self, amount, reason, source=None):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            balance = self.token_balance or 0
            if amount <= 0:
                return False
            new_balance = balance + amount
            self.token_balance = new_balance
            supabase.table('users').update({'token_balance': new_balance}).eq('id', self.id).execute()
            TokenTransaction.create(self.id, amount, reason, source or 'app', None)
            return True
        except Exception as e:
            print(f"Error adding tokens: {e}")
            return False

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

class RoleConfig:
    @staticmethod
    def get_quota_for_role(role):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            r = supabase.table('role_configs').select("monthly_quota").eq('role', role).single().execute()
            if r.data and 'monthly_quota' in r.data:
                return int(r.data['monthly_quota'])
        except Exception:
            pass
        role_lower = (role or '').lower()
        if role_lower == 'trainer' or role_lower == 'مدرب':
            return 50
        if role_lower == 'admin':
            return 1000
        return 20

class TokenTransaction:
    def __init__(self, data):
        self.id = data.get('id')
        self.user_id = data.get('user_id')
        self.change = data.get('change')
        self.reason = data.get('reason')
        self.source = data.get('source')
        self.meta = data.get('meta')
        self.date_created = data.get('date_created')

    @staticmethod
    def create(user_id, change, reason, source, meta):
        try:
            supabase = current_app.config["SUPABASE_CLIENT"]
            supabase.table('token_transactions').insert({
                'user_id': user_id,
                'change': change,
                'reason': reason,
                'source': source,
                'meta': meta
            }).execute()
            return True
        except Exception as e:
            print(f"Error creating token transaction: {e}")
            return False
