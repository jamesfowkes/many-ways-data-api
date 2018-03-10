# many-ways-data-api
This is for Hack24 2018 by team Big Unknown.


    wme@django2 ~/D/H/2/many-ways-data-api> curl http://localhost:5000/manyways/
    {
        "end": "amerillo", 
        "start": "nottingham"
    }
    wme@django2 ~/D/H/2/many-ways-data-api> curl http://localhost:5000/manyways/nottingham/leicester/
    {
        "end": "leicester", 
        "start": "nottingham"
    }

