from django.http import JsonResponse

def user_list(request):
    return JsonResponse({"message": "Liste des utilisateurs"})
