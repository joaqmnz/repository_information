from classes.Repositorio import Repositorio
# from classes.Elasticsearch import ElasticS
from datetime import datetime
from utils.verificar_tamanho import *
from utils.calcula_tempo import hora
from time import time

projeto = 'moby/moby'

moby = Repositorio(projeto=projeto)

tag = ''

ini = time()
moby.get_release_commits(tag)
# print(f'Release "{tag}": {get_tamanho_commits_release(tag)} commits')
fim = time()

print(f'Tempo: {hora(fim - ini)}s')

print(f"Finalizou em {datetime.now().hour}:{datetime.now().minute}")
