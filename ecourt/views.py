from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import ECourtsScraper
import json
import os
from datetime import datetime

def index(request):
    """Main page view"""
    return render(request, 'ecourts/index.html')

@csrf_exempt
def get_states(request):
    """API endpoint to get states"""
    scraper = ECourtsScraper()
    states = scraper.get_states()
    return JsonResponse({'states': states})

@csrf_exempt
def get_districts(request):
    """API endpoint to get districts"""
    if request.method == 'POST':
        data = json.loads(request.body)
        state_code = data.get('state_code')
        
        scraper = ECourtsScraper()
        districts = scraper.get_districts(state_code)
        return JsonResponse({'districts': districts})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_court_complexes(request):
    """API endpoint to get court complexes"""
    if request.method == 'POST':
        data = json.loads(request.body)
        state_code = data.get('state_code')
        district_code = data.get('district_code')
        
        scraper = ECourtsScraper()
        complexes = scraper.get_court_complexes(state_code, district_code)
        return JsonResponse({'complexes': complexes})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def get_courts(request):
    """API endpoint to get courts"""
    if request.method == 'POST':
        data = json.loads(request.body)
        state_code = data.get('state_code')
        district_code = data.get('district_code')
        complex_code = data.get('complex_code')
        
        scraper = ECourtsScraper()
        courts = scraper.get_courts(state_code, district_code, complex_code)
        return JsonResponse({'courts': courts})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def download_cause_list(request):
    """API endpoint to download cause list"""
    if request.method == 'POST':
        data = json.loads(request.body)
        state_code = data.get('state_code')
        district_code = data.get('district_code')
        complex_code = data.get('complex_code')
        court_code = data.get('court_code')
        date_str = data.get('date')
        download_all = data.get('download_all', False)
        
        download_path = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_path, exist_ok=True)
        
        scraper = ECourtsScraper()
        
        if download_all:
            results = scraper.download_all_courts_cause_list(
                state_code, district_code, complex_code, date_str, download_path
            )
            return JsonResponse({'results': results})
        else:
            success, message = scraper.download_cause_list(
                state_code, district_code, complex_code, 
                court_code, date_str, download_path
            )
            return JsonResponse({'success': success, 'message': message})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
