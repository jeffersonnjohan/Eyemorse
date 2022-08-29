#Import necessary libraries
from flask import Flask, jsonify, render_template, Response, request
import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
from cvzone.PlotModule import LivePlot

counterFrame = 0
morse_string = ""
final_message = ""
isBlinking = False
isDetectingFace = False

#Initialize the Flask app
app = Flask(__name__)

camera = cv2.VideoCapture(0)

# Dictionary for morse code
def morse_dict(str):
    # Character
    if str == '.-':
        return 'A'
    elif str == '-...':
        return 'B'
    elif str == '-.-.':
        return 'C'
    elif str == '-..':
        return 'D'     
    elif str == '.':
        return 'E'
    elif str == '..-.':
        return 'F'
    elif str == '--.':  
        return 'G'
    elif str == '....':
        return 'H'
    elif str == '..':   
        return 'I'
    elif str == '.---':
        return 'J'
    elif str == '-.-':
        return 'K'
    elif str == '.-..':
        return 'L'
    elif str == '--':
        return 'M'
    elif str == '-.':
        return 'N'
    elif str == '---':
        return 'O'
    elif str == '.--.':
        return 'P'
    elif str == '--.-':
        return 'Q'
    elif str == '.-.':
        return 'R'
    elif str == '...':
        return 'S'
    elif str == '-':
        return 'T'
    elif str == '..-':
        return 'U'
    elif str == '...-':
        return 'V'
    elif str == '.--':
        return 'W'
    elif str == '-..-':
        return 'X'
    elif str == '-.--':
        return 'Y'
    elif str == '--..':
        return 'Z'
    # Number
    elif str == '.----':
        return '1'
    elif str == '..---':
        return '2'
    elif str == '...--':
        return '3'
    elif str == '....-':
        return '4'
    elif str == '.....':
        return '5'
    elif str == '-....':
        return '6'
    elif str == '--...':
        return '7'
    elif str == '---..':
        return '8'
    elif str == '----.':
        return '9'
    elif str == '-----':
        return '0'
    else:
        return ''

def gen_frames():
    camera = cv2.VideoCapture(0)
    detector = FaceMeshDetector(maxFaces = 1)
    plotY = LivePlot(640, 360, [20, 50], invert = True)

    idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
    ratioList = []
    blinkCounter = 0
    counter = 0
    color = (255, 0, 255)

    # Message
    string = "Undefined"
    global morse_string
    global final_message
    global counterFrame
    global isBlinking
    global isDetectingFace

    counterFrame = 0
    morse_string = ""
    final_message = ""
    isBlinking = False

    while True:
        success, img = camera.read()
        img, faces = detector.findFaceMesh(img, draw = False)
        
        if faces:
            isDetectingFace = True
            face = faces[0]
            
            for id in idList:
                cv2.circle(img, face[id], 5, color, cv2.FILLED)
            
            leftUp = face[159]
            leftDown = face[23]
            leftLeft = face[130]
            leftRight = face[243]
            
            lengthVer, _ = detector.findDistance(leftUp, leftDown)
            lengthHor, _ = detector.findDistance(leftLeft, leftRight)
            
            cv2.line(img, leftUp, leftDown, (0, 200,0), 3 )
            cv2.line(img, leftLeft, leftRight, (0,200,0), 3)
            
            ratio = lengthVer * 100 // lengthHor
            ratioList.append(ratio)
            
            if len(ratioList) > 5:
                ratioList.pop(0)
            
            ratioAvg = sum(ratioList)/len(ratioList)

            if(ratioAvg < 30) and counter == 0:
                # Mata kedip
                isBlinking = True
                counterFrame += 1
                blinkCounter += 1
                color = (0, 200, 0)
                counter = 1
            if counter != 0:
                counter += 1
                if counter > 10:
                    color = (255, 0, 255)
                    counter = 0
            
            if ratioAvg >= 30:
                # Mata terbuka
                isBlinking = False
                if counterFrame >= 10:
                    # Convert string menjadi alphabet
                    final_message += morse_dict(morse_string)
                    morse_string = ""
                elif counterFrame >= 6:
                    # Cek apakah panjang
                    string = "Panjang"
                    morse_string += '-'
                elif counterFrame >= 3:
                    # Cek apakah pendek
                    string = "Pendek"
                    morse_string += '.'
                counterFrame = 0
            
            cvzone.putTextRect(img, f'Blink Counter: {counterFrame}', (100,100), colorR = color)
            cvzone.putTextRect(img, f'Final: {final_message}', (100,300), colorR = color)
            # cvzone.putTextRect(img, f'Morse: {morse_string}', (100,400), colorR = color)
            cvzone.putTextRect(img, f'Bool: {isBlinking}', (100,400), colorR = color)
            
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            isDetectingFace = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/_stuff', methods=['GET'])
def stuff():
    global counterFrame
    return jsonify(blinkCounter=counterFrame, stringMorse = morse_string, stringFinal = final_message, isBlinking = isBlinking, isDetectingFace = isDetectingFace)

if __name__ == "__main__":
    app.run(debug=True)