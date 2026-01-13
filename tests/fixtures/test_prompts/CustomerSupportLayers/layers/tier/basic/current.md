{% block escalation %}
Escalation Policy:
- Escalate to senior support after 3 failed attempts
- Offer callback during business hours only
- Response time: within 24 hours
{% endblock %}

{% block capabilities %}
{{ super() }}

Basic Tier Limitations:
- Email support only
- Standard response times
- Self-service resources available
{% endblock %}
