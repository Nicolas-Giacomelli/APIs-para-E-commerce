from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user


login_manager = LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'minhachave123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecomerce.db'

db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)
#modelagem
#Usuario (id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    cart = db.relationship('cartItem', backref='user', lazy=True)

#produto (id, name, price, description)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

class cartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId  =   db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    productId  =   db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

#autenticação de usuario
@login_manager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=["POST"])
def login():
    data = request.json
    data.get("username")

    user = User.query.filter_by(username=data.get("username")).first()
    if user and data.get("password") == user.password:
        login_user(user)
        return jsonify({"message":"Logged in succesfully"}), 200
    return jsonify({"message": "Unauthorized. Invalid credentials"}),401

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message":"Logout succesfully"})

#Definindo Rota de adição de produto
@app.route('/api/products/add', methods=["POST"])
@login_required
def addProduct():
    data = request.json
    #verificando se nome e preco estão preenchidos, caso não 
    if 'name' in data and 'price' in data:
    #data[tag] <- campos obrigatórios, se nao preenchidos da erro
    #data.get[tag, preenchimento] <- campos nao obrigatórios, se nao encontrar vai inserir o que colocarmos após a virgula
        product = Product(name=data["name"],price=data["price"],description=data.get("description",""))
    #adicionando produto no database
        db.session.add(product)
        db.session.commit()
        return jsonify({"message":"Product added succesfully"}), 200
    return jsonify({"message":"Invalid Product data"}), 400

@app.route('/api/products/delete/<int:product_id>',methods=["DELETE"])
@login_required
def deleteProduct(product_id):
    #recuperar o produto do db
    product = Product.query.get(product_id)
    #verificar se o produto existe
    #se existe apagar do db
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message":"Product deleted succesfully"}),200
    #se nao existe retornar 404
    return jsonify({"message":"Product not found"}),404


@app.route('/api/products/<int:product_id>',methods=["GET"])
def getProductDetails(product_id):
    #recuperar o produto do db
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })
    return jsonify({"message":"Product not found"}),404

@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def updateProduct(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message":"Product not found"}),404
    
    data = request.json
    if 'name' in data:
        product.name = data['name']

    if 'price' in data:
        product.price = data['price']
    
    if 'description' in data:
        product.description = data['description']
    
    db.session.commit()
    return jsonify({"message":"Product updated succesfully"}), 200

@app.route('/api/products', methods=["GET"])
def getProducts():
    products = Product.query.all()
    productList = []
    for product in products:
        productData = {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        productList.append(productData)
    return jsonify(productList)


@app.route('/')
def teste():
    return 'Teste'

if __name__ == "__main__":
    app.run(debug=True)