from github import Github
from dotenv import load_dotenv
from os import environ, path
import json

class Repositorio:
    def __init__(self, projeto: str) -> None:
        load_dotenv()
        self.token = environ['TOKEN']
        self.github = Github(self.token)
        self.repo = self.github.get_repo(projeto)
        self.projeto = projeto.split('/')[1]
        self.url_graphql = 'https://api.github.com/graphql'
        self.header_graphql = {"Authorization": environ['GRAPHQL']}

        self.path_tags = './output/tags.json'
        self.path_releases = './output/releases_tag_commits.json'
        self.path_ultimo_commit = './output/ultimo_commit.json'
    
    def get_tags(self) -> None:
        print(f'Obtendo as tags do repositório "{self.projeto}"')

        # Váriavel para armazenar as tags
        tags = {}

        # Iteração para obter as tags
        for tag in self.repo.get_tags():
            # Adicionando no dicionário
            tags[tag.name] = {
                'commit': tag.commit.sha,
                'tag': tag.name,
                'download': tag.zipball_url
            }
        
        # Salvando em um arquivo .json
        with open(self.path_tags, 'w') as arquivo:
            json.dump(tags, arquivo, indent=True)
        
        print("Operação finalizada")
    
    def get_releases(self) -> None:
        print(f'Obtendo releases do repositório "{self.projeto}"')

        # Váriavel para armazenar as releases
        releases = {}

        # Iteração nas releases
        for item in self.moby.get_releases():
            # Verificando se é ou não uma pre-release
            if item.prerelease:
                print(f"Pre-release: {item.tag_name}")
            else:
                print(f"Release: {item.tag_name}")
            
            # Adicionando informações da release no dicionário
            releases[item.tag_name] = {
                'pre_release': item.prerelease,
                'author': {
                    'author_name': item.author_name,
                    'author_id': item.author_id,
                    'author_url': item.author_url,
                    'author_node_id': item.author_node_id,
                    'author_twt_username': item.author_twt_username,
                    'author_permissions': {
                        "admin": item.author.permissions.admin,
                        "maintain": item.author.permissions.maintain,
                        "pull": item.author.permissions.pull,
                        "push": item.author.permissions.push,
                        "triage": item.author.permissions.triage
                    }
                },
                'url': item.html_url,
                'tag_name': item.tag_name,
                'id': item.id,
                'title': item.title
            }

            print(f'Salvando release "{item.tag_name}"')

            # Salvando as releases
            with open(self.path_releases, 'w') as arquivo:
                json.dump(releases, arquivo, indent=True)

    def get_releases_tag_commits(self) -> None:
        # Abrindo arquivo de tags no modo leitura
        with open(self.path_tags, 'r') as arquivo:
            tags = json.load(arquivo)
        
        # Abrindo arquivo das releases no modo leitura
        with open(self.path_tags, 'r') as arquivo:
            releases = json.load(arquivo)
        
        # Iteração nas tags
        for tag in tags:
            # Verificando se a tag está nas releases
            if tag in releases:
                print(f"Inserindo commit da release {tag}")
                # Inserindo commit referente à tag
                releases[tag]['commit'] = tags[tag]['commit']
                # Avançaando para a proxima tag, pois não há necessidade de percorrer as releases
                continue
            
            print(f"Tag '{tag}' não pertence à uma release")
        
        # Salvando novamente as releases, atualizadas com os commits das suas respectivas tags
        with open(self.path_releases, 'w') as arquivo:
            json.dump(releases, arquivo, indent=True)
    
    def get_release_commits(self, tag: str) -> None:
        # Abrindo arquivo das releases no modo leitura
        with open(self.path_releases, 'r') as arquivo:
            releases = json.load(arquivo)
        
        # Verificando se tag é uma release ou se deseja pegar os commits a partir da branch master
        if tag in releases or tag == '':
            
            if tag:
                print(f"'{tag}' é uma release")
            else:
                print("Obtendo commits a partir da branch master")

            # Váriavel para armazenar todos os commits
            novos_commits = {}

            # Verificação para saber se é a partir da branch master
            if tag:
                # Váriavel para armazenar o commit inicial da busca
                commit_sha = releases[tag]['commit']
            else:
                commit_sha = ''
                tag = 'master'

            # Váriavel para armazenar o último commit
            commit_atual = ''

            # Variável para saber se precisa juntar os novos commits com o arquivo já existente
            reagrupar = False

            # Váriavel para armazenar a quantidade de commits atual
            total_commits = 0

            # Verificando se o arquivo do último commit existe
            if path.isfile(self.path_ultimo_commit):
                # Abre o arquivo no modo leitura para recuperar o último commit
                with open(self.path_ultimo_commit, 'r') as arquivo:
                    ultimo_commit = json.load(arquivo)
                
                # Verificando se o conteúdo não é vazio
                if ultimo_commit:
                    # Atribui a váriavel para iniciar a busca a partir do último commit
                    commit_sha = ultimo_commit

                    reagrupar = True
            
            # Estrutura try/except para evitar erro ao atingir o limite da API
            try:
                # Iteração nos commits
                for commit in self.repo.get_commits(sha=commit_sha):
                    print(f"Obtendo commit {total_commits} - {commit.sha}")

                    # Váriavel para obter o autor do commit
                    author = commit.author

                    # Váriavel para armazenar os dados do autor
                    commit_author = {}

                    # Verificando se author não é nulo
                    if author:
                        # Adicionando informações do autor
                        commit_author = {
                            'name': author.name,
                            'id': author.id,
                            'url': author.url,
                            'node_id': author.node_id,
                        }

                        # Verificando se possui permissões:
                        if author.permissions:
                            # Adicionando informações das permissões
                            commit_author['permissions'] = {
                                'admin': author.permissions.admin,
                                'maintain': author.permissions.maintain,
                                'pull': author.permissions.pull,
                                'push': author.permissions.push,
                                'triage': author.permissions.triage
                            }
                        else:
                            commit_author['permissions'] = None
                    else:
                        commit_author = None

                    # Armazenando as informações do commit
                    novos_commits[commit.sha] = {
                        'author': commit_author,
                        'url': commit.html_url,
                        'sha': commit.sha
                    }

                    # Incrementando a quantidade de commits
                    total_commits += 1

                    # Salvando o último commit
                    commit_atual = commit.sha
            except:
                print(f"Limite de API atingido, salvando os {total_commits} commits")

            # Salvando o ulimo commit
            with open(self.path_ultimo_commit, 'w') as arquivo:
                json.dump(commit_atual, arquivo, indent=True)
            
            # Verificação para juntar os novos commits no arquivo já existente
            if reagrupar:

                print(f'Adicionando os novos {total_commits} commits')

                # Abrindo arquivo no modo leitura dos commits da release atual
                with open(f'./output/releases_commits/{tag}.json', 'r') as arquivo:
                    commits = json.load(arquivo)
                
                # Variável para a quantidade de novos commits
                total_atual = 0

                # Variável para a quantidade de commits anterior (a que está no arquivo 'tag'.json)
                total_anterior = commits['total_commits']

                # Deletando chave do total de commits para se deslocar para última posição
                del commits['total_commits']

                # Iteração nos novos commits
                for commit in novos_commits:
                    print(f'Reagrupando commit {total_atual} - {commit}')

                    # Adicionando o commit
                    commits[commit] = novos_commits[commit]

                    # Incrementando a quantidade de commits
                    total_atual += 1

                # Adicionando nova quantidade de commits
                commits['total_commits'] = total_anterior + total_atual

                # Salvando os commits atualizados
                with open(f'./output/releases_commits/{tag}.json', 'w') as arquivo:
                    json.dump(commits, arquivo, indent=True)
            
                return
            
            # A partir daqui não atingiu o limite da API

            print(f"Salvando os {total_commits} commits")

            # Adicionando a chave com a quantidade total de commits obtidos
            novos_commits['total_commits'] = total_commits

            # Salvando os commits no arquivo
            with open(f'./output/releases_commits/{tag}.json', 'w') as arquivo:
                json.dump(novos_commits, arquivo, indent=True)
        else:
            print(f"'{tag}' não é uma release")
