import requests
from src.config.settings import BASE_URL, API_KEY

class SPTransAPIClient:
    def __init__(self):
        self.session = requests.Session()
        self.is_authenticated = False

    def authenticate(self):
        """Realiza autenticação na api SPTrans e armazena cookies da sessão"""
        auth_url = f"{BASE_URL}/Login/Autenticar?token={API_KEY}"
        response = self.session.post(auth_url)

        if response.status_code == 200 and response.text == 'true':
            self.is_authenticated = True
            print("Autenticado com sucesso")
            return True
        
    
    def get_bus_positions(self):
        """Coleta os dados de localização dos onibus em tempo real"""
        if not self.is_authenticated:
            if not self.authenticate():
                raise Exception("Não é possível solicitar as rotas sem autenticação")
        
        pos_url = f"{BASE_URL}/Posicao"
        response = self.session.get(pos_url)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Falha ao solicitar os dados. Erro: {response.status_code}")
        