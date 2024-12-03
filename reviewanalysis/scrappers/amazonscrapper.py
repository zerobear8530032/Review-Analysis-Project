from bs4 import BeautifulSoup
import pandas 
import pickle
import requests
import matplotlib.pyplot as plt
import math
import string
import numpy as np
import sys
import os
import base64
import io
import tldextract
from scipy.sparse import hstack
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import seaborn as sns
stop = stopwords.words('english')

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from exceptions import unabletoparseException, insufficientDataException,invalidurlException

class AmazonScrapper:
    def validate_url(self,url:str)->bool:
        tld=tldextract.extract(url)
        return tld.domain in ["amazon","flipkart"]
    def get_domain(self,url:str)->bool:
        tld=tldextract.extract(url)
        return tld.domain
    def get_source_code(self,url:str)->str:
        """this function will get url and return source code in str to parse of the url"""
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.flipkart.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "max-age=0",
        "Accept-Charset": "UTF-8,*;q=0.5",
        "DNT": "1",
        "TE": "Trailers",
        "Upgrade-Insecure-Requests": "1",
        "Origin": "https://www.flipkart.com",
        "X-Requested-With": "XMLHttpRequest",
        }

        try :
            sourcecode= requests.get(url,headers=headers).text
            return sourcecode
        except Exception as e:
            print(f"An error occurred: {e}")
    def get_soup_code(self, source_code:str,source_parser="lxml")->BeautifulSoup:
        """convert the source code to beautiful soup source code """
        return  BeautifulSoup(source_code,source_parser);        
    def findtotalreviewsNumber(self,soup:BeautifulSoup)->str:
        """find the total number of reviews avaible on the product"""
        # get the review text
        review_count_tag = soup.find("span", {"data-hook": "total-review-count"})
        if review_count_tag is None:
            raise ValueError("Review count not found on the page.")
        try:
            num = review_count_tag.text.split()[0]  # Extract first part of the text (number)
        except AttributeError:
            raise ValueError("Error parsing review count text.")
        # split the text to extract numbers
        num=review_count_tag.text.split()[0]   
        ans=0
        # convert the text to integer
        for x in num:
            if x.isnumeric():
                ans=ans*10+int(x)
            if(x==' '):
                break
        return ans
    # this convert the number to percentage:
    def convertnumbertopercentage(self,total,percent):
        """this function return the percentage from number"""
        return total*(percent/100);

    def findavgrating(self,total,percentages:list)->int:
        """this function evaluate  the average rating of a product  """
        rating=0 # rating
# length of percentage
        n= len(percentages) 
        # if none means its empty
        for i,per in enumerate(percentages):# here we iterate over entire percentage list and multiply it with correspionding stars and sum them a
            rating=rating+(self.convertnumbertopercentage(total,per)*(n-i))/total
        # return ans:
        return rating
        
    def getAllRatingNumber(self,total, percentages):
        # convert the rating % to number
        return [self.convertnumbertopercentage(total, p) for p in percentages]
    # plot labels and % or rating distribution in the bar chart
    # def percentagePlot(self, labels: list, percentages: list):
    #     """Plot the % on y-axis and labels on x-axis and save as an image file."""
    #     plt.style.use("dark_background")
    #     fig, ax = plt.subplots(figsize=(10, 6))
    #     ax.grid(True)
    #     ax.bar(labels, percentages, color="skyblue")
    #     ax.set_xlabel("Stars")
    #     ax.set_ylabel("Percentage (%)")
    #     ax.set_title("Percentage Plot")
    #     ax.set_ylim(0, 100)

    #     # Save plot to a temporary file
    #     file_path = os.path.join(self.TEMP_DIR, 'percentage_plot.png')
    #     fig.savefig(file_path, format='png', bbox_inches="tight")
    #     plt.close(fig)  # Close the figure to free memory

    #     return file_path

    # def reviewNumberPlot(self, labels: list, reviews: list):
    #     """Plot number of reviews and labels and save as an image file."""
    #     plt.style.use("dark_background")
    #     fig, ax = plt.subplots(figsize=(10, 6))
    #     ax.grid(True)
    #     ax.bar(labels, reviews, color="skyblue")
    #     ax.set_xlabel("Stars")
    #     ax.set_ylabel("Rating (%)")
    #     ax.set_title("Rating Plot")
    #     ax.set_ylim(0, 100)

    #     # Save plot to a temporary file
    #     file_path = os.path.join(self.TEMP_DIR, 'rating_plot.png')
    #     fig.savefig(file_path, format='png', bbox_inches="tight")
    #     plt.close(fig)  # Close the figure to free memory

    #     return file_path

    def findReviewsPercentages(self,soup:BeautifulSoup):
        """scrap the  percentages distribution """ 
        div=soup.find("div",class_="a-section a-spacing-none a-text-right aok-nowrap")
        spans=div.find_all("span") 
        return  [x.text for x in spans]
            
    
    def convertPercentageToInt(self,strlist:[str]):
        "convert the % str to integer"
        return [int(x[:-1]) for x in  strlist]
    

    def converttonumber (self, num:str):
        n=0;
        for x in num:
            if x.isnumeric():
                n=n*10+int(x);
        return n;

    def get_product_price(self,soup:BeautifulSoup)->int:
        price_tag=soup.find("span",class_="a-price-whole")
        if price_tag==None:
            raise ValueError("Cant Find Price of Product")
        return self.converttonumber(price_tag.text)

    def get_product_title(self,soup:BeautifulSoup)->str:
        title_tag=soup.find("span",id="productTitle")
        if title_tag==None:
            raise ValueError("Cant Find Title of Product")
        name=title_tag.text.strip()
        return name
    

    def getReviews(self,soup:BeautifulSoup):
        """scrap reviews """

        reviews=soup.find_all("div",class_="a-row a-spacing-small review-data")
        if len(reviews)==0:
            raise ValueError("this is value error from getReviews")
        return [x.text for x in reviews]

    #  get helpfulness:
    def getHelpFull(self,soup):
        """extract helpfullness of reviews"""
        helpfultxt=[x.text for x in soup.find_all("span",{"data-hook":"helpful-vote-statement"})]
        ans=[]
        for x in helpfultxt:
            splitxt=x.split()[0]
            if splitxt.isnumeric():
                ans.append(int(splitxt))
            else:
                ans.append(0)
        return ans

    def getHelpFullness(self,soup,total:int):
        return [(x/total)*100 for x in self.getHelpFull(soup)]
    
    def load_model(self,path="picklefiles/logisticregression.pkl"):
        """load the model """
        with open(path, 'rb') as model_file:
            model = pickle.load(model_file)
            return model
    def load_vec(self,path="picklefiles/vectorizer_review.pkl"):
        """load the vectorizer """
        with open(path, 'rb') as review_vec_file:
            vectorizer_review = pickle.load(review_vec_file)
            return vectorizer_review
    def load_tfidf(self,path="picklefiles/tfidf_review.pkl"):
        """load the tfidc vectorizer """
        with open(path, 'rb') as tfidf_review_file:
            tfidf_review = pickle.load(tfidf_review_file)
            return tfidf_review
    def lowercase(self,s:str)->str:
        """function to convert to lower case""" 
        return s.lower()
    def removepunctuations(self,s: str) -> str:
        """function to remove punctuations """
        # Create translation table to replace punctuation with spaces
        translation_table = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
        # Remove punctuation using the translation table
        return s.translate(translation_table)
    def removestopwords(self,s: str, stop: set=stop) -> str:
        """function to remove punctuations"""
        return ' '.join([word for word in s.split() if word not in stop])
    def applylemmatizer(self,s:str)->[str]:
        """apply lemmatizer"""
        lemmatizer = WordNetLemmatizer()
        return ' '.join([lemmatizer.lemmatize(s) for s in s.split()])
    def applycountvector(self,s: str, vectorizer: CountVectorizer) -> any:
        """apply counter vector"""
        return vectorizer.transform([s])
    def applyTFIDFvector(self,s: str, vectorizer: TfidfVectorizer) -> any:
        """apply tfidf vector"""
        return vectorizer.transform([s])

    
    def combineparameters (self,x_tfidf_review,x_cvec_review):
        """combined all  the parameters"""
        return hstack([x_tfidf_review,x_cvec_review])


    def applydatapreprocessing(self,s:str,cvector:CountVectorizer,tfidf:TfidfVectorizer)->any:
        """apply full preprocessing at once"""
        s=self.lowercase(s)
        s=self.removepunctuations(s)
        s=self.removestopwords(s)
        s=self.applylemmatizer(s)
        s_vec=self.applycountvector(s,cvector)
        s_tfidf=self.applyTFIDFvector(s,tfidf)
        return hstack([s_tfidf,s_vec])
    def findmaxoccurences(self,outputs:list):
        """find max occurence of label from the reviews """
        pos=0;
        neg=0;
        neu=0;
        for x in outputs:
            if x==1:
                pos+=1;
            if x==0:
                neu+=1;
            if x==-1:
                neg+=1;
        if pos==0 and neg==0 and neu==0:
            raise  ValueError
        if(pos>neg and pos>neu):
            return "Positive" 
        elif(neg>pos and neg>neu):
            return "Negative"
        else:
            return "Neutral"

    def findpredictions(self,model:any,inputs:list)->list:
        """return the number of list of predictions from reviews"""
        return [model.predict(x) for x in inputs]
    
    def model_predict(self,model,inputs):
        outputs=self.findpredictions(model,inputs)
        return self.findmaxoccurences(outputs)
    
    def converttodict(self,lables:str,values:int)->dict:
        if (len(lables)==len(values)):
            ans=[]
            for x,y in zip(lables,values):
                ans.append({"label":x, "value":y})
            return ans
    def combineparameter(self,model,overall,reviewstxt,helpful:list,vectorizer_review,tfidf_review):
        """this function will preprocess data and give the output to be feed to the model"""
        pre_processed_data=[self.applydatapreprocessing(x,vectorizer_review,tfidf_review) for x in reviewstxt]
        # inputs=[hstack([overall,helpful,pre_processed_data[i]]) for i,data in enumerate(helpful)]
        inputs=[]
        for i,data in enumerate(pre_processed_data):
            if i>=len(helpful):
                break
            inputs.append(hstack([overall,helpful[i],data]))

        return inputs
    def find_probability(self,model,inputs):
        probabilities = [model.predict_proba(input) for input in inputs]
        neg=0
        neu=0
        pos=0
        for i, prob in enumerate(probabilities):
            for class_label, p in zip(model.classes_, prob[0]):  # prob[0] is for the first (or only) sample
                if(class_label==np.int64(-1)):
                    neg+=p
                if(class_label==np.int64(0)):
                    neu+=p
                if(class_label==np.int64(1)):
                    pos+=p           
        neg_value = (neg / len(probabilities))*100 if len(probabilities) > 0 else 0
        neu_value = (neu / len(probabilities))*100 if len(probabilities) > 0 else 0
        pos_value = (pos / len(probabilities))*100 if len(probabilities) > 0 else 0

        # Return sentiment proportions
        result = [
        {"label": "negative", "value": f"{neg_value:.4f}"},
        {"label": "neutral", "value": f"{neu_value:.4f}"},
        {"label": "positive", "value": f"{pos_value:.4f}"}
        ]
        return result





    
if __name__=="__main":
    a=AmazonScrapper()
    # print(a.get_source_code("https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4?pid=MOBGTAGPTB3VS24W&lid=LSTMOBGTAGPTB3VS24WVZNSC6&marketplace=FLIPKART&q=iphone&store=tyy%2F4io&spotlightTagId=BestsellerId_tyy%2F4io&srno=s_1_1&otracker=search&otracker1=search&fm=Search&iid=25a57b7f-4bf6-4891-8dd8-be541b7d9d92.MOBGTAGPTB3VS24W.SEARCH&ppt=sp&ppn=sp&ssid=ees1v7rrog0000001730139836292&qH=0b3f45b266a97d70"))
    sourcecode =""
    with open("class_test/file.txt", "r", encoding="utf-8") as f:
        sourcecode = f.read()
    if(sourcecode ==""):
        print("their is nothing in sourcecode")
    soup=a.get_soup_code(sourcecode)
        
    total_reviews=a.findtotalreviewsNumber(soup)
    # print(total_reviews)
    a.percentagePlot(  labels=[5,4,3,2,1], percentages=a.convertPercentageToInt(a.findReviewsPercentages(soup)))
