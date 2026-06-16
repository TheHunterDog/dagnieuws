from summarizer import Summarizer

summarizer = Summarizer()
summary = summarizer.summarize_using_ollama("Feyenoord staat op het punt Giovanni van Bronckhorst aan te stellen als hoofdtrainer, melden VI, ESPN, het AD en transferjournalist Fabrizio Romano. De oud-speler was van 2015 tot 2019 al trainer van de Rotterdammers. Sipke Hulshoff gaat een belangrijke rol vervullen als assistent")

print(summary)