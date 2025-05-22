def ai_assistant_context(request):
    return {
        'ai_response': request.session.pop('ai_response', None) if hasattr(request, 'session') else None
    }