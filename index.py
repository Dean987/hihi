import requests
from bs4 import BeautifulSoup
import firebase_admin



from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

app = Flask(__name__)

@app.route("/")
def index():
    homepage = "<h1>陳俊祥Python讀取Firestore</h1>"
    homepage += "<a href=/account>網頁表單輸入實例</a><br><br>"
    homepage += "<a href=/search>課程查詢</a><br><br>"
    homepage += "<br><a href=/movie target = _blank>讀取開眼電影即將上映影片，寫入Firestore</a><br>"
    homepage += "<a href=/search_movie target = _blank>電影查詢</a><br>"


    return homepage

@app.route("/account", methods=["GET", "POST"])
def account():
    if request.method == "POST":
        user = request.form["user"]
        pwd = request.form["pwd"]
        result = "您輸入的帳號是：" + user + "; 密碼為：" + pwd 
        return result
    else:
        return render_template("account.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        cond = request.form["keyword"]
        result = "您輸入的課程關鍵字是：" + cond
        db = firestore.client()
        collection_ref = db.collection("1111")
        docs = collection_ref.get()
        result = ""
        for doc in docs:
            dict = doc.to_dict()
            if cond in dict["Course"]:
                #print("{}老師開的{}課程,每週{}於{}上課".format(dict["Leacture"], dict["Course"],  dict["Time"],dict["Room"]))
                result += dict["Leacture"] + "老師開的" + dict["Course"] + "課程,每週"
                result += dict["Time"] + "於" + dict["Room"] + "上課<br>" 

    return result
    else:
        return render_template("search.html")




@app.route("/movie")
def movie():   
    url = "http://www.atmovies.com.tw/movie/next/"
    Data = requests.get(url)
    Data.encoding = "utf-8"
    sp = BeautifulSoup(Data.text, "html.parser")
    result = sp.select(".filmListAllX li")
    lastUpdate = sp.find("div", class_="smaller09").text[5:]

    for item in result:
        picture = item.find("img").get("src").replace(" ", "")
        rate = item.find("div", class_="runtime").text
        test_rate = item.find_all("img")
        for img in test_rate:
            if 'src' in img.attrs:
                if img['src'].endswith('/images/cer_G.gif'):
                    rate = "普遍級(一般觀眾皆可觀賞)"
                elif img['src'].endswith('/images/cer_P.gif') :
                    rate = "保護級(未滿六歲之兒童不得觀賞，六歲以上未滿十二歲之兒童須父母、師長或成年親友陪伴輔導觀賞)"
                elif img['src'].endswith('/images/cer_F2.gif') :
                    rate = "輔導級(未滿十二歲之兒童不得觀賞)"
                elif img['src'].endswith('/images/cer_F5.gif') :
                    rate = "輔導級(未滿十五歲之人不得觀賞)"
                elif img['src'].endswith('/images/cer_R.gif'):
                    rate = "限制級(未滿十八歲之人不得觀賞)"
                else :
                    rate = "尚無電影分級資訊"
        title = item.find("div", class_="filmtitle").text
        movie_id = item.find("div", class_="filmtitle").find("a").get("href").replace("/", "").replace("movie", "")
        hyperlink = "http://www.atmovies.com.tw" + item.find("div", class_="filmtitle").find("a").get("href")
        show = item.find("div", class_="runtime").text.replace("上映日期：", "")
        show = show.replace("片長：", "")
        show = show.replace("分", "")
        showDate = show[0:10]
        showLength = show[13:]

        doc = {
        "title":title,
        "picture":picture,
        "rate":rate,
        "hyperlink":hyperlink,
        "showDate":showDate,
        "showLength":showLength,
        "lastUpdate":lastUpdate
        }

        doc_ref = db.collection("俊祥電影").document(movie_id)
        doc_ref.set(doc)
        return "近期上映電影已爬蟲及存檔完畢，網站最近更新日期為：" + lastUpdate 
@app.route("/search_movie", methods=["POST","GET"])
def search_movie():
    if request.method == "POST":
        MovieTitle = request.form["MovieTitle"]
        info = ""     
        collection_ref = db.collection("俊祥電影")
        docs = collection_ref.order_by("showDate").get()
        for doc in docs:
            if MovieTitle in doc.to_dict()["title"]: 
                info += "片名：<a target = _blank href=" + doc.to_dict()["hyperlink"] + ">" + doc.to_dict()["title"] + "</a>" + "<br>" 
                info += "分級資訊：" + doc.to_dict()["rate"] + "<br><br>"
        if info == "":
            info += "抱歉，查無相關條件的電影資訊" 
        return info
        else:  
            return render_template("search_movie.html")

        













        


#if __name__ == "__main__":
    #app.run()