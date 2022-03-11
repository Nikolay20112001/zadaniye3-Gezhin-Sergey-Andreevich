# -*- coding: utf-8 -*-
import datetime
import json

from flask import Flask, jsonify, abort, request, render_template
from idna import unicode
from flask_swagger_ui import get_swaggerui_blueprint
import random


class PromoAction:
    def __init__(self, id, name, description, prizes, participants):
        self.id = id
        self.name = name
        self.description = description
        self.prizes = prizes
        self.participants = participants


class Prize:
    def __init__(self, id, description):
        self.id = id
        self.description = description

class Participant:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class Result:
    def __init__(self, winner, prize):
        self.winner = winner
        self.prize = prize

app = Flask(__name__)

#  Генерация начальных данных

prize1 = Prize(1, 'prize_des1')
prize2 = Prize(2, 'prize_des2')

participant1 = Participant(1, 'participant1')
participant2 = Participant(2, 'participant2')

promo1 = PromoAction(1, 'Promo1', 'promo_des1', [prize1, prize2], [participant1, participant2])
promo2 = PromoAction(2, 'Promo2', 'promo_des2', [prize1], [participant1])

prizes = [prize1, prize2]
participants = [participant1, participant2]
promos = [promo1, promo2]

@app.route('/')
def index():
    return "Гежин Сергей Андреевич, gezhinsa@yandex.ru, 2 курс Бакалавриата"


@app.route('/promo', methods=['GET'])
def get_promos():
    res = []
    for i in promos:
        promo = {
        'id': i.id,
        'name': i.name,
        'description': i.description
        }
        res.append(promo)
    return jsonify(res), 200

@app.route('/promo/<int:id>', methods=['GET'])
def get_promo(id):
    promo = list(filter(lambda t: t.id == id, promos))[0]
    if not promo:
        abort(404)
    prizess = []
    for i in promo.prizes:
        prize = {'id': i.id, 'description': i.description}
        prizess.append(prize)
    participantss = []
    for i in promo.participants:
        participant = {'id': i.id, 'name': i.name}
        participantss.append(participant)
    res = {'id': promo.id, 'name': promo.name, 'description': promo.description,
           'prizes': prizess, 'participants': participantss}
    return jsonify(res), 200

@app.route('/promo', methods=['POST'])
def create_promo():
    if not request.json or not 'name' in request.json:
        abort(400)
    a = promos[-1].id + 1
    promo = PromoAction(a, request.json['name'], request.json.get('description', ""), None, None)
    promos.append(promo)
    return jsonify(a), 201

@app.route('/promo/<int:id>', methods=['PUT'])
def update_promo(id):
    promo = list(filter(lambda t: t.id == id, promos))[0]
    if not promo:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json:
        if type(request.json['name']) != unicode:
            abort(400)
        else:
            if request.json['name'] == '':
                abort(400)
            else:
                promo.name = request.json['name']


    if 'description' in request.json:
        if type(request.json['description']) is not unicode:
            abort(400)
        else:
            promo.description = request.json['description']

    return jsonify('Changed'), 200

@app.route('/promo/<int:id>', methods=['DELETE'])
def delete_promo(id):
    promo = list(filter(lambda t: t.id == id, promos))[0]
    if not promo:
        abort(404)
    promos.remove(promo)
    return jsonify('Deleted'), 200

@app.route('/promo/<int:id>/participant', methods=['POST'])
def add_participant(id):
    if not request.json or not 'name' in request.json:
        abort(400)
    promo = list(filter(lambda t: t.id == id, promos))[0]
    if not promo:
        abort(404)
    a = promo.participants[-1].id + 1
    participant = Participant(a, request.json['name'])
    promo.participants.append(participant)
    return jsonify(a), 201

@app.route('/promo/<int:promo_id>/participant/<int:participant_id>', methods=['DELETE'])
def delete_participant(promo_id, participant_id):
    promo = list(filter(lambda t: t.id == promo_id, promos))[0]
    if not promo:
        abort(404)
    participant = list(filter(lambda t: t.id == participant_id, promo.participants))[0]
    if not participant:
        abort(404)
    promo.participants.remove(participant)
    return jsonify('Participant_Deleted'), 200

@app.route('/promo/<int:id>/prize', methods=['POST'])
def add_prize(id):
    if not request.json or not 'description' in request.json:
        abort(400)
    promo = list(filter(lambda t: t.id == id, promos))[0]
    if not promo:
        abort(404)
    a = promo.prizes[-1].id + 1
    prize = Prize(a, request.json['description'])
    promo.prizes.append(prize)
    return jsonify(a), 201

@app.route('/promo/<int:promo_id>/prize/<int:prize_id>', methods=['DELETE'])
def delete_prize(promo_id, prize_id):
    promo = list(filter(lambda t: t.id == promo_id, promos))[0]
    if not promo:
        abort(404)
    prize = list(filter(lambda t: t.id == prize_id, promo.prizes))[0]
    if not prize:
        abort(404)
    promo.prizes.remove(prize)
    return jsonify('Prize_Deleted'), 200

@app.route('/promo/<int:id>/raffle', methods=['POST'])
def raffle(id):
    promo = list(filter(lambda t: t.id == id, promos))[0]
    if not promo:
        abort(404)
    prizelen = len(promo.prizes)
    participantslen = len(promo.participants)
    if prizelen != participantslen:
        abort(409)
    else:
        response = []
        for i in range(prizelen):
            prize = random.choice(promo.prizes)
            promo.prizes.remove(prize)

            participant = random.choice(promo.participants)
            promo.participants.remove(participant)

            result = Result(participant, prize)
            print(result, end=' ')

            res = {'winner': {'id': result.winner.id, 'name': result.winner.name},
                   'prize': {'id': result.prize.id, 'description': result.prize.description}}
            response.append(res)

        return jsonify(response), 200

if __name__ == '__main__':
    app.run(port=8080)
