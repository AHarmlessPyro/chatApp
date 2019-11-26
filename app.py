from quart import Quart
from quart import render_template
import re
import os
import requests

#from werkzeug.debug import DebuggedApplication
app = Quart(__name__, template_folder="template")

app.env = 'development'
app.debug = True
app.static_folder = 'static'
app.static_url_path = 'static'
app.config['TESTING'] = True


@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/<word>/<position>')
def ret(word, position):
    response = requests.get('https://www.dictionaryapi.com/api/v3/references/collegiate/json/' +
                            word+'?key=721730b3-70ba-4169-9a3c-d170a41d49c3')
    val = response.json()
    print(val[0])

    list_item_ret = ""

    try:
        if(val[0]['shortdef'] == None or len(val[0]['shortdef']) == 0):
            print("Hello")
            item = dict()
            item['shortdef'] = ['Word doesn\'t exist in Webster Dictionary']
            return render_template('secondaryPage.html', list_item=item, Word=word)
    except:
        print("No Hello")
        item = dict()
        item['shortdef'] = ['Word doesn\'t exist in Webster Dictionary']
        return render_template('secondaryPage.html', list_item=item, Word=word)
    print("Pass through")
    return render_template('secondaryPage.html', list_item=val[0], Word=word)


@app.route('/')
def testTemplateNesting():
    return render_template('MainBody.html')


@app.template_filter('search')
def match(inputStr):
    try:
        regex = r"[^\|\{\}\'][a-zA-Z \,]+[^\|\{\}\']"
        matches = re.findall(regex, inputStr, re.MULTILINE)
        print(matches)
        if(matches == None or matches == []):
            print("Formatting not accepted" + str(inputStr))
            return 'Input format weird.Can\'t process input ' + input
        else:
            print('DONE')
            return str(matches[0])
    except:
        print("Formatting not accepted" + str(inputStr))
        return 'Input format weird.Can\'t process input \n' + str(inputStr)
