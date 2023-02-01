from django.http import JsonResponse

from .models import Attendee, ConferenceVO, AccountVO

from common.json import ModelEncoder

from django.views.decorators.http import require_http_methods

import json


class ConferenceVODetailEncoder(ModelEncoder):
    model = ConferenceVO
    properties = ["name", "import_href"]


class AttendeesListEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
    ]
    encoders = {
        "conference": ConferenceVODetailEncoder(),
    }


class AttendeesDetailEncoder(ModelEncoder):
    model = Attendee
    properties = [
        "email",
        "name",
        "company_name",
        "created",
        "conference",
    ]
    encoders = {
        "conference": ConferenceVODetailEncoder(),
    }

    def get_extra_data(self, o):
        has_account = False
        for account in AccountVO.objects.all():
            if o.email == account.email:
                has_account = True
        if has_account:
            return {"has_account": True}
        else:
            return {"has_account": False}


@require_http_methods(["GET", "POST"])
def api_list_attendees(request, conference_vo_id=None):
    if request.method == "GET":
        conference_href = f"/api/conferences/{conference_vo_id}/"
        conference = ConferenceVO.objects.get(href=conference_href)
        attendees = Attendee.objects.filter(conference=conference)
        return JsonResponse(
            {"attendees": attendees}, encoder=AttendeesListEncoder
        )
    else:
        content = json.loads(request.body)
        print(content)
        try:
            # THIS LINE IS ADDED
            conference_href = content["conference"]

            # THIS LINE CHANGES TO ConferenceVO and import_href
            conference = ConferenceVO.objects.get(import_href=conference_href)

            content["conference"] = conference

            ## THIS CHANGES TO ConferenceVO
        except ConferenceVO.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid conference id"},
                status=400,
            )

        attendee = Attendee.objects.create(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeesDetailEncoder,
            safe=False,
        )


@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_attendee(request, pk):
    if request.method == "GET":
        attendee = Attendee.objects.get(id=pk)
        return JsonResponse(
            attendee,
            encoder=AttendeesDetailEncoder,
            safe=False,
        )

    elif request.method == "DELETE":
        count, _ = Attendee.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})

    elif request.method == "PUT":
        content = json.loads(request.body)
        if "conference" in content:
            try:
                conference = Conference.objects.ge(
                    name=content["conference_name"]
                )
                content["conference_name"] = conference
            except Conference.DoesNotExist:
                return JsonResponse(
                    {"message": "Invalid Conference Name"},
                    status=400,
                )
        attendee = Attendee.objects.filter(id=pk).update(**content)
        return JsonResponse(
            attendee,
            encoder=AttendeesDetailEncoder,
            safe=False,
        )
