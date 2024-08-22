from flask import Flask, render_template, request, redirect, url_for
import pycoreconf
import pprint
import json
import random
import os
import cbor2

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    outputText = ""
    errMessage = ""
    if request.method == 'POST':
        sidTextRaw = request.form['input1']
        dataTextRaw = request.form['input2']
        outputText = sidTextRaw + " " + dataTextRaw

              # Validate if sidTextRaw is a valid JSON string
        try:
            sidJSON = json.loads(sidTextRaw)
        except json.JSONDecodeError:
            # If sidTextRaw is not a valid JSON, handle the error (e.g., display an error message)
            errMessage = "Error: SID content is not a valid JSON."

        try:
            dataJSON = json.loads(dataTextRaw)
        except json.JSONDecodeError:
            # If dataTextRaw is not a valid JSON, handle the error (e.g., display an error message)
            errMessage = "Error: Data instance is not a valid JSON."

        if errMessage:
            return render_template('index.html', output_text=errMessage)


        # Create a random 10 character string using random library
        randomString = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))

        sidFileName = 'tmp/' + randomString + '_sid.json'
        dataFileName = 'tmp/' + randomString + '_data.json'
        
        with open(sidFileName, 'w') as f:
            json.dump(sidJSON, f)
        with open(dataFileName, 'w') as f:
            json.dump(dataJSON, f)
        
        try:
            ccm = pycoreconf.CORECONFModel(sidFileName, model_description_file=None)
            coreconfByteString = (ccm.toCORECONF(dataFileName))
            outputText = pprint.pformat(cbor2.loads(coreconfByteString))
            hexText = coreconfByteString.hex()
        except:
            errMessage = "Error: CORECONF conversion failed."
        finally:
            # Delete the temporary files
            os.remove(sidFileName)
            os.remove(dataFileName)

        if errMessage:
            return render_template('index.html', output_text=errMessage)

        return render_template('index.html', output_text=outputText, hex_text=hexText, hex_length=len(hexText), sid_text_raw=sidTextRaw, data_text_raw=dataTextRaw)
    
    # If it's a GET request (e.g., page refresh), render with empty outputText
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
