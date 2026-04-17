Enregistrez et renommez votre clé json dans le dossier `/credentials/letudiant-data-prod-albert.json`

Build une image et test d'une premiere requête
```sh
docker build . -t albert && docker run --rm python:3.14 index.py 
```
