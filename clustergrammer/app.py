from flask import Flask, redirect
import sys
import logging
from logging.handlers import RotatingFileHandler
import os
from flask import send_from_directory

from clustergrammer import viz_pages
from clustergrammer import home_pages
from clustergrammer import demo_pages
from clustergrammer import upload_pages
from clustergrammer import status_check
from clustergrammer import grab_data

app = Flask(__name__, static_url_path='')
app.config.from_pyfile('settings.py')

#########################
# v1.5.2
#########################

# address for mongodbs

# # local
# mongo_address = '10.90.122.218'

# # elizabeth
# mongo_address = '146.203.54.165'

# hannah
# mongo_address = os.environ.get('MONGODB', '146.203.54.131')

# from config
mongo_address = app.config['MONGODB']

##########################################
# switch for local and docker development
##########################################

# # for local development
SERVER_ROOT = os.path.dirname(os.getcwd()) + '\clustergrammer-web-master\clustergrammer'
print(SERVER_ROOT)

# for docker development
#SERVER_ROOT = './clustergrammer'
# change routing of logs when running docker
logging.basicConfig(stream=sys.stderr)

######################################
######################################
@app.route(app.config['ENTRY_POINT'] + '/<path:path>')
def send_static(path):
  return send_from_directory(SERVER_ROOT, path)

@app.route(app.config['ENTRY_POINT'] + '/l1000cds2/', methods=['POST'])
def l1000cds2_upload():
  '''
  l1000cds2 is using a old version of clustergrammer.py
  '''
  
  import requests
  import json
  from clustergrammer_old import Network
  from pymongo import MongoClient
  from bson.objectid import ObjectId
  from flask import request

  l1000cds2 = json.loads( request.form.get('signatures') )

  net = Network()
  net.load_l1000cds2(l1000cds2)

  cutoff_comp = 0
  min_num_comp = 2
  net.cluster_row_and_col(dist_type='cosine', dendro=True)
  net.dat['node_info']['row']['ini'] = net.sort_rank_node_values('row')
  net.dat['node_info']['col']['ini'] = net.sort_rank_node_values('col')
  net.viz = {}
  net.viz['row_nodes'] = []
  net.viz['col_nodes'] = []
  net.viz['links'] = []
  net.viz_json()
  
  export_dict = {}
  export_dict['name'] = 'l1000cds2'
  export_dict['dat'] = net.export_net_json('dat')
  export_dict['viz'] = net.viz
  export_dict['_id'] = ObjectId(l1000cds2['_id'])
  client = MongoClient(mongo_address)
  db = client.clustergrammer
  tmp = db.networks.find_one({'_id': ObjectId(l1000cds2['_id']) })
  if tmp is None:
    tmp_id = db.networks.insert_one( export_dict )

  client.close()
  return redirect(app.config['ENTRY_POINT'] + '/l1000cds2/'+l1000cds2['_id'])
home_pages.add_routes(app)
viz_pages.add_routes(app, mongo_address)
demo_pages.add_routes(app)
upload_pages.add_routes(app, mongo_address)
status_check.add_routes(app, mongo_address)
grab_data.add_routes(app)

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)
