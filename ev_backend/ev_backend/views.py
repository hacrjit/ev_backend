# core/views.py
from django.http import HttpResponse

def home(request):
    html = """
    <h1>Welcome to the EV Backend API</h1>
    <ul>
        <li><a href="/admin/">/admin/</a></li>
        <li><a href="/api/accounts/">/api/accounts/</a></li>
        <li><a href="/api/auth/social/">/api/auth/social/</a></li>
        <li><a href="/api/vehicles/">/api/vehicles/</a></li>
        <li><a href="/api/stations/">/api/stations/</a></li>
        <li><a href="/api/wallet/">/api/wallet/</a></li>
    </ul>
    """
    return HttpResponse(html)
