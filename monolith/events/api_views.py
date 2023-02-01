from django.http import JsonResponse

from .models import Conference, Location, State

from common.json import ModelEncoder

from django.views.decorators.http import require_http_methods

import json

from .acls import get_photo, get_weather_data


class ConferenceListEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
    ]


@require_http_methods(["GET", "POST"])
def api_list_conferences(request):
    if request.method == "GET":
        conferences = Conference.objects.all()
        return JsonResponse(
            {"conferences": conferences},
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
    elif request.method == "POST":
        content = json.loads(request.body)
        try:
            location = Location.objects.get(name=content["location"])
            content["location"] = location
        except Location.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid Location Name"},
                status=400,
            )
        conference = Conference.objects.create(**content)
        weather = get_weather_data(
            city=conference.location.city, state=conference.location.state.name
        )

        return JsonResponse(
            {
                "weather": weather,
                "conference": conference,
            },
            encoder=ConferenceListEncoder,
            safe=False,
        )


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = ["name", "city"]


class ConferenceDetailEncoder(ModelEncoder):
    model = Conference
    properties = [
        "name",
        "description",
        "max_presentations",
        "max_attendees",
        "starts",
        "ends",
        "created",
        "updated",
        "location",
    ]
    encoders = {
        "location": LocationListEncoder(),
    }


@require_http_methods(["GET", "PUT", "DELETE"])
def api_show_conference(request, pk):
    if request.method == "GET":
        conference = Conference.objects.get(id=pk)
        weather = get_weather_data(
            city=conference.location.city, state=conference.location.state.name
        )
        return JsonResponse(
            {
                "weather": weather,
                "conference": conference,
            },
            encoder=ConferenceDetailEncoder,
            safe=False,
        )
    elif request.method == "DELETE":
        count, _ = Conference.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    elif request.method == "PUT":
        content = json.loads(request.body)
        if "location" in content:
            try:
                location = Location.objects.get(name=content["location"])
                content["location"] = location
            except Location.DoesNotExist:
                return JsonResponse(
                    {"message": "Invalid Location Name"},
                    status=400,
                )
        Conference.objects.filter(id=pk).update(**content)

        conference = Conference.objects.get(id=pk)
        return JsonResponse(
            conference,
            encoder=ConferenceDetailEncoder,
            safe=False,
        )


class LocationListEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


@require_http_methods(["GET", "POST"])
def api_list_locations(request):
    if request.method == "GET":
        locations = Location.objects.all()
        return JsonResponse(
            {"locations": locations},
            encoder=LocationListEncoder,
        )
    elif request.method == "POST":
        content = json.loads(request.body)
        content["picture_url"] = get_photo(
            city=content["city"], state=content["state"]
        )
        try:
            state = State.objects.get(abbreviation=content["state"])
            content["state"] = state
        except State.DoesNotExist:
            return JsonResponse(
                {"message": "Invalid state abbreviation"},
                status=400,
            )

        location = Location.objects.create(**content)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )


class LocationDetailEncoder(ModelEncoder):
    model = Location
    properties = [
        "name",
        "city",
        "room_count",
        "created",
        "updated",
        "picture_url",
    ]

    def get_extra_data(self, o):
        return {"state": o.state.abbreviation}


@require_http_methods(["GET", "DELETE", "PUT"])
def api_show_location(request, pk):
    if request.method == "GET":
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location, encoder=LocationDetailEncoder, safe=False
        )
    elif request.method == "DELETE":
        count, _ = Location.objects.filter(id=pk).delete()
        return JsonResponse({"deleted": count > 0})
    elif request.method == "PUT":
        content = json.loads(request.body)
        if "state" in content:
            try:
                state = State.objects.get(abbreviation=content["state"])
                content["state"] = state
            except State.DoesNotExist:
                return JsonResponse(
                    {"message": "Invalid state abbreviation"},
                    status=400,
                )
        Location.objects.filter(id=pk).update(**content)
        location = Location.objects.get(id=pk)
        return JsonResponse(
            location,
            encoder=LocationDetailEncoder,
            safe=False,
        )
