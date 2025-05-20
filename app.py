from flask import Flask, render_template, request, redirect, session
from models.user import db, User, UserProfile
from forms import LoginForm, Userprofileform

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Tarakonas009.@localhost:3306/puslapis'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

db.init_app(app)

with app.app_context():
    db.create_all()
  
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = LoginForm()
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            return "Email already exists"
        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
       

        session['user_id'] = new_user.id
        return redirect('/register/step2')
    
    return render_template('register.html', form=form)


@app.route('/register/step2', methods=['GET', 'POST'])
def register_step2():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/register')
    
    form = Userprofileform()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        user_profile = UserProfile(
            user_id=user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            address=form.address.data,
            phone_number=form.phone_number.data
        )
        db.session.add(user_profile)
        db.session.commit()
        
        return "Registration successful"
    
    return render_template('register/step2.html', form=form)

@app.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    user = User.query.get(user_id)
    if not user:
        return redirect('/login')
    
    profile = user.profile
    db.session.add_all([profile])

    return render_template('profile.html', user=user, profile=profile)

@app.route('/user_menu')
def user_menu():
    return render_template('profile.html')

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')
    
    user = User.query.get(user_id)
    profile = user.profile

    form = Userprofileform(obj=profile)

    if form.validate_on_submit():
        if not profile:
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)

        form.populate_obj(profile)
        db.session.commit()

        return "Saved"

    return render_template('edit_profile.html', form=form)












@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(password=form.password.data, email=form.email.data).first()
        
        
        if user:
            session['user_id'] = user.id
            return redirect('/profile')
        else:
            return "Invalid credentials"
    return render_template('login.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
                
                            
                    
