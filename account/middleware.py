from django.shortcuts import redirect

class GatewayMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):

        if request.user.is_authenticated:
            
            managers = request.user.is_superuser or request.user.is_assistant
            
            if 'admin' in request.path and not managers:

                return redirect("account:dashboard")
            
        return self.get_response(request)


























