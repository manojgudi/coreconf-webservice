from flask import Flask, render_template, request, redirect, url_for
import pycoreconf
import pprint
import json
import random
import os
import cbor2

app = Flask(__name__)

senmlSIDFile = "examples/senml@unknown.sid"
senmlDataFile = "examples/senml_data.json"
camSIDFile = "examples/cam@unknown.sid"
camDataFile = "examples/cam_yogoko_message.json"

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
            outputText = pprint.pformat(cbor2.loads(coreconfByteString), width=40)
            hexText = coreconfByteString.hex()
        except:
            errMessage = "Error: CORECONF conversion failed."
        finally:
            # Delete the temporary files
            os.remove(sidFileName)
            os.remove(dataFileName)

        if errMessage:
            return render_template('index.html', output_text=errMessage)

        jsonSize = len(json.dumps(dataJSON,  separators=(',', ':')))
        hexSize  = int(len(hexText)/2)
        compressedPercent = round(100 - (hexSize/jsonSize)*100, 2)
        return render_template('index.html', output_text=outputText, hex_text=hexText, json_length=jsonSize, hex_length=hexSize, 
                               compressed_percent = compressedPercent, sid_text_raw=sidTextRaw, data_text_raw=dataTextRaw)
    
    # If it's a GET request (e.g., page refresh), render with empty outputText
    return render_template('index.html')

@app.route('/senml_example', methods=['GET'])
def senmlExample():
    # Read the example files and return the content as sid_text_raw and data_text_raw
   
    sidTextRaw = "Unable to read SID file."
    dataTextRaw= "Unable to read SenML Data file."

    with open(senmlSIDFile, 'r') as f:
        sidTextRaw = f.read()
    with open(senmlDataFile, 'r') as f:
        dataTextRaw = f.read()

    return render_template('index.html', sid_text_raw=sidTextRaw, data_text_raw=dataTextRaw)

@app.route('/cam_example', methods=['GET'])
def camExample():
    # Read the example files and return the content as sid_text_raw and data_text_raw
   
    camTextRaw = "Unable to read CAM file."
    dataTextRaw= "Unable to read CAM Data file."

    with open(camSIDFile, 'r') as f:
        camTextRaw = f.read()
    with open(camDataFile, 'r') as f:
        dataTextRaw = f.read()

    return render_template('index.html', sid_text_raw=camTextRaw, data_text_raw=dataTextRaw)

if __name__ == '__main__':
    app.run(debug=True)
