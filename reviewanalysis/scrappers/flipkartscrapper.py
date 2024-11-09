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

class FlipKartScrapper:
    def validate_url(self,url:str)->bool:
        """validate url belongs to flip kart or amazon"""
        tld=tldextract.extract(url)
        return tld.domain in ["amazon","flipkart"]
    def get_domain(self,url:str)->bool:
        """return the domain of the url """
        tld=tldextract.extract(url)
        return tld.domain
    def get_source_code(self,url:str)->str:
        """this function will get url and return source code in str to parse of the url"""
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.flipkart.com/",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Connection": "keep-alive"}
        try :
            sourcecode= requests.get(url,headers=headers).text
            return sourcecode
        except Exception as e:
            print(f"An error occurred: {e}")
    def get_soup_code(self, source_code:str,source_parser="lxml")->BeautifulSoup:
        """convert the source code to beautiful soup source code """
        return  BeautifulSoup(source_code,source_parser)  
    def findtotalreviews(self,soup):
        """get the total reviews of the product """
        review_count_tag = soup.find("div", class_= "row j-aW8Z")
        if review_count_tag is None:
            raise ValueError("Cannot Found Review on the Page")
        try:
            num = review_count_tag.text.split()[0]  # Extract first part of the text (number)
        except AttributeError:
            raise ValueError("Error parsing review count text.")
        num=review_count_tag.text.split()[0]
        ans=0
        for x in num:
            if x.isnumeric():
                ans=ans*10+int(x)
            if(x==' '):
                break
        return ans
    def converttonumber (self,num:str):
        """convert the string int to integer number"""
        n=0
        for x in num:
            if x.isnumeric():
                n=n*10+int(x)
        return n
    


    def get_product_title(self,soup:BeautifulSoup)->str:
        title_tag=soup.find("span",class_="VU-ZEz")
        if title_tag==None:
            raise ValueError("cannot find product title ")
        name=title_tag.text
        return name.strip()
    def get_product_price(self,soup:BeautifulSoup)->str:
        price_tag=soup.find("div",class_="Nx9bqj CxhGGd yKS4la")
        if price_tag==None:
            price_tag=soup.find("div",class_="Nx9bqj CxhGGd")
            if price_tag==None:
                raise ValueError("cannot find product price ")
        return self.converttonumber(price_tag.text)
    def findnumberofreviews(self,soup)->list:
        """get the number of reviews in a list"""        
        reviewstags= soup.find("ul",class_="+psZUR")
        if reviewstags==None:
            raise ValueError("cannot found Enough review comments to analyze product")
        reviewsnumber=reviewstags.find_all("li",class_="fQ-FC1")
        return [self.converttonumber(review.text) for review in reviewsnumber]
    
    def findavgrating(self,total,percentages:list)->int:
        rating=0
        n= len(percentages)
        if len(percentages)==0:
            print("no percentage found")
        for i,per in enumerate(percentages):
            rating=rating+(self.findnumberofreviews(total,per)*(n-i))/total
            
        return rating
        
    def getAllRatingNumber(self,total, percentages):
        return [self.findnumberofreviews(total, p) for p in percentages]
    def percentageconvertion(self,total:int,totalreviews:list):
        return [(x/total)*100 for x in totalreviews]
    
    def percentagePlot(self,labels:list,percentages:list):
        plt.figure(figsize=(10, 6))
        plt.grid(True)
        plt.bar(labels, percentages, color="skyblue")
        plt.xlabel("Stars")
        plt.ylabel("Percentage (%)")
        plt.title("Percentage Plot")
        plt.ylim(0, 100)
        plt.show()
    def globalPlot(self,labels:list,reviews:list):
        plt.figure(figsize=(10, 6))
        plt.bar(labels, reviews)
        plt.grid(True)
        plt.xlabel("Stars")
        plt.ylabel("Review")
        plt.title("Review Distribution (%)")
        plt.ylim(0, math.ceil(max(reviews))*1.10)
        plt.show()
    #  get helpfulness:
    def getHelpFull(self,soup):        
        """compute the helpfull ness of comment"""
        helpfulltag= soup.find_all("span",class_="tl9VpF")
        if helpfulltag==None:
            raise ValueError("There is not HelpFull Review Available")
        return [self.converttonumber(x.text) for x in helpfulltag]
        
    def getHelpFullness(self,soup):
        """scrap the all helpfull comments form the webpage """
        helpfull_list=self.getHelpFull(soup)
        return [
            (helpfull_list[x] / (helpfull_list[x] + helpfull_list[x + 1]) * 100)
            if (helpfull_list[x] + helpfull_list[x + 1]) != 0
            else 0  # Return 0% if both helpful and total votes are zero
            for x in range(0, len(helpfull_list), 2)
        ]
    def getReviews(self,soup:BeautifulSoup):
        """scrap all the reviews froom the webpage of flipkart"""
        reviews=soup.find_all("div",class_="ZmyHeo")

        if reviews==None:
            raise ValueError("Cannot Find Reviews")
        return [x.text for x in reviews]
    
    
    def convertPercentageToInt(self,strlist:[str]):
        """convert the % str to integer"""
        return [int(x[:-1]) for x in  strlist]
    

    
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
    def combineparameter(self,model,overall,reviewstxt,helpful:list,vectorizer_review,tfidf_review):
        """this function will preprocess data and give the output to be feed to the model"""
        pre_processed_data=[self.applydatapreprocessing(x,vectorizer_review,tfidf_review) for x in reviewstxt]
        inputs=[hstack([overall,helpful[i],data]) for i,data in enumerate(pre_processed_data)]
        return inputs
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
        pos=0
        neg=0
        neu=0
        for x in outputs:
            if x==1:
                pos+=1
            if x==0:
                neu+=1
            if x==-1:
                neg+=1
        if pos==0 and neg==0 and neu==0:
            return "not enough data found for analysis"
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
        """predict the output from model"""
        outputs=self.findpredictions(model,inputs)
        return self.findmaxoccurences(outputs)
    
    def converttodict(self,lables:str,values:int)->dict:
        """convert lists to dict """
        if (len(lables)==len(values)):
            ans=[]
            for x,y in zip(lables,values):
                ans.append({"label":x, "value":y})
            return ans
    def combineparameter(self,model,overall,reviewstxt,helpful:list,vectorizer_review,tfidf_review):
        """this function will preprocess data and give the output to be feed to the model"""
        pre_processed_data=[self.applydatapreprocessing(x,vectorizer_review,tfidf_review) for x in reviewstxt]
        inputs=[hstack([overall,helpful[i],data]) for i,data in enumerate(pre_processed_data)]
        return inputs
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
# print("helo")

if __name__=="__main__":
    
    f=FlipKartScrapper()
    # url="https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4?pid=MOBGTAGPTB3VS24W&lid=LSTMOBGTAGPTB3VS24WVZNSC6&marketplace=FLIPKART&q=iphone&store=tyy%2F4io&spotlightTagId=BestsellerId_tyy%2F4io&srno=s_1_1&otracker=search&otracker1=search&fm=Search&iid=25a57b7f-4bf6-4891-8dd8-be541b7d9d92.MOBGTAGPTB3VS24W.SEARCH&ppt=sp&ppn=sp&ssid=ees1v7rrog0000001730139836292&qH=0b3f45b266a97d70"
    url="https://www.flipkart.com/motrex-full-sleeve-colorblock-men-jacket/p/itm4e806a0bcb999?pid=JCKH3CQZXRZDEDXG&lid=LSTJCKH3CQZXRZDEDXGXBPOUD&marketplace=FLIPKART&store=clo%2Fqvw%2Fz0g%2Fjbm&srno=b_1_1&otracker=browse&fm=organic&iid=bd7c7c26-4d6e-4313-a6de-346f58e6a197.JCKH3CQZXRZDEDXG.SEARCH&ppt=browse&ppn=browse&ssid=xfjcc4deio0000001731001861888"
    try:
        print(f.get_domain(url))
        print(f.validate_url(url))
        sourcecode=f.get_source_code(url)
        soup=f.get_soup_code(sourcecode)
        total=f.findtotalreviews(soup)
        reviews_int=f.findnumberofreviews(soup)
        percentlist=f.percentageconvertion(total,reviews_int)
        # f.globalPlot(labels=[5,4,3,2,1],reviews=reviews_int)
        # f.percentagePlot(labels=[5,4,3,2,1],percentages=percentlist)
        helpfullness=f.getHelpFullness(soup)
        reviewstxt= f.getReviews(soup)
        model=f.load_model()
        tfidf=f.load_tfidf()
        cvec=f.load_vec()
        finalinputs =f.combineparameter(model=model,helpful=helpfullness,overall=total,reviewstxt=reviewstxt,tfidf_review=tfidf,vectorizer_review=cvec) 
        probabilities =f.find_probability(model=model,inputs=finalinputs)
        print("probability dict",probabilities)
        print("% dict  ",f.converttodict(lables=[5,4,3,2,1],values=reviews_int))
        print("review dict  ",f.converttodict(lables=[5,4,3,2,1],values=percentlist))
        print(f.model_predict(model,finalinputs))
    except Exception as e:
        print(e)
