from flask import Flask, request, redirect, session, url_for, render_template, flash, jsonify 

import os
from gmodrpc import GMODAdapter
import json

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = os.urandom(24)

gmod_adaptor = GMODAdapter()

@app.route('/<mine>/gmodrpc/1.1/organisms.json')
def organisms(mine):
    data = gmod_adaptor.organisms(mine)
    return jsonify(**data)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=5005)
