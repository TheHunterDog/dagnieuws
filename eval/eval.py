import csv
from datetime import datetime
from pathlib import Path

from tqdm import tqdm

import llm_helper
from document import Document
from ingester import Ingester
from llm_helper import LlmHelper
from retriever import Retriever

sample_docs = [
    Document(
        id="2",
        source="AD",
        title="Klap blijft uit: effect Iranoorlog minder groot voor meeste burgers dan gevreesd",
        description="Nederlandse huishoudens gaan minder merken van de Iranoorlog in hun portemonnee dan eerder werd gevreesd. Op één groep na: mensen die veel autokilometers maken en in een slecht geïsoleerd huis wonen, kunnen tot 6 procent van hun koopkracht kwijtraken.",
        url="https://www.ad.nl/politiek/klap-blijft-uit-effect-iranoorlog-minder-groot-voor-meeste-burgers-dan-gevreesd~a215a256/",
    ),
    Document(
        id="3",
        source="AD",
        title="Emiraten leveren bendeleider Shurandy Q. uit aan Curaçao",
        description="De Verenigde Arabische Emiraten hebben een van de leiders van de criminele organisatie No Limit Soldiers (NLS) aan Curaçao uitgeleverd. Het hooggerechtshof van de Emiraten keurde onlangs de uitlevering van Shurandy Q. goed. Het Openbaar Ministerie op Curaçao maakte dat dinsdag bekend.",
        url="https://www.ad.nl/binnenland/emiraten-leveren-bendeleider-shurandy-q-uit-aan-curacao~a4bcd6df/",
    ),
    Document(
        id="4",
        source="AD",
        title="NS waarschuwt reizigers als goedkoop zomerabonnement bijna afloopt, belooft staatssecretaris",
        description="Staatssecretaris Annet Bertram (Infrastructuur en Waterstaat) heeft met de NS besproken dat mensen die een zomerabonnement hebben afgesloten een seintje krijgen als dit bijna afloopt, zodat ze er niet aan vastzitten. „Er is ook aandacht voor'', aldus de bewindsvrouw tijdens een tweeminutendebat over het spoor.",
        url="https://www.ad.nl/binnenland/ns-waarschuwt-reizigers-als-goedkoop-zomerabonnement-bijna-afloopt-belooft-staatssecretaris~a8da2771/",
    ),
    Document(
        id="5",
        source="AD",
        title="Jacht op Russische schaduwvloot: tankers geënterd, fregatten ingezet, maar Nederland kijkt nog toe",
        description="Met het enteren van zeker zes olietankers in het afgelopen halfjaar heeft West-Europa de jacht geopend op de Russische schaduwvloot. Als reactie zet Moskou steeds vaker zwaarbewapende oorlogsfregatten in om de vloot te escorteren. Maar van de Nederlandse marine hebben de Russen voorlopig weinig te vrezen.",
        url="https://www.ad.nl/buitenland/jacht-op-russische-schaduwvloot-tankers-geenterd-fregatten-ingezet-maar-nederland-kijkt-nog-toe~af63b255/",
    ),
    Document(
        id="6",
        source="AD",
        title="Nieuwe coronavariant breidt snel uit in Europa, WHO roept op tot waakzaamheid",
        description="De Wereldgezondheidsorganisatie (WHO) heeft landen opgeroepen waakzaam te blijven na de opkomst van een nieuwe coronavariant die zich snel verspreidt in meerdere Europese landen. Deskundigen adviseren kwetsbare groepen om zich te laten vaccineren.",
        url="https://www.ad.nl/gezondheid/nieuwe-coronavariant-breidt-snel-uit-in-europa-who-roept-op-tot-waakzaamheid~a9cf4521/",
    ),
    Document(
        id="7",
        source="AD",
        title="Klimaatakkoord: Nederland belooft uitstoot te halveren tegen 2030",
        description="De Nederlandse regering heeft op de klimaattop in Parijs beloofd de CO2-uitstoot tegen 2030 te halveren. Milieu-organisaties juichen het besluit toe maar vrezen dat de maatregelen onvoldoende concreet zijn.",
        url="https://www.ad.nl/klimaat/klimaatakkoord-nederland-belooft-uitstoot-te-halveren-tegen-2030~ab12c345/",
    ),
    Document(
        id="8",
        source="AD",
        title="Fietsdiefstal neemt toe in grote steden, politie vraagt om betere sloten",
        description="Het aantal fietsendiefstallen is het afgelopen jaar met 15 procent gestegen in de vier grote steden. De politie roept fietsers op om goede sloten te gebruiken en fietsen dubbel op slot te zetten.",
        url="https://www.ad.nl/binnenland/fietsdiefstal-neemt-toe-in-grote-steden-politie-vraagt-om-betere-sloten~ac23d456/",
    ),
    Document(
        id="9",
        source="AD",
        title="Kunstmatige intelligentie helpt artsen bij diagnose zeldzame ziektes",
        description="Ziekenhuizen in Nederland experimenteren met AI-systemen die artsen helpen bij het diagnosticeren van zeldzame aandoeningen. Eerste resultaten zijn veelbelovend en kunnen wachttijden aanzienlijk verkorten.",
        url="https://www.ad.nl/technologie/kunstmatige-intelligentie-helpt-artsen-bij-diagnose-zeldzame-ziektes~ad34e567/",
    ),
    Document(
        id="10",
        source="AD",
        title="Woningmarkt blijft oververhit: gemiddelde prijs stijgt naar recordhoogte",
        description="De gemiddelde huizenprijs in Nederland is voor het eerst boven de 450.000 euro gestegen. Makelaars waarschuwen dat starters volledig uit de markt worden geprezen zonder ingrijpen van de overheid.",
        url="https://www.ad.nl/wonen/woningmarkt-blijft-oververhit-gemiddelde-prijs-stijgt-naar-recordhoogte~ae45f678/",
    ),
    Document(
        id="11",
        source="AD",
        title="Schiphol schrapt honderden vluchten vanwege personeelstekort",
        description="Schiphol heeft aangekondigd honderden vluchten te schrappen vanwege een groot tekort aan beveiligingspersoneel. Reizigers worden geadviseerd ruim op tijd te komen en rekening te houden met lange wachttijden.",
        url="https://www.ad.nl/reizen/schiphol-schrapt-honderden-vluchten-vanwege-personeelstekort~af56g789/",
    ),
    Document(
        id="12",
        source="AD",
        title="Elektrische auto's winnen aan populariteit: verkoop stijgt met 40 procent",
        description="De verkoop van volledig elektrische auto's is het afgelopen jaar met 40 procent gestegen. Experts voorspellen dat tegen 2035 bijna alle nieuw verkochte auto's elektrisch zullen zijn.",
        url="https://www.ad.nl/auto/elektrische-autos-winnen-aan-populariteit-verkoop-stijgt-met-40-procent~ag67h890/",
    ),
    Document(
        id="13",
        source="AD",
        title="Cybercriminelen richten zich steeds vaker op kleine bedrijven",
        description="Kleine en middelgrote ondernemingen worden steeds vaker het doelwit van cyberaanvallen. Beveiligingsexperts adviseren bedrijven hun digitale beveiliging serieus te nemen en personeel te trainen.",
        url="https://www.ad.nl/technologie/cybercriminelen-richten-zich-steeds-vaker-op-kleine-bedrijven~ah78i901/",
    ),
    Document(
        id="14",
        source="AD",
        title="Droogte bedreigt oogst: boeren vrezen voor mislukte teelt",
        description="Door de aanhoudende droogte vrezen boeren voor hun oogst. Met name de aardappel- en graanteelt staan onder druk. De overheid overweegt noodmaatregelen om de landbouwsector te ondersteunen.",
        url="https://www.ad.nl/binnenland/droogte-bedreigt-oogst-boeren-vrezen-voor-mislukte-teelt~ai89j012/",
    ),
    Document(
        id="15",
        source="AD",
        title="Onderwijsstaking zorgt voor gesloten scholen in heel Nederland",
        description="Leraren in het basisonderwijs hebben vandaag gestaakt voor betere arbeidsvoorwaarden en kleinere klassen. Duizenden scholen blijven dicht en ouders moeten andere opvang regelen voor hun kinderen.",
        url="https://www.ad.nl/onderwijs/onderwijsstaking-zorgt-voor-gesloten-scholen-in-heel-nederland~aj90k123/",
    ),
    Document(
        id="16",
        source="AD",
        title="Sporters vieren Nederlands succes op Olympische Spelen",
        description="Nederlandse atleten hebben op de Olympische Spelen meerdere medailles gewonnen. De zwemmers en wielrenners leverden topprestaties en brachten het totaal op 25 medailles.",
        url="https://www.ad.nl/sport/sporters-vieren-nederlands-succes-op-olympische-spelen~ak01l234/",
    ),
    Document(
        id="17",
        source="AD",
        title="Nieuw medicijn biedt hoop voor Alzheimerpatiënten",
        description="Een nieuw medicijn zou de achteruitgang bij Alzheimerpatiënten kunnen vertragen. Wetenschappers zijn voorzichtig optimistisch maar benadrukken dat meer onderzoek nodig is.",
        url="https://www.ad.nl/gezondheid/nieuw-medicijn-biedt-hoop-voor-alzheimerpatienten~al12m345/",
    ),
    Document(
        id="18",
        source="AD",
        title="Politie rolt internationaal drugsnetwerk op met Europese samenwerking",
        description="Door samenwerking tussen Europese opsporingsdiensten is een groot internationaal drugsnetwerk opgerold. Er zijn tientallen arrestaties verricht en grote hoeveelheden cocaïne en heroïne in beslag genomen.",
        url="https://www.ad.nl/binnenland/politie-rolt-internationaal-drugsnetwerk-op-met-europese-samenwerking~am23n456/",
    ),
    Document(
        id="19",
        source="AD",
        title="Windparken op zee leveren record hoeveelheid energie",
        description="De windparken op de Noordzee hebben dit jaar een recordhoeveelheid elektriciteit opgewekt. Dit draagt bij aan de klimaatdoelen en vermindert de afhankelijkheid van fossiele brandstoffen.",
        url="https://www.ad.nl/klimaat/windparken-op-zee-leveren-record-hoeveelheid-energie~an34o567/",
    ),
    Document(
        id="20",
        source="AD",
        title="Gemeenten worstelen met tekort aan sociale woningen",
        description="Veel gemeenten kampen met een groot tekort aan sociale huurwoningen. De wachtlijsten zijn opgelopen tot meer dan tien jaar in sommige regio's. Corporaties roepen op tot meer nieuwbouw.",
        url="https://www.ad.nl/wonen/gemeenten-worstelen-met-tekort-aan-sociale-woningen~ao45p678/",
    ),
]

TEST_CASES = [
    # ── Baseline: near-verbatim title matches ──
    (
        ["Russische schaduwvloot"],
        "5",
        "[easy]   title near-verbatim — doc 5",
    ),
    (
        ["Emiraten leveren bendeleider Shurandy Q. uit aan Curaçao"],
        "3",
        "[easy]   title near-verbatim — doc 3",
    ),
    (
        ["NS waarschuwt reizigers voor aflopend zomerabonnement"],
        "4",
        "[easy]   title near-verbatim — doc 4",
    ),
    (
        ["Nieuw medicijn biedt hoop voor Alzheimerpatiënten"],
        "17",
        "[easy]   title near-verbatim — doc 17",
    ),
    # ── Medium: paraphrase, different wording than title ──
    (
        ["Russische tankers in beslag genomen door marine"],
        "5",
        "[medium] paraphrase of doc 5 — no shared title phrase",
    ),
    (
        ["koopkracht huishoudens stijgende energiekosten"],
        "2",
        "[medium] paraphrase of doc 2 — Iran-war economic impact",
    ),
    (
        ["alzheimer medicijn vertraagt achteruitgang"],
        "17",
        "[medium] paraphrase of doc 17 — medical vocabulary",
    ),
    (
        ["huizenprijs recordhoogte starters uit markt geprijsd"],
        "10",
        "[medium] paraphrase of doc 10 — housing market",
    ),
    # ── Hard: deep paraphrase, expanded with multiple phrasings ──
    (
        [
            "uitlevering crimineel Caribisch gebied",
            "bendeleider uitgeleverd aan Curaçao",
            "No Limit Soldiers uitlevering Emiraten",
            "Shurandy Q. uitgeleverd",
        ],
        "3",
        "[hard]   expanded: 4 phrasings around extradition doc",
    ),
    (
        [
            "treinabonnement opzeggen herinnering",
            "NS zomerabonnement afloop melding",
            "staatssecretaris Bertram waarschuwing abonnement",
            "goedkoop treinabonnement opzegtermijn",
        ],
        "4",
        "[hard]   expanded: 4 phrasings around NS subscription doc",
    ),
]

HYDE_CACHE = {}

TOP_K = 3

def _ids(results):
    ids = []
    for r in results:
        ids.append(r["db_id"])
    return ids

def _get_db_path():
    return Path(__file__).resolve().parent / "dbs" / "test" / "chroma_db"


def ingest_docs_in_test_db(embedding_model_name: str):
    ingester = Ingester(db_path=_get_db_path(), embedding_model_name=embedding_model_name)
    ingester.delete_articles()
    ingester.__ingest_articles__(sample_docs)
    print(f"Ingested {len(sample_docs)} docs into the test database.")


def mean_reciprocal_rank(embedding_model_name: str):
    retriever = Retriever(db_path=_get_db_path(), embedding_model_name=embedding_model_name)
    mrr_scores = []
    print(f"\n--- MRR with {embedding_model_name} (query expanded) ---")
    for queries, expected_id, note in TEST_CASES:
        results = retriever.retrieve(queries=queries)
        result_ids = _ids(results)
        score = (1 / (result_ids.index(expected_id) + 1)) if expected_id in result_ids else 0
        mrr_scores.append(score)
        match_pos = result_ids.index(expected_id) + 1 if expected_id in result_ids else "—"
        print(f"  {note[:50]} | expected={expected_id} | pos={match_pos} | MRR={score:.1f} | phrasings={len(queries)}")
    mean_mrr = sum(mrr_scores) / len(mrr_scores)
    print(f"  {'─'*95}")
    print(f"  Mean MRR: {mean_mrr:.2f}")

    with open("mrr_scores.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now(), mean_mrr, mrr_scores, embedding_model_name])

def hyde_transform(query: str) -> str:
    llm = LlmHelper()
    """Echte HyDE: LLM genereert hypothetisch nieuwsbericht."""
    messages = [
        {
            "role": "system",
            "content": "Je bent een nieuwsredacteur. Schrijf een kort nieuwsbericht "
                       "van 2-3 zinnen dat past bij de zoekopdracht. Gebruik "
                       "Nederlandse nieuwsstijl. Noem concrete gebeurtenissen, "
                       "organisaties en locaties als die relevant zijn."
        },
        {
            "role": "user",
            "content": f"Zoekopdracht: {query}\n\nSchrijf een nieuwsbericht:"
        },
    ]
    return llm.get_response_with_ollama(messages)



def hyde_recall_test(embedding_model_name: str):
    retriever = Retriever(db_path=_get_db_path(), embedding_model_name=embedding_model_name)

    print(f"\n--- HyDE Recall@{TOP_K} with {embedding_model_name} ---")
    recall_scores = []
    for index, (queries, expected_id, note) in enumerate(TEST_CASES):
        hyde_queries = HYDE_CACHE[tuple(queries)]
        results = retriever.retrieve(queries=hyde_queries)
        result_ids = _ids(results)
        top_k_ids = result_ids[:TOP_K]

        passed = expected_id in top_k_ids
        status = "✔" if passed else "✘"
        print(f"  [{index}] {note[:50]:50s} | expected={expected_id} | top-{TOP_K}={top_k_ids} | {status}")
        recall_scores.append(1 if passed else 0)

    mean_recall = sum(recall_scores) / len(recall_scores)
    print(f"  {'─'*95}")
    print(f"  HyDE Recall@{TOP_K}: {recall_scores} → mean: {mean_recall:.2f}")

    with open("recall_scores.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now(), mean_recall, recall_scores, f"{embedding_model_name} (HyDE)"])


def hyde_mrr_test(embedding_model_name: str):
    retriever = Retriever(db_path=_get_db_path(), embedding_model_name=embedding_model_name)

    print(f"\n--- HyDE MRR with {embedding_model_name} ---")
    mrr_scores = []
    for queries, expected_id, note in TEST_CASES:
        hyde_queries = HYDE_CACHE[tuple(queries)]
        results = retriever.retrieve(queries=hyde_queries)
        result_ids = _ids(results)
        score = (1 / (result_ids.index(expected_id) + 1)) if expected_id in result_ids else 0
        mrr_scores.append(score)
        match_pos = result_ids.index(expected_id) + 1 if expected_id in result_ids else "—"
        print(f"  {note[:50]} | expected={expected_id} | pos={match_pos} | MRR={score:.1f}")
    mean_mrr = sum(mrr_scores) / len(mrr_scores)
    print(f"  {'─'*95}")
    print(f"  HyDE Mean MRR: {mean_mrr:.2f}")

    with open("mrr_scores.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now(), mean_mrr, mrr_scores, f"{embedding_model_name} (HyDE)"])



def recall_test(embedding_model_name: str):
    recall_scores = []
    retriever = Retriever(db_path=_get_db_path(), embedding_model_name=embedding_model_name)

    print(f"\n--- Recall@{TOP_K} with {embedding_model_name} (query expanded) ---")
    for index, (queries, expected_id, note) in enumerate(TEST_CASES):
        results = retriever.retrieve(queries=queries)
        result_ids = _ids(results)
        top_k_ids = result_ids[:TOP_K]

        passed = expected_id in top_k_ids
        status = "✔" if passed else "✘"
        print(f"  [{index}] {note[:50]:50s} | expected={expected_id} | top-{TOP_K}={top_k_ids} | {status} | phrasings={len(queries)}")
        recall_scores.append(1 if passed else 0)

    mean_recall = sum(recall_scores) / len(recall_scores)
    print(f"  {'─'*95}")
    print(f"  Recall@{TOP_K}: {recall_scores} → mean: {mean_recall:.2f}")

    with open("recall_scores.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([datetime.now(), mean_recall, recall_scores, embedding_model_name])


if __name__ == "__main__":
    amount_of_runs = 1

    for run in range(amount_of_runs):
        # Fresh CSV headers each run
        for csv_file, header in [
            ("recall_scores.csv", ["date", "mean recall", "recall scores", "model"]),
            ("mrr_scores.csv",   ["date", "mean mrr",   "mrr scores",   "model"]),
        ]:
            with open(csv_file, "w", newline="") as f:
                csv.writer(f).writerow(header)

        models = ["sentence-transformers/all-MiniLM-L6-v2", "sentence-transformers/all-mpnet-base-v2", "sentence-transformers/all-distilroberta-v1", "BAAI/bge-m3", "intfloat/multilingual-e5-small", "intfloat/multilingual-e5-base"]

        for queries, expected_id, note in tqdm(TEST_CASES):
            print(f"Generating HyDE queries for {note}")
            HYDE_CACHE[tuple(queries)] = [hyde_transform(q) for q in queries]


        for model in models:
            print(f"\n{'='*100}")
            print(f"MODEL: {model}")
            print(f"{'='*100}")
            ingest_docs_in_test_db(model)
            recall_test(model)
            mean_reciprocal_rank(model)
            hyde_recall_test(model)
            hyde_mrr_test(model)
