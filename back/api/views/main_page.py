from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


def get_public_data(user: User | None):
    if user and user.is_authenticated:
        return {'applications': [] }
    data = [
        {
            'app_id': 'Tasks',
            'icon': 'check2-square',
            'title': 'Capabilities:',
            'features': [
                'Combining tasks into lists, and lists into groups.',
                'Search by name, task description and task categories.',
                'Reminder of tasks by pop-up messages of the browser on the computer and in the phone.',
                'For each task, execution stages can be set, tracking of the execution of both the task itself and its stages is available.',
                'For a task, a due date, frequency of repetition, date and time of reminder can be set.',
                'A task can be marked as "important" or as added to the "My Day" view.',
                'Each task can be assigned an arbitrary number of "categories" and filter the list of tasks by them.',
                'In the task, you can specify a hyperlink to an external Internet resource.',
                'You can attach an arbitrary number of files to the task.',
            ],
        },
        {
            'app_id': 'Note',
            'icon': 'sticky',
            'title': 'Personal notes about everything. For each note, in addition to the description, you can specify a hyperlink to an external Internet resource, an arbitrary number of categories, attach files. Notes, like tasks, are combined into lists, and lists into groups. Notes can be searched by title, description, and category.',
            'features': [],
        },
        {
            'app_id': 'News',
            'icon': 'newspaper',
            'title': 'Similar to a list of notes, but the emphasis is on the date-time of publication.',
            'features': [],
        },
        {
            'app_id': 'Proj',
            'icon': 'piggy-bank',
            'title': 'Allows you to track costs for several projects. Multiple currencies can be selected for accounting and totals.',
            'features': [],
        },
        {
            'app_id': 'Fuel',
            'icon': 'droplet',
            'title': 'For the car owner the ability to control fuel consumption, as well as the frequency of service maintenance and replacement of consumable materials.',
            'features': [],
        }
    ]

    return {'applications': data }

@api_view(['GET'])
@permission_classes([IsAuthenticatedOrReadOnly])
def main_page(request):
    data = get_public_data(request.user)
    return Response(data)

