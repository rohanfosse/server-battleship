from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)
players = {}
matches_history = []
scores = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auto_join', methods=['POST'])
def auto_join():
    data = request.json
    username, ip, port = data['username'], request.remote_addr, data['port']
    players[username] = {'ip':ip, 'port':port, 'joined':datetime.now().isoformat()}
    scores.setdefault(username, 0)
    return jsonify({'status':'connected'})

@app.route('/players')
def get_players():
    return jsonify([{'username':u,**p} for u,p in players.items()])

@app.route('/propose_match', methods=['POST'])
def propose_match():
    data=request.json
    from_player,to_player=data['from'],data['to']
    # Ici on stocke simplement la demande
    players[to_player]['match_request']=from_player
    return jsonify({'status':'sent'})

@app.route('/check_requests/<username>')
def check_requests(username):
    req=players.get(username,{}).pop('match_request',None)
    return jsonify({'request_from':req})

@app.route('/confirm_match',methods=['POST'])
def confirm_match():
    data=request.json
    p1,p2=data['player1'],data['player2']
    matches_history.append({
        'player1':p1,'player2':p2,
        'timestamp':datetime.now().strftime("%d/%m/%Y %H:%M"),
        'winner':None
    })
    return jsonify({'status':'match_started'})

@app.route('/match_result',methods=['POST'])
def match_result():
    data=request.json
    winner,loser=data['winner'],data['loser']
    scores[winner]+=1
    for m in reversed(matches_history):
        if m['winner'] is None and winner in [m['player1'],m['player2']]:
            m['winner']=winner
            break
    return jsonify({'status':'result_recorded'})

@app.route('/scores_history')
def scores_history():
    sorted_scores=sorted(scores.items(),key=lambda x:-x[1])
    return jsonify({'scores':sorted_scores,'history':matches_history})

if __name__=='__main__':
    app.run(debug=True)
