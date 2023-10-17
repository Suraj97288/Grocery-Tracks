from flask import Flask , render_template , request,session,redirect
from jinja2 import Template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func ,or_, and_


app = Flask(__name__ ,'/static')


app.secret_key = 'super secret key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Data.db"

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.String, nullable=False)
    firstname = db.Column(db.String, nullable=False)
    lastname = db.Column(db.String)
    email = db.Column(db.String ,unique = True, nullable = False)
    password = db.Column(db.String ,nullable = False)

class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    item_name = db.Column(db.String,nullable=False)
    item_cat = db.Column(db.String,nullable=False)
    item_price = db.Column(db.Integer, nullable=False)
    item_qty= db.Column(db.Integer, nullable=False)
    item_mfd = db.Column(db.Text , nullable=False)
    item_exp = db.Column(db.Text , nullable = False)
    item_image = db.Column(db.String)

class Category(db.Model):
    cat_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    cat_name = db.Column(db.String,nullable=False , unique = True)
    cat_image = db.Column(db.String)

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String , nullable = False)
    citem_name = db.Column(db.String, nullable=False)
    citem_qty = db.Column(db.Integer, nullable=False)
    citem_price = db.Column(db.Integer,nullable = False)
    citem_image = db.Column(db.String)

with app.app_context():
    db.create_all()

#rendering login
@app.route('/')
def index():
    return render_template('index.html')

#rendering registration page
@app.route('/register')
def register():
    return render_template('register.html')

#confirm modal
@app.route('/confirm')
def confirm():
    return render_template('confirmodal.html')

#rendering admin page
@app.route('/admin')
def admin():
    cats = Category.query.all()
    items = Items.query.order_by(Items.item_id.desc()).all()
    return render_template('admin.html' , items = items,cats = cats )

# rendering customer page
@app.route('/mainpage')
def mainpage():
    user = session.get('email')
    customer = User.query.filter_by(email = user).first()
    cats = Category.query.all()
    items = Items.query.order_by(Items.item_id.desc()).all()
    return render_template('mainpage.html', items=items, cats=cats , firstname = customer.firstname)

#adding item
@app.route('/add_item')
def add_item():
    category = db.session.query(Category.cat_name).all()
    return render_template('add_item.html' , category =category)

#adding category
@app.route('/add_category')
def add_cat():
    items = Category.query.all()
    return render_template('add_category.html',items = items)

#opening cart
@app.route('/cart')
def cart():
    user_email = session.get('email')
    cartitems = Cart.query.filter_by(user_email=user_email).all()
    carttotal = db.session.query(func.sum(Cart.citem_price)).filter_by(user_email=user_email).scalar()
    return render_template('cart.html' , cartitems = cartitems, carttotal = carttotal ,cartlen = len(cartitems))

#deleting item
@app.route('/delete/<item_id>')
def delete(item_id):
    item = Items.query.filter_by(item_id=item_id).first()
    citem = Cart.query.filter_by(citem_name = item.item_name )
    for citm in citem:
        db.session.delete(citm)
    db.session.delete(item)
    db.session.commit()
    items = Items.query.order_by(Items.item_id.desc()).all()
    cats = Category.query.all()
    return render_template('admin.html' , items = items ,cats = cats )

# adding item to cart

@app.route('/addtocart/<int:item_id>', methods=['POST','GET'])
def addtocart(item_id):
    cqty = int(request.form.get("cqty"))
    user_email = session.get('email')
    item = Items.query.filter_by(item_id=item_id).first()
    if cqty <= item.item_qty:
        newcartitem = Cart(user_email = user_email ,citem_name =item.item_name,citem_qty = cqty, citem_price = (item.item_price)*(cqty) , citem_image = item.item_image)
        db.session.add(newcartitem)
        db.session.commit()
        items = Items.query.order_by(Items.item_id.desc()).all()
        cats = Category.query.all()
        user = session.get('email')
        customer = User.query.filter_by(email = user).first()
        return render_template('mainpage.html' , items = items,cats = cats ,firstname = customer.firstname)
    else:
        items = Items.query.order_by(Items.item_id.desc()).all()
        cats = Category.query.all()
        user = session.get('email')
        customer = User.query.filter_by(email = user).first()
        return render_template('mainpage.html' , items = items ,cats = cats, lencart = len(items),firstname = customer.firstname )
    
#remove item from Cart

@app.route('/remove/<id>')
def remove(id):
    item = Cart.query.filter_by(id=id).first()
    db.session.delete(item)
    db.session.commit()
    return redirect('/cart' )

#updating item details

@app.route('/update/<item_id>', methods=['POST','GET'])
def update(item_id):
    if request.method == 'POST':
        item_cat = request.form.get("item_cat")
        item_name = request.form.get("item_name")
        item_price = request.form.get("item_price")
        item_mfd = request.form.get("item_mfd")
        item_exp = request.form.get("item_exp")
        item_qty= request.form.get("item_qty")
        item_image = request.form.get("item_image")
        item = Items.query.filter_by(item_id=item_id).first()
        item.item_cat = item_cat
        item.item_name = item_name
        item.item_price = item_price
        item.item_mfd = item_mfd
        item.item_exp = item_exp
        item.item_qty = item_qty
        item.item_image = item_image
        db.session.add(item)
        db.session.commit()
        items = Items.query.order_by(Items.item_id.desc()).all()
        cats = Category.query.all()
        return render_template('admin.html' , items = items,cats = cats )
    
    item = Items.query.filter_by(item_id=item_id).first()
    category = db.session.query(Category.cat_name).all()
    return render_template('update.html', item=item , category = category)

# adding new user

@app.route('/add', methods= ["POST"])
def add():  
    Type = request.form.get("Type")
    if Type == "1" :
        Type = "Customer"
    else:
        Type = "Admin"
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    email = request.form.get("email")
    password = request.form.get("password")
    newuser = User(Type= Type ,firstname=firstname , lastname= lastname , email=email , password=password )
    db.session.add(newuser)
    db.session.commit()
    return render_template('index.html')

# login

@app.route('/login' , methods = ['POST'])
def login():
    Type = request.form.get("Type")
    if Type == "1" :
        Type = "Customer"
    else:
        Type = "Admin"
    email = request.form.get("email")
    password = request.form.get("password")
    
    user = User.query.filter_by(email=email).first()
    passw = user.password
    type = user.Type

    if password==passw and Type == type:
        if Type == "Admin":
            items = Items.query.order_by(Items.item_id.desc()).all()
            cats = Category.query.all()
            return render_template('admin.html' , items = items,cats = cats )
        else:
            session['email'] = email
            items = Items.query.order_by(Items.item_id.desc()).all()
            cats = Category.query.all()
            user = session.get('email')
            customer = User.query.filter_by(email = user).first()
            return render_template("mainpage.html" ,items = items,cats = cats , firstname = customer.firstname)
    else:
        return redirect('/')

#adding items in items table

@app.route('/additem', methods= ["POST"])
def additem():  
    item_cat = request.form.get("item_cat")
    item_name = request.form.get("item_name")
    item_price = request.form.get("item_price")
    item_mfd = request.form.get("item_mfd")
    item_exp = request.form.get("item_exp")
    item_qty= request.form.get("item_qty")
    if  request.form.get("item_image") == "":
        item_image= "https://img.freepik.com/free-icon/groceries_318-889751.jpg"
    else:
        item_image = request.form.get("item_image")

    newitem = Items(item_cat= item_cat ,item_name=item_name , item_price= item_price , item_mfd=item_mfd , item_exp=item_exp ,item_qty=item_qty, item_image = item_image )
    db.session.add(newitem)
    db.session.commit()
    return redirect("/add_item")

#adding category in category table
@app.route('/addcat', methods= ["POST"])
def addcat():
    cat_name = request.form.get("cat_name")
    cat_image= request.form.get("cat_image")
    newcat = Category(cat_name = cat_name , cat_image = cat_image)
    db.session.add(newcat)
    db.session.commit()
    return redirect("/add_item")

#updating category
@app.route('/updatecat/<cat_id>', methods=['POST','GET'])
def updatecat(cat_id):
    if request.method == 'POST':
        cat_name = request.form.get("cat_name")
        cat_image= request.form.get("cat_image")
        catitem = Category.query.filter_by(cat_id=cat_id).first()
        catitem.cat_name = cat_name
        catitem.cat_image = cat_image
        db.session.add(catitem)
        db.session.commit()
        items = Category.query.all()
        return render_template('add_category.html' , items = items )

    cat = Category.query.filter_by(cat_id = cat_id).first()
    items = Category.query.all()
    return render_template('updatecat.html', cat = cat ,items = items)

#deleting category
@app.route('/deletecat/<cat_name>')
def deletecat(cat_name):
    cat = Category.query.filter_by(cat_name=cat_name).first()
    item = Items.query.filter_by(item_cat = cat_name).all()
    for itm in item:
        db.session.delete(itm)

    db.session.delete(cat)
    db.session.commit()
    items = Items.query.all()
    cats = Category.query.all()
    return render_template('admin.html' , items = items,cats = cats )

#search item
@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.form.get('search')
    if request.method=='POST':
        if query:
            items = Items.query.filter(or_(Items.item_name.ilike(f'%{query}%'),(Items.item_price.ilike(f'%{query}%')),
                                           (Items.item_mfd.ilike(f'%{query}%')),(Items.item_exp.ilike(f'%{query}%'))
                                           ,(Items.item_cat.ilike(f'%{query}%')))).all()
            cats = Category.query.filter(Category.cat_name.ilike(f'%{query}%')).all()
        else:
            items = Items.query.all()
            cats = Category.query.all()
        
        user = session.get('email')
        if user:
            customer = User.query.filter_by(email=user).first()
            return render_template("mainpage.html", items=items, cats=cats, firstname=customer.firstname)
        else:
            return render_template("mainpage.html", items=items, cats=cats)

    

#search item on admin page
@app.route('/searchadm', methods=['GET', 'POST'])
def searchadm():
    query = request.form.get('search')
    if request.method=='POST':
        if query:
            items = Items.query.filter(or_(Items.item_name.ilike(f'%{query}%'),(Items.item_price.ilike(f'%{query}%')),
                                           (Items.item_mfd.ilike(f'%{query}%')),(Items.item_exp.ilike(f'%{query}%')),(Items.item_cat.ilike(f'%{query}%')))).all()
            cats = Category.query.filter(Category.cat_name.ilike(f'%{query}%')).all()
        else:
            items = Items.query.all()
            cats = Category.query.all()
        
        return render_template("admin.html", items=items, cats=cats)


  
if __name__ == '__main__':
    app.run(debug=True)