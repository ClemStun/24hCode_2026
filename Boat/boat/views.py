from django.shortcuts import render
import requests

def index(request):
    resp = requests.get(
        'http://ec2-15-237-116-133.eu-west-3.compute.amazonaws.com:8443/marketplace/offers',
        headers={
            "codinggame-id": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb2RpbmdnYW1lIiwic3ViIjoiMDAyNjQyYzItYmJiMS00OTdkLWFiZTItMDU5ZTA2MGJhNzExIiwicm9sZXMiOlsiVVNFUiJdfQ.bTbRXfHkvrBHYexewru3uX7x3j8L-GfMnXzymkxbU2k"
        }
    )
    offers = resp.json()
    return render(request, 'index.html', {'offers': offers})

