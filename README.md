Note: 
-------------------------------------------------------------------------------------------
ip_local = 127.0.0.0
ip_de_la_machine = (pour recuperer l'adresse ip d'une machine on tape la commande ipconfig) 
ctrl + c : pour arreter le serveur
l'esp, le telephone et l'ordinateur doivent etre dans le meme reseau
la synthese vocal ne marche correctement que dans microsof edge
------------------------------------------------------------------------------------------

une fois que tu clone ou telecharge le projet tu dois te rassurer que python est installer dans ton ordi
1) Ouvrir le repertoire (medibox) sur vscode en suite t'ouvre le teminale et tu tape la commande suivante pour activer l'environnement virtuel : env/Scripts/activate
1-1)  si la commande marche sans probleme tu peux deja lancer le programme pour un test en la commande suivante : py manage.py runserver 
1-2) si la commande d'activation de l'environnement virtuel ne marche pas alors tu dois supprimer le dossier (env) en suite tu tape cette commande dans le terminal : pip install -r req.txt pour installer les dependances que j'ai stoqué dans le fiichier req.txt
2) pour la creation d'un compte d'administrateur tu dois taper la commande suivante et suivre les instructons : py manage.py createsuperuser
3) une fois le compte d'aministrateur crée tu relances le serveur a fin de pouvoir utiliser l'application : py manage.py runserver 
4) ensuite tu te rends sur l'url ip_local:8000/sadmin pour te connecter sur la page d'admin, en suite tu pourras ajouter un medecin, les produits etc...
5) pour connecter un medecin et faire une prescription tu te rend sur l'url ip_local:8000/medecin
   
#les modifications à apporter dans le code pour faire comminiquer le systeme avec un telephone et l'ESP
1) tu te rends dans le repertoire param_seribox/settings.py et tu ajoutes l'adresse ip de ta machine dans le tableau ALLOWED_HOSTS
2) tu te rends dans le repertoire app_medibox/views.py et tu cherches "adresse_ip_esp" pour etre rapide tape ctrl + f, et tu ajoutes "adresse_ip_esp" dans la barre de recherche, pour chaque variable adresse_ip_esp tu l'affectes l'adresse ip de l'esp sous la forme : adresse_ip_esp = "http://ip_de_l'esp:80"
3) les modifications sont enfin finies maintenant tape la commande suivante dans le terminal : py manage.py runserver 0.0.0.0:8000
4) maintenant tu peux te connecter au site avec ton telephone en ecrivant l'url suivante dans le navigateur : ip_de_la_machine:8000
5) Fiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii

