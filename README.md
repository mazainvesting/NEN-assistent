# De NEN-Assistent 🔧

Een eenvoudige Streamlit-chatapp voor leerlingen en zij-instromers. Ome Henk geeft korte Nederlandse uitleg op basis van zelf geüploade PDF-samenvattingen, met bronpassages en een vaste veiligheidswaarschuwing.

## 1. Installeer software

- Python 3.12 (64-bit): https://www.python.org/downloads/ — vink op Windows **Add Python to PATH** aan.
- VS Code met Python-extensie: https://code.visualstudio.com/
- Git: https://git-scm.com/
- Een OpenAI API-project met API-sleutel, facturering en toegang tot de gekozen modellen. Een ChatGPT-abonnement vervangt geen API-facturering.

Een normale laptop volstaat. Er is geen lokale AI-installatie of GPU nodig.

## 2. Download de code

Open een terminal in VS Code:

```bash
git clone https://github.com/mazainvesting/NEN-assistent.git
cd NEN-assistent
```

Of download de ZIP via GitHub en open de uitgepakte map in VS Code.

## 3. Maak een virtuele omgeving

Windows (opdrachtprompt / Command Prompt):

```bat
py -3.12 -m venv .venv
.venv\Scripts\activate.bat
```

Windows PowerShell: activeer met `.venv\Scripts\Activate.ps1`. Als uitvoering is geblokkeerd, gebruik de opdrachtprompt; je hoeft geen beveiligingsbeleid te wijzigen.

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Op macOS kunnen Xcode Command Line Tools nodig zijn: `xcode-select --install`.

Installeer vervolgens in de geactiveerde omgeving:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Voeg je API-sleutel toe

Kopieer **.env.example** naar **.env** in dezelfde map als **app.py**. Vul in:

```dotenv
OPENAI_API_KEY=jouw_eigen_api_sleutel
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

De modelkeuze is instelbaar. GPT-4o mini staat in de OpenAI-documentatie als deprecated; controleer modeltoegang voordat je start. Als het model niet beschikbaar is, vul een geschikt model in waartoe jouw project toegang heeft en valideer de antwoorden opnieuw.

Publiceer nooit je API-sleutel. `.env` en Streamlit secrets zijn uitgesloten via `.gitignore`. Gebruik bij hosting servergeheimen of `.streamlit/secrets.toml` met dezelfde variabelen.

## 5. Start de app

```bash
python -m streamlit run app.py
```

Open de getoonde lokale URL (meestal http://localhost:8501).
Stoppen: **Ctrl+C**. Bij een volgende sessie: open de map, activeer de omgeving en voer hetzelfde startcommando uit.

## 6. Upload en chat

1. Upload links één tot vijf tekst-PDF's (maximaal 10 MB per PDF, samen 300 pagina's).
2. Bevestig dat je deze documenten met AI mag verwerken en naar OpenAI mag sturen.
3. Klik **Documenten verwerken**.
4. Stel je vraag. Open **Gevonden passages** om PDF-pagina's en tekst te controleren.
5. **Nieuw gesprek** wist alleen het gesprek. **Documenten en gesprek wissen** verwijdert de index en het gesprek uit de sessiestatus; verwijder uploads ook via het uploadveld als je de geselecteerde bestanden wilt weghalen.

NEN-content mag volgens NEN niet zonder toestemming in AI worden ingezet. Ook een gekochte PDF geeft niet automatisch toestemming voor dit gebruik. Gebruik eigen materiaal met de benodigde rechten of regel expliciete toestemming voor het beoogde gebruik. Upload geen vertrouwelijke gegevens of persoonsgegevens.

## Bestanden en aanpassingen

| Bestand | Functie |
| --- | --- |
| app.py | Chatinterface, upload, sessiebeheer, API-aanroep |
| prompts.py | Volledige system prompt voor Ome Henk en vaste veiligheidsafsluiting |
| rag.py | PDF lezen, LangChain-chunks, embeddings, cosine-zoekfunctie en bron-ID-controle |
| requirements.txt | Benodigde Python-pakketten |
| .env.example | Voorbeeldinstellingen zonder sleutel |
| .streamlit/config.toml | Kleuren en uploadlimiet |
| tests/test_rag.py | Lokale controles zonder API-aanroepen |

De volledige kopieerbare rol staat als **SYSTEM_PROMPT** in **prompts.py**. Pas daar toon en leerdoel aan. De app voegt de veiligheidswaarschuwing zelf toe, ook bij foutmeldingen in een antwoord.

## Technische werking

- pypdf leest tekst per PDF-pagina; LangChain RecursiveCharacterTextSplitter maakt stukken van maximaal 1200 tekens met 200 tekens overlap.
- De officiële OpenAI SDK maakt embeddings met text-embedding-3-small in batches.
- NumPy bewaart genormaliseerde vectoren in het geheugen van de eigen Streamlit-sessie; geen aparte vectordatabase nodig.
- Per vraag worden maximaal vijf passages geselecteerd met cosine similarity. De drempel 0,30 is een voorlopige heuristiek, geen kans op juistheid.
- De laatste twee gebruikersvragen helpen bij het zoeken voor vervolgvragen. Dit kan bij onderwerpwisselingen minder nauwkeurig zijn: start dan een nieuw gesprek.
- De Responses API ontvangt de system prompt, maximaal zes eerdere berichten en de gevonden passages. store=False wordt gebruikt; dit is geen garantie op nul gegevensretentie bij de API-aanbieder.
- Bij ontbreken van treffers wordt geen antwoordmodel aangeroepen. Bij ontbrekende/ongeldige bron-ID's wordt het modelantwoord vervangen door een terughoudende melding.
- Bronnen verwijzen naar PDF-pagina's, niet automatisch naar normartikelen of normedities. Die metadata wordt nog niet automatisch gevalideerd.
- Wijziging/verwijdering van uploads of intrekken van toestemming wist de actieve index en het gesprek.

De app bewaart documenten en vectoren niet op schijf. De browseruploads en sessiegegevens bestaan tijdelijk in het procesgeheugen. Tekst wordt naar OpenAI gestuurd voor embeddings; vragen, beperkte gesprekshistorie en geselecteerde passages voor antwoorden. API-verwerking kost geld. Stel budgetmeldingen in en bewaak gebruik.

## Grenzen van dit prototype

Geen OCR, automatische tabelinterpretatie, editiecontrole of garantie op correcte antwoorden. PDF-extractie kan tabellen of uitzonderingen verkeerd lezen. Een geldige bron-ID bewijst niet dat de tekst de uitspraak ondersteunt. Promptinjectie wordt begrensd met instructies, maar niet gegarandeerd voorkomen. Controleer kritieke antwoorden met de volledige toepasselijke norm en een bevoegde deskundige.

Dit is een lokaal leerprototype, geen installatiekeuring of productieplatform. Voor openbare hosting zijn authenticatie, harde gebruikslimieten, aanvullende bestandisolatie, privacyafspraken en vakinhoudelijke acceptatietests nodig. De naam impliceert geen officiële band met NEN.

## Testen

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

Test daarna met een vakdocent representatieve vragen, niet-beantwoordbare vragen, tegenstrijdige bronnen, vervolgvragen en risicovolle praktijksituaties. Kalibreer de zoekdrempel voordat je de app breder gebruikt.

## Documentatie

- Streamlit: https://docs.streamlit.io/get-started/installation/command-line
- OpenAI tekstgeneratie: https://developers.openai.com/api/docs/guides/text
- OpenAI embeddings: https://developers.openai.com/api/docs/guides/embeddings
- GPT-4o mini: https://developers.openai.com/api/docs/models/gpt-4o-mini
- LangChain splitter: https://docs.langchain.com/oss/python/integrations/splitters/recursive_text_splitter
- NEN auteursrecht en AI: https://www.nen.nl/nen-naam-logo-auteursrecht
