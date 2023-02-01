from django.http import JsonResponse

from .models import Presentation, Status
from events.models import Conference
from events.api_views import ConferenceListEncoder
from common.json import ModelEncoder

from django.views.decorators.http import require_http_methods

import json
import pika


class PresentationListEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "title",
    ]

    def get_extra_data(self, o):
        return {"status": o.status.name}


@require_http_methods(["GET", "POST"])
def api_list_presentations(request, conference_id):
    if request.method == "GET":
        conference = Conference.objects.get(id=conference_id)
        presentations = Presentation.objects.filter(conference=conference)
        return JsonResponse(
            {"presentations": presentations},
            encoder=PresentationListEncoder,
        )
    elif request.method == "POST":
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(name=content["conference"])
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Conference Name"},
                status=400,
            )
        presentation = Presentation.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


class PresentationDetailEncoder(ModelEncoder):
    model = Presentation
    properties = [
        "presenter_name",
        "company_name",
        "presenter_email",
        "title",
        "synopsis",
        "created",
        "conference",
    ]

    encoders = {
        "conference": ConferenceListEncoder(),
    }

    def get_extra_data(self, o):
        return {"status": o.status.name}


@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_presentation(request, pk):
    if request.method == "GET":
        presentation = Presentation.objects.get(id=pk)

        return JsonResponse(
            presentation, encoder=PresentationDetailEncoder, safe=False
        )
    elif request.method == "DELETE":
        count, _ = Presentation.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    elif request.method == "PUT":
        content = json.loads(request.body)
        try:
            conference = Conference.objects.get(name=content["conference"])
            content["conference"] = conference
        except Conference.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Conference Name"},
                status=400,
            )
        try:
            status = Status.objects.get(name=content["status"])
            content["status"] = status
        except Status.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Status"},
                status=400,
            )
        presentation = Presentation.objects.create(**content)
        return JsonResponse(
            presentation,
            encoder=PresentationDetailEncoder,
            safe=False,
        )


@require_http_methods(["PUT"])
def api_approve_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.approve()

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_approvals")
    data = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    data_json = json.dumps(data)
    channel.basic_publish(
        exchange="",
        routing_key="presentation_approvals",
        body=data_json,
    )
    connection.close()
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )


@require_http_methods(["PUT"])
def api_reject_presentation(request, pk):
    presentation = Presentation.objects.get(id=pk)
    presentation.reject()

    parameters = pika.ConnectionParameters(host="rabbitmq")
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue="presentation_rejections")
    data = {
        "presenter_name": presentation.presenter_name,
        "presenter_email": presentation.presenter_email,
        "title": presentation.title,
    }
    data_json = json.dumps(data)
    channel.basic_publish(
        exchange="",
        routing_key="presentation_rejections",
        body=data_json,
    )

    connection.close()
    return JsonResponse(
        presentation,
        encoder=PresentationDetailEncoder,
        safe=False,
    )
