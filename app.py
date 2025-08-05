from flask import Flask, request, jsonify
from flask_cors import CORS
import model
from PIL import Image
import numpy as np

app = Flask("ThyroNetV6")
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://thyronetv6.vercel.app",
    ])

@app.route("/", methods = ["POST"])
def handleData():
    # name = request.form.get('name')
    age = request.form.get('age')
    sex = request.form.get('gender')

    toggle_scan = request.form.get('toggleScanDiagnosis')
    toggle_blood = request.form.get('toggleBloodDiagnosis')
    
    try:
        scan_image = request.files['scanImage']
    except:
        scan_image = None

    image_data = None

    if scan_image:
        try:
            image = Image.open(scan_image).convert("RGB")
            image_data = image
        except Exception as e:
            return jsonify({
                'error': f'Invalid image file: {str(e)}',
                'status': 400,
                })
    
    if toggle_scan and image_data is not None:
        try:
            scan_target, scan_target_summary = model.predict_tirads(image_data)
            scan_result = {
                'target' : scan_target,
                'target_summary' : scan_target_summary,
            }
        except Exception as e:
            scan_result = {"error": str(e)}
    else:
        scan_result = {
            "target" : None,
            "target_summary" : None
            }
    
    tsh = request.form.get('tsh')
    freeT4 = request.form.get('freeT4')
    freeT3 = request.form.get('freeT3')
    totalT4 = request.form.get('totalT4')
    antiTpo = request.form.get('antiTpo')
    antiTg = request.form.get('antiTg')

    if toggle_blood:
        try:
            new_input = {
                "Age": float(age) if age and age != '' else np.nan,
                "Sex": sex,
                "TSH": float(tsh) if tsh and tsh != '' else np.nan,
                "Free T4": float(freeT4) if freeT4 and freeT4 != '' else np.nan,
                "Free T3": float(freeT3) if freeT3 and freeT3 != '' else np.nan,
                "Total T4": float(totalT4) if totalT4 and totalT4 != '' else np.nan,
                "AntiTPO": float(antiTpo) if antiTpo and antiTpo != '' else np.nan,
                "AntiTg": float(antiTg) if antiTg and antiTg != '' else np.nan,
            }
            predicted_condition, class_probabilities = model.predict_condition(new_input)
            blood_result = {
                "target": predicted_condition,
                "target_summary": class_probabilities
            }
        except Exception as e:
            blood_result = {"error": str(e)}
    else:
        blood_result = {
            "target" : None,
            "target_summary" : None
            }

    data = {
        'message': 'OK',
        'scan_result': scan_result,
        'blood_result': blood_result
    }
    
    return jsonify({
        'data': data,
        'status': 200,
    })
    
if __name__ in "__main__":
    app.run(debug=True)