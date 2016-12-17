
def init_connexion_to_hub(remote_api):
    remote_api.register_daemon(name='geotweets server daemon')
    remote_api.register_external_dataset(tag='geotweets', desc='Large dataset storing tweet metadata.')
