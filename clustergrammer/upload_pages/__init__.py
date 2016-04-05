from flask import Blueprint
from flask.ext.cors import cross_origin

import Enrichr_clustergram_endpoint as enr_clust_endpoint
import vector_upload_function as vector_upload_fun
import run_load_tsv

def add_routes(app=None, mongo_address=None):

  upload_pages = Blueprint('upload_pages', __name__, 
    static_url_path='/upload_pages/static', static_folder='./static', 
    template_folder='./templates')

  @upload_pages.route('/clustergrammer/Enrichr_clustergram', methods=['POST','GET'])
  @cross_origin()
  def enrichr_clustergram():
    return enr_clust_endpoint.main(mongo_address)

  @upload_pages.route('/clustergrammer/vector_upload/', methods=['POST'])
  @cross_origin()
  def proc_vector_upload():
    return vector_upload_fun.main(mongo_address)

  @upload_pages.route('/clustergrammer/upload_network/', methods=['POST'])
  def upload_network():
    return run_load_tsv.main(mongo_address, response_type='redirect')

  @upload_pages.route('/clustergrammer/matrix_upload/', methods=['POST'])
  def proc_matrix_upload():
    return run_load_tsv.main(mongo_address, response_type='link')

  app.register_blueprint(upload_pages)