# Mi Proyecto

Acabo de inicializar el git llamado `autocontent_podcast`. 
En este repositorio quiero lograr como output final 5 posts de linkedin a publicar en ingles en la cuenta de Brain Response (consultora de neurotecnologia) sobre temas de interes que se discutan en el podcast.
Para eso, en la subdir `./episode_2_viewmind` ya tengo el .mp3 del audio del entrevistado (guardado como `guest.mp3`. Tambien en ese subdir tengo mi audio en otra pista (guardado como `host.mp3`).
Entiendo que los pasos a hacer se.
En esa misma subdir tengo tambien el documento de preproduccion que contiene, entre otras cosas, algunas de las preguntas que planeaba hacerle a Gerardo.

A continaucion voy a describir la serie de pasos que me imagino deberiamos ejecutar para poder llevar a cabo este proyecto:

1. Los archivos guest - host y preproduction ponerlos adentro de una carpeta que sea `./raw` en la carpeta del episodio
2. A traves de alguna libreira gratis (como whisper) crear un script que pueda desgrabar la respuesas del invitado (guest.mp3) y depositarlas en un una nueva carpeta dentro de la carpeta del episodio que se llame `./processed` guardado como un .txt
3. Ahora hacer lo mismo pero con el archivo del host.
4. A traves de usar API Call de algun LLM, crear un nuevo documento .txt que una preguntas del host y respuestas del entrevistado.
5. Con otra llamada a un modelo de LLM considerar el docuento de preproduccion `preproduction.txt` y las dos transcripciones de preguntas y respuestas del entrevistado, y crear a partir de esto 5 posts de linkedin sobre la informacion mas valiosa del podcast para el publico del podast. Considera que estos post en linkedin deben tener valor principalmente para: founders de startups de neurotecnologia, key opinion leaders de neurotecnologia, personas de departamnetos de innovacion o de R/D intereados en neurotencologia, invesores interesaods en neurotecnologia o bien cientificos interesados en emprender. Estos posts deben ser guardados en otra subdir del episodio llamada `./linkedin_posts`