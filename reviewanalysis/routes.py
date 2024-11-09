import secrets
import pickle
import shutil
from datetime import datetime
import os
import json
from PIL import Image
from reviewanalysis import app,db,bcrypt,mail,amazon,flipkart
from flask import render_template,flash,redirect,url_for,request,abort,send_from_directory
from reviewanalysis.forms import RegisterForm,LoginForm,UpdateAccountForm,RequestResetForm,ResetPasswordForm,ProductLink,APIGenerator,DeleteAPI,ContactUsForm
from reviewanalysis.models import Registertable,APItable,ContactUstable
from flask_login import login_user,current_user,logout_user,login_required
from flask_mail import Message
from flask import jsonify,session


@app.route("/register", methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        print("Form validation successful!")  # Add a print statement to check if form validation is successful
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        userdata = Registertable(username=form.username.data, email=form.email.data, password=hashed,api_count=0)
        db.session.add(userdata)
        db.session.commit()
        flash("Your account is created and you can login now!", 'success')
        return redirect(url_for('login'))  
    else:
        print("Form validation failed!") 
    return render_template("register.html", title="Register", form=form)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login",methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form=LoginForm()
    if form.validate_on_submit():
            userdata=Registertable.query.filter_by(email=form.email.data).first()
            if(userdata and bcrypt.check_password_hash(userdata.password,form.password.data)):
                 login_user(userdata,remember=form.remember.data)
                 next_page=request.args.get('next')
                 return redirect(next_page) if next_page else  redirect(url_for("home"))
            elif(userdata):
                flash("check your password","danger")
            else:     
                flash('Wrong Email Entered',"danger")
    return render_template("login.html",title="Login",form=form)
def save_picture(form_picture):
    random_hex=secrets.token_hex(8)
    _,f_ext=os.path.splitext(form_picture.filename)
    picture_fn=random_hex+f_ext
    picture_path=os.path.join(app.root_path,'static/pictures',picture_fn)
    output_size=(125,125)
    i=Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    
    return picture_fn

@app.route("/aboutus")
def aboutus():
     return render_template("aboutus.html")
@app.route("/contactus",methods=["POST","GET"])
def contactus():
    form=ContactUsForm()
    if form.validate_on_submit():
        userdata =ContactUstable(username=form.name.data,email=form.email.data,message=form.message.data)
        db.session.add(userdata)
        db.session.commit()
        flash("Your Message Recieved Successfully","success")
        return render_template("contactus.html",form=form)
    return render_template("contactus.html",form=form)
     

@app.route("/services")
def service():
    return render_template("services.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def send_reset_email(user):
    token=user.get_reset_token()
    msg=Message('Password Reset Request',sender="saboorabdul627@gmail.com",recipients=[user.email])
    msg.body=f''' to Rese your password visit the following link :
http://127.0.0.1:5000/{url_for('reset_token',token=token,external=True)}   
if you did not request reset then ignore this email'''
    mail.send(msg)


@app.route("/reset_password",methods=['POST','GET'])
def reset_request():
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    form=RequestResetForm()
    if form.validate_on_submit():
        user_data=Registertable.query.filter_by(email=form.email.data).first()
        send_reset_email(user_data)
        flash("check your email to reset password !","info")
        return redirect(url_for('login'))
    return render_template('resetrequest.html',form=form)

@app.route("/reset_password/<token>",methods=['POST','GET'])
def reset_token(token):
    if current_user.is_authenticated:
         return redirect(url_for('home'))
    user_data=Registertable.verify_reset_token(token)
    if user_data is None:
        flash("That is an Inavalid token the link is Expired ",'warning')
        return redirect(url_for('reset_request'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        print("Form validation successful!")  # Add a print statement to check if form validation is successful
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user_data.password=hashed
        db.session.commit()
        flash("Your Password is reset !", 'success')
        return redirect(url_for('login')) 
    return render_template('resetpassword.html',form=form)

@app.route("/api/documents")
def document():
    return render_template("documentation.html")

"""
@app.route("/amazonscrapper",methods=['POST','GET'])
@login_required
def amazonscrapper():
    form = ProductLink()
    if form.validate_on_submit(): 
        url=form.product_link._value()
        domain =amazon.get_domain(url)

        valid=amazon.validate_url(url)
        if valid==False:
            flash("Sorry the Web site Only support FlipKart or Amazon Link","danger")
            return render_template("webscrapper.html",form=form,valid=valid)
        sourcecode=amazon.get_source_code(url)
        soup=amazon.get_soup_code(sourcecode)
        try:
            total=amazon.findtotalreviewsNumber(soup) # this throw the none type error if used on the flip kart link
            text_percentages=amazon.findReviewsPercentages(soup)
            int_percentages=amazon.convertPercentageToInt(text_percentages)
            avg_rating = amazon.findavgrating(total,int_percentages)
            rating_number=amazon.getAllRatingNumber(total=total,percentages=int_percentages)
            reviews=amazon.getReviews(soup)
            helpfullness=amazon.getHelpFullness(soup,total) 
            model=amazon.load_model()
            cvec=amazon.load_vec()
            tfidf=amazon.load_tfidf()
            rating_dict=amazon.converttodict([5,4,3,2,1],rating_number)
            per_dict=amazon.converttodict([5,4,3,2,1],int_percentages)
            finalinputs=amazon.combineparameter(helpful=helpfullness,model=model,overall=avg_rating,reviewstxt=reviews,tfidf_review=tfidf,vectorizer_review=cvec)
            output=amazon.model_predict(model=model,inputs=finalinputs)
            prob_dict=amazon.find_probability(model,finalinputs)
            return render_template("webscrapper.html",form=form,valid=valid,output=output,rating_dict=rating_dict,per_dict=per_dict,prob_dict=prob_dict)
        except Exception  as e:
            flash("The web page does not contains sufficient data for Analysis","warning")
            return render_template("webscrapper.html",form=form,error="Sorry For inconvineince but the provided link does not have the Required Data for Analysis")
    flash("the form is only passed here")
    return render_template("webscrapper.html",form=form)

@app.route("/flipkartscrapper",methods=['POST','GET'])
@login_required
def flipkartscrapper():
    form = ProductLink()
    if form.validate_on_submit(): 
        url=form.product_link._value()
        domain =flipkart.get_domain(url)
        valid=amazon.validate_url(url)
        if valid==False:
            flash("Sorry the Web site Only support FlipKart or Amazon Link","danger")
            return render_template("webscrapper.html",form=form,valid=valid)
        sourcecode=amazon.get_source_code(url)
        soup=amazon.get_soup_code(sourcecode)
        try:
            total=flipkart.findtotalreviews(soup)
            review_int=flipkart.findnumberofreviews(soup)
            percent_int=flipkart.percentageconvertion(total,review_int)
            avg_rating = flipkart.findavgrating(total,percent_int)
            reviews=flipkart.getReviews(soup)
            helpfullness=flipkart.getHelpFullness(soup) 
            model=amazon.load_model()
            cvec=amazon.load_vec()
            tfidf=amazon.load_tfidf()
            rating_dict=amazon.converttodict([5,4,3,2,1],review_int)
            per_dict=amazon.converttodict([5,4,3,2,1],percent_int)
            finalinputs=amazon.combineparameter(helpful=helpfullness,model=model,overall=avg_rating,reviewstxt=reviews,tfidf_review=tfidf,vectorizer_review=cvec)
            output=amazon.model_predict(model=model,inputs=finalinputs)
            prob_dict=amazon.find_probability(model,finalinputs)
            return render_template("webscrapper.html",form=form,valid=valid,output=output,rating_dict=rating_dict,per_dict=per_dict,prob_dict=prob_dict)
        except Exception  as e:
            flash(f"The web page does not contains sufficient data for Analysis {e}","warning")
            return render_template("webscrapper.html",form=form,error="Sorry For inconvineince but the provided link does not have the Required Data for Analysis")
    flash("the form is only passed here","warning")
    return render_template("webscrapper.html",form=form)
"""


@app.route("/scrapper", methods=['POST', 'GET'])
@login_required
def scrapper():
    form = ProductLink()
    if form.validate_on_submit():
        url = form.product_link._value()
        domain = amazon.get_domain(url) if "amazon" in url else flipkart.get_domain(url)
        
        # Validate URL
        valid = amazon.validate_url(url) if "amazon" in url else flipkart.validate_url(url)
        if not valid:
            flash("Sorry, the website only supports Flipkart or Amazon links", "danger")
            return render_template("webscrapper.html", form=form, valid=valid)
        
        # Fetch source code and parse
        sourcecode = amazon.get_source_code(url)
        soup = amazon.get_soup_code(sourcecode)
        
        try:
            # Process based on domain
            if "amazon" in domain:
                # Amazon-specific functions
                total = amazon.findtotalreviewsNumber(soup)
                text_percentages = amazon.findReviewsPercentages(soup)
                int_percentages = amazon.convertPercentageToInt(text_percentages)
                avg_rating = amazon.findavgrating(total, int_percentages)
                rating_number = amazon.getAllRatingNumber(total=total, percentages=int_percentages)
                reviews = amazon.getReviews(soup)
                helpfullness = amazon.getHelpFullness(soup, total)
            elif "flipkart" in domain:
                # Flipkart-specific functions
                total = flipkart.findtotalreviews(soup)
                review_int = flipkart.findnumberofreviews(soup)
                percent_int = flipkart.percentageconvertion(total, review_int)
                avg_rating = flipkart.findavgrating(total, percent_int)
                reviews = flipkart.getReviews(soup)
                helpfullness = flipkart.getHelpFullness(soup)
                rating_number = review_int
                int_percentages = percent_int

            # Load model and transform features
            model = amazon.load_model()
            cvec = amazon.load_vec()
            tfidf = amazon.load_tfidf()
            rating_dict = amazon.converttodict([5, 4, 3, 2, 1], rating_number)
            per_dict = amazon.converttodict([5, 4, 3, 2, 1], int_percentages)
            finalinputs = amazon.combineparameter(helpful=helpfullness, model=model, overall=avg_rating,
                                                  reviewstxt=reviews, tfidf_review=tfidf, vectorizer_review=cvec)
            output = amazon.model_predict(model=model, inputs=finalinputs)
            prob_dict = amazon.find_probability(model, finalinputs)

            return render_template("webscrapper.html", form=form, valid=valid, output=output,
                                   rating_dict=rating_dict, per_dict=per_dict, prob_dict=prob_dict)
        
        except Exception as e:
            flash(f"The web page does not contain sufficient data for analysis{e}", "warning")
            return render_template("webscrapper.html", form=form,
                                   error="Sorry for the inconvenience, but the provided link does not have the required data for analysis")
    
    # If form is not validated or no link is submitted
    return render_template("webscrapper.html", form=form)

@app.route("/api", methods=['POST', 'GET'])
@login_required
def api():
    form = APIGenerator()
    user=current_user
    if form.validate_on_submit():
        if user.api_count >= 5:
            flash("You have reached the limit of 5 APIs.", "warning")
            return render_template("api.html",form=form)
        api_key = secrets.token_hex(16)
        new_api = APItable(
            user_id=current_user.id,  # Link the API key to the logged-in user
            api_key=api_key,
            created_at=datetime.utcnow(),  # Set the creation time
            status='active',  # Set the default status to 'active'
            usage_count=0  # Initialize usage count to 0
        )
        # created a api
        db.session.add(new_api)
        db.session.commit()
        # update the api count
        user.api_count += 1
        db.session.commit()
        flash("New API Generated Successfully  !!! Please make sure to Not lose this API you wont be able to access it again","success")
        return render_template("api.html",form=form,api_key=api_key)
    return render_template("api.html",form=form)

@app.route("/api/manageapi", methods=['POST', 'GET'])
@login_required
def manageapi():
    user_api=APItable.query.all()
    form= DeleteAPI()
    
    return render_template("manageapi.html",user_api=user_api,form=form)
@app.route("/api/manageapi/delete<int:id>", methods=["POST", "GET"])
@login_required
def deleteapi(id):
    try:
        api = APItable.query.get(id)
        if not api:
            flash("API key not found.", "error")
            return redirect(url_for('manageapi'))
        
        # Delete the API entry
        db.session.delete(api)
        
        # Update the usage count for the user who owns the API
        current_user.api_count -= 1  # Adjust as needed, e.g., increment or decrement
        db.session.commit()
        
        flash(f"Successfully deleted the API {api.api_key}", "success")
    
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the API key.", "error")
        print(e)  # or log the error as needed
    
    return redirect(url_for('manageapi'))

#   api routes :


@app.route("/api/scrapper", methods=["POST", "GET"])
def scrapperapi():
    api_key = request.args.get("api_key")
    key_record = APItable.query.filter_by(api_key=api_key).first()
    if key_record is None:
        return jsonify({"status": "error", "message": "Invalid API"}), 400
    key_record.usage_count += 1
    db.session.commit()  
    url = request.args.get("url")
    domain = amazon.get_domain(url) if "amazon" in url else flipkart.get_domain(url)
    
    # Validate URL format
    valid = amazon.validate_url(url) if "amazon" in url else flipkart.validate_url(url)
    if not valid:
        return jsonify({"status": "error", "message": "Invalid URL", "reason": "the scrapper works only on flipkart and amazon"}), 400

    sourcecode = amazon.get_source_code(url)
    soup = amazon.get_soup_code(sourcecode)

    try:
        if "amazon" in domain:
            total = amazon.findtotalreviewsNumber(soup)
            text_percentages = amazon.findReviewsPercentages(soup)
            int_percentages = amazon.convertPercentageToInt(text_percentages)
            avg_rating = amazon.findavgrating(total, int_percentages)
            rating_number = amazon.getAllRatingNumber(total=total, percentages=int_percentages)
            reviews = amazon.getReviews(soup)
            helpfullness = amazon.getHelpFullness(soup, total)
        elif "flipkart" in domain:
            total = flipkart.findtotalreviews(soup)
            review_int = flipkart.findnumberofreviews(soup)
            percent_int = flipkart.percentageconvertion(total, review_int)
            avg_rating = flipkart.findavgrating(total, percent_int)
            reviews = flipkart.getReviews(soup)
            helpfullness = flipkart.getHelpFullness(soup)
            rating_number = review_int
            int_percentages = percent_int

        # Pre-load the model and vectorizer only once
        model = amazon.load_model()
        cvec = amazon.load_vec()
        tfidf = amazon.load_tfidf()

        rating_dict = amazon.converttodict([5, 4, 3, 2, 1], rating_number)
        per_dict = amazon.converttodict([5, 4, 3, 2, 1], int_percentages)

        finalinputs = amazon.combineparameter(helpful=helpfullness, model=model, overall=avg_rating,
                                              reviewstxt=reviews, tfidf_review=tfidf, vectorizer_review=cvec)

        output = amazon.model_predict(model=model, inputs=finalinputs)
        prob_dict = amazon.find_probability(model, finalinputs)

        output_dict = {
            "status": "success",
            "output": output,
            "rating_dict": rating_dict,
            "percent_dict": per_dict,
            "probability_dict": prob_dict
        }
        return jsonify(output_dict)

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/product_data", methods=['POST', "GET"])
def product_data_api():
    api_key = request.args.get("api_key")
    key_record = APItable.query.filter_by(api_key=api_key).first()
    if key_record is None:
        return jsonify({"status": "error", "message": "Invalid API"}), 400
    key_record.usage_count += 1
    db.session.commit()  

    try:
        url = request.args.get("url")
        domain = amazon.get_domain(url) if "amazon" in url else flipkart.get_domain(url)

        if domain == "amazon":
            source_code = amazon.get_source_code(url)
            soup = amazon.get_soup_code(source_code)
            title = amazon.get_product_title(soup)
            price = amazon.get_product_price(soup)
            total = amazon.findtotalreviewsNumber(soup)
            text_percentages = amazon.findReviewsPercentages(soup)
            int_percentages = amazon.convertPercentageToInt(text_percentages)
            rating = amazon.findavgrating(total, int_percentages)

        elif domain == "flipkart":
            source_code = flipkart.get_source_code(url)
            soup = flipkart.get_soup_code(source_code)
            title = flipkart.get_product_title(soup)
            price = flipkart.get_product_price(soup)
            total = flipkart.findtotalreviews(soup)
            review_int = flipkart.findnumberofreviews(soup)
            percent_int = flipkart.percentageconvertion(total, review_int)
            rating = flipkart.findavgrating(total, percent_int)

        product_data = {
            "title": title,
            "price": price,
            "rating": rating,
            "reviews_count": total,
        }

        return jsonify({
            "status": "success",
            "product_data": product_data
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })
