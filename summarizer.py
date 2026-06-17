from langchain_core.messages import content

from llm_helper import LlmHelper
from ollama import chat
from ollama import ChatResponse

class Summarizer:
    def __init__(self):
        self.prompt = """
        Je bent een samenvattingstool die nieuws artikelen samenvat naar een makkelijk lezend geschreven tekst.
    
    Het is van belang dat de teksten nederlands zijn samengevat omdat de doelgroep enkel nederlands kan spreken.

    Stijl:
    - Gebruik maximaal 140 woorden.
    - Gebruik geen markdown of andere opmaak.
    - Gebruik een enkel spatie voor elke woordscheidling.

    Regels:
    - Het is belangrijk dat de samenvatting overeenkomt met de inhoud van het artikel en er mogen geen details worden toegevoegd die niet in het artikel staan.
    - De samenvatting moet in het Nederlands zijn, ongeacht de taal van het oorspronkelijke artikel.
    - De samenvatting moet gemakkelijk te begrijpen zijn voor een breed publiek, inclusief mensen die niet bekend zijn met het onderwerp van het artikel.
    - De samenvatting moet de belangrijkste punten van het artikel bevatten, maar mag niet te gedetailleerd zijn. Het doel is om een beknopte en informatieve samenvatting te bieden die de kern van het artikel weergeeft zonder overbodige details.
    
    mocht de samenvatting niet aan deze regels voldoen, geef dan een foutmelding terug in plaats van een samenvatting.
    
    Voeg aan het einde een sectie toe genaamd 'WAAROM' met één zin die uitlegt waarom dit belangrijk is voor de lezer
        """
        pass

    def summarize(self, text):
        llm_helper = LlmHelper()

        return llm_helper.get_response([
            {
                'role': 'system',
                'content': self.prompt
            },
            {
                'role': 'user',
                'content': text,
            },
        ])

    def summarize_with_relevance(self, text):
        llm_helper = LlmHelper()

        return llm_helper.get_response_with_ollama([
            {
                'role': 'system',
                'content': self.prompt
            },
            {
                'role': 'user',
                'content': text,
            },
        ])