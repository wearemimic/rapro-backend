from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
import json

# @csrf_exempt
# def login_view(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         email = data.get('email')
#         password = data.get('password')
#         # TODO: authenticate
#         if email == 'test@example.com' and password == 'password':
#             return JsonResponse({'status': 'success', 'token': 'exampletoken'})
#         else:
#             return JsonResponse({'status': 'fail'}, status=401)
#             return JsonResponse({'error': 'Invalid method'}, status=405)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data.get("refresh")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logged out successfully"}, status=205)
    except Exception as e:
        return Response({"error": str(e)}, status=400)       
    
