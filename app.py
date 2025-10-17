from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt
from datetime import datetime, timedelta

# Flask app initialization
app = Flask(__name__)
app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/hostel_management'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=True)
    room = db.relationship('Room', backref='users')

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False)
    seater = db.Column(db.Integer, nullable=False)
    fees = db.Column(db.Float, nullable=False)

class Complaint(db.Model):
    __tablename__ = 'complaints'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complaint_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='complaints')

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='feedbacks')

class AccessLog(db.Model):
    __tablename__ = 'access_log'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    login_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='access_logs')

class MessBooking(db.Model):
    __tablename__ = 'mess_bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    menu_item = db.Column(db.String(100), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user = db.relationship('User', backref='mess_bookings')

# Create tables
with app.app_context():
    db.create_all()

# Menu items for mess booking
MENU_ITEMS = {
    'Breakfast': ['Idli', 'Dosa', 'Poha', 'Upma'],
    'Lunch': ['Rice Dal', 'Chicken Curry', 'Veg Biryani', 'Paneer Butter Masala'],
    'Dinner': ['Roti Sabzi', 'Fried Rice', 'Noodles', 'Fish Curry'],
    'Snacks': ['Samosa', 'Pakoda', 'Sandwich', 'Chips']
}

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('index.html')

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    return render_template('login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password, user.password.encode('utf-8')):
            session['user_id'] = user.id
            access_log = AccessLog(user_id=user.id)
            db.session.add(access_log)
            db.session.commit()
            flash('Login successful!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('user_login.html')

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if 'user_id' in session:
        return redirect(url_for('user_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            if existing_user.username == username:
                flash('Username already exists. Please choose another.', 'danger')
            elif existing_user.email == email:
                flash('Email is already registered. Use a different one.', 'danger')
            return redirect(url_for('user_register'))
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        new_user = User(username=username, email=email, password=password.decode('utf-8'))
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_register.html')

@app.route('/book_room', methods=['GET', 'POST'])
def book_room():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    user = User.query.get(session['user_id'])
    if user.room_id:
        booked_room = Room.query.get(user.room_id)
        return render_template('book_room.html', message="You already booked a room", rooms=None, booked_room=booked_room)
    if request.method == 'POST':
        room_id = request.form['room_id']
        room = Room.query.get(room_id)
        occupants = User.query.filter_by(room_id=room_id).count()
        if occupants < room.seater:
            user.room_id = room_id
            db.session.commit()
            flash('Room booked successfully!', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash("It's full!", 'danger')
            rooms = Room.query.all()
            rooms_with_occupants = [
                {'room': room, 'occupants': User.query.filter_by(room_id=room.id).count()}
                for room in rooms
            ]
            return render_template('book_room.html', message="Room is full!", rooms=rooms_with_occupants)
    rooms = Room.query.all()
    rooms_with_occupants = [
        {'room': room, 'occupants': User.query.filter_by(room_id=room.id).count()}
        for room in rooms
    ]
    return render_template('book_room.html', rooms=rooms_with_occupants)

@app.route('/mess_booking', methods=['GET', 'POST'])
def mess_booking():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        meal_type = request.form['meal_type']
        menu_item = request.form['menu_item']
        booking_date = request.form['booking_date']
        new_booking = MessBooking(
            user_id=session['user_id'],
            meal_type=meal_type,
            menu_item=menu_item,
            booking_date=booking_date
        )
        db.session.add(new_booking)
        db.session.commit()
        flash('Meal booked successfully!', 'success')
        return redirect(url_for('mess_booking'))
    bookings = MessBooking.query.filter_by(user_id=session['user_id']).order_by(MessBooking.created_at.desc()).all()
    today = datetime.now().date()
    dates = {
        'Today': today.strftime('%Y-%m-%d'),
        'Tomorrow': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
        'Yesterday': (today - timedelta(days=1)).strftime('%Y-%m-%d')
    }
    return render_template('mess_booking.html', menu_items=MENU_ITEMS, dates=dates, bookings=bookings)

@app.route('/admin_manage_mess', methods=['GET', 'POST'])
def admin_manage_mess():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        new_meal_type = request.form['meal_type']
        new_menu_item = request.form['menu_item']
        new_booking_date = request.form['booking_date']
        booking = MessBooking.query.get(booking_id)
        if booking:
            booking.meal_type = new_meal_type
            booking.menu_item = new_menu_item
            booking.booking_date = new_booking_date
            db.session.commit()
            flash('Mess booking updated successfully!', 'success')
        else:
            flash('Booking not found.', 'danger')
        return redirect(url_for('admin_manage_mess'))
    bookings = MessBooking.query.all()
    today = datetime.now().date()
    dates = {
        'Today': today.strftime('%Y-%m-%d'),
        'Tomorrow': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
        'Yesterday': (today - timedelta(days=1)).strftime('%Y-%m-%d')
    }
    return render_template('admin_manage_mess.html', menu_items=MENU_ITEMS, dates=dates, bookings=bookings)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')
        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.checkpw(password, admin.password.encode('utf-8')):
            session['admin_id'] = admin.id
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
    return render_template('admin_login.html')

@app.route('/user_profile')
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    user = User.query.get(session['user_id'])
    return render_template('user_profile.html', user=user)

@app.route('/user_dashboard')
def user_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    return render_template('user_dashboard.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        existing_admin = Admin.query.filter((Admin.username == username) | (Admin.email == email)).first()
        if existing_admin:
            if existing_admin.username == username:
                flash('Username already exists. Please choose another.', 'danger')
            elif existing_admin.email == email:
                flash('Email is already registered. Use a different one.', 'danger')
            return redirect(url_for('admin_register'))
        password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
        new_admin = Admin(username=username, email=email, password=password.decode('utf-8'))
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin registration successful! Please log in.', 'success')
        return redirect(url_for('admin_login'))
    return render_template('admin_register.html')

@app.route('/admin_view_complaints')
def admin_view_complaints():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    complaints = Complaint.query.all()
    return render_template('admin_view_complaints.html', complaints=complaints)

@app.route('/admin_view_feedback')
def admin_view_feedback():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    feedbacks = Feedback.query.all()
    return render_template('admin_view_feedback.html', feedbacks=feedbacks)

@app.route('/complaint', methods=['GET', 'POST'])
def complaint():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        complaint_text = request.form['complaint_text']
        new_complaint = Complaint(user_id=session['user_id'], complaint_text=complaint_text)
        db.session.add(new_complaint)
        db.session.commit()
        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('complaint.html')

@app.route('/submit_feedback', methods=['GET', 'POST'])
def submit_feedback():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        feedback_text = request.form['feedback_text']
        new_feedback = Feedback(user_id=session['user_id'], feedback_text=feedback_text)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('user_dashboard'))
    return render_template('submit_feedback.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session and 'admin_id' not in session:
        return redirect(url_for('user_login'))
    if request.method == 'POST':
        current_password = request.form['current_password'].encode('utf-8')
        new_password = request.form['new_password'].encode('utf-8')
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        else:
            user = Admin.query.get(session['admin_id'])
        if user and bcrypt.checkpw(current_password, user.password.encode('utf-8')):
            hashed_new_password = bcrypt.hashpw(new_password, bcrypt.gensalt())
            user.password = hashed_new_password.decode('utf-8')
            db.session.commit()
            flash('Password changed successfully.', 'success')
            if 'user_id' in session:
                return redirect(url_for('user_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Current password incorrect.', 'danger')
    return render_template('change_password.html')

@app.route('/access_log')
def access_log():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    logs = AccessLog.query.order_by(AccessLog.login_time.desc()).all()
    return render_template('access_log.html', logs=logs)

@app.route('/admin_profile')
def admin_profile():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    admin = Admin.query.get(session['admin_id'])
    return render_template('admin_profile.html', admin=admin)

@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))

@app.route('/user_logout')
def user_logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('user_login'))

@app.route('/room_details/<int:room_id>')
def room_details(room_id):
    if 'user_id' not in session and 'admin_id' not in session:
        return redirect(url_for('user_login'))
    room = Room.query.get_or_404(room_id)
    return render_template('room_details.html', room=room)

@app.route('/manage_rooms', methods=['GET', 'POST'])
def manage_rooms():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        room_number = request.form['room_number']
        seater = int(request.form['seater'])
        fees = float(request.form['fees'])
        new_room = Room(room_number=room_number, seater=seater, fees=fees)
        db.session.add(new_room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('manage_rooms'))
    rooms = Room.query.all()
    return render_template('manage_rooms.html', rooms=rooms)

@app.route('/student_registration', methods=['GET', 'POST'])
def student_registration():
    return redirect(url_for('user_register'))

@app.route('/view_complaints')
def view_complaints():
    if 'user_id' not in session:
        return redirect(url_for('user_login'))
    complaints = Complaint.query.filter_by(user_id=session['user_id']).all()
    return render_template('view_complaints.html', complaints=complaints)

if __name__ == '__main__':
    app.run(debug=True)