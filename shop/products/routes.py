from flask import Blueprint, abort, render_template, request, redirect, url_for, flash, session
from .models import Brand, Category
from shop import db, photos, create_app
from shop.products.forms import Addproducts
from shop.products.models import AddProduct, ProductImage
from werkzeug.utils import secure_filename

products = Blueprint("products", __name__)

@products.route('addbrand/', methods=['GET', 'POST'])
def addbrand():
    return add_item('brand', Brand, 'products/addbrand_category.html')

@products.route('addcategory/', methods=['GET', 'POST'])
def addcategory():
    return add_item('category', Category, 'products/addbrand_category.html')

def add_item(item_type, model, template):
    if request.method == "POST":
        name = request.form.get(item_type)
        item = model(name=name)
        db.session.add(item)
        flash(f'The {item_type.capitalize()} {name} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for(f'products.add{item_type}'))

    return render_template(template, item_type=item_type)


@products.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def update_brand(id):
    if 'email' not in session:
        flash("Please login first", 'danger')
        return redirect(url_for('admin.login'))
    
    updatebrand= Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'The brand has been updated', 'success')
        db.session.commit()
        return redirect(url_for('admin.brands'))

    return render_template('products/update_item.html', title='Update Brand Page')

# Function to check if the file extension is allowed
def allowed_file(filename):
    app = create_app()
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@products.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    brands = Brand.query.all()
    categories = Category.query.all()
    form = Addproducts(request.form)
    
    if request.method == 'POST' and form.validate(): 
        name=form.name.data
        price=form.price.data
        discount=form.discount.data
        stock=form.stock.data
        description=form.description.data
        colors=form.colors.data
        brand=request.form.get('brand')
        category=request.form.get('category')
        new_product =AddProduct(name=name, price=price, discount= discount, stock=stock, colors= colors,
                                description=description, brand_id=brand, category_id=category)
        
        images = request.files.getlist('images')
        for i, file in enumerate(images, start=1):
            # Validate file type
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                photos.save(file, name=filename)

                # Create a ProductImage instance for each uploaded image
                new_image = ProductImage(filename=filename)
                new_product.images.append(new_image)
            else:
                flash(f'Invalid file type for {file.name}. Only jpg, png, and jpeg are allowed.', 'danger')
                return render_template('products/addproduct.html', title='Add product page', form=form, brands=brands, categories=categories)
        
            # Continue with creating the new product
            db.session.add(new_product)
            flash(f'The product {form.name.data} was added to your database', 'success')
            db.session.commit()
            return redirect(url_for('products.addproduct'))
    else:
        print("Form validation failed:", form.errors)
    return render_template('products/addproduct.html', title='Add product page', form=form, brands=brands, categories=categories)