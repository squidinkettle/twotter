import os
from twitter_api.main import app, api
from twitter_api.apify import User_id, Users, Twoots
from flask_restful import Resource, Api


api.add_resource(User_id, '/user_id') # Route_1
api.add_resource(Users, '/users') # Route_2
api.add_resource(Twoots, '/users/<int:id>') # Route_3
if __name__ == '__main__':
    app.debug = True
    app.config['SECRET_KEY'] = "kljasdno9asud89uy981uoaisjdoiajsdm89uas980d"
    host = os.environ.get('IP', '0.0.0.0')
    port = int(os.environ.get('PORT', 8080))
    app.run(host=host, port=port)
    

