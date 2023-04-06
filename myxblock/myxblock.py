"""TO-DO: Write a description of what this XBlock is."""

import datetime
import time
import pkg_resources
import random
import string
import requests
import json
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import  Scope, Integer, String, Boolean
from .utils import render_template

# Disable SSL verification to ignore invalid SSL certificates
requests.packages.urllib3.disable_warnings()

# Configure the API endpoint
host_ip = 'x.x.x.x'
api_key = 'xxxx'
headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}

# Generate a random name for the container
container_name = 'lab-' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32))

class MyXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    container = String(
        default=None, scope=Scope.user_state,
        help="URL for terminal access",
    )

    extra_link = String(
        default=None, scope=Scope.user_state,
        help="Extra URL for terminal access",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the MyXBlock, shown to students
        when viewing courses.
        """
        context = {
            'self': self,
            'container': self.container,
            'extra_link': self.extra_link,
        }

        frag = Fragment()
        frag.add_content(render_template('static/html/myxblock.html', context))
        frag.add_css(self.resource_string("static/css/myxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/myxblock.js"))
        frag.initialize_js('MyXBlock')
        return frag

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def create_container(self, data, suffix=''):
        """
        Creating container.
        """

        # Create the container
        create_url = f'https://{host_ip}:9443/api/endpoints/2/docker/containers/create?name={container_name}'
        create_payload = {
            'Image': 'hands-on-lab-xss:latest', 
            "Tty": True,
            "AttachStdin": True,
            "AttachStdout": True,
            "AttachStderr": True,
            'ExposedPorts': {'80/tcp': {}}, 
            'HostConfig': {'PortBindings': {'80/tcp': [{'HostPort': ''}]}}
            }
        response = requests.post(create_url, headers=headers, data=json.dumps(create_payload), verify=False)

        # Start the container
        start_url = f'https://{host_ip}:9443/api/endpoints/2/docker/containers/{container_name}/start'
        response = requests.post(start_url, headers=headers, data='{}', verify=False)

        # Inspect the container
        inspect_url = f'https://{host_ip}:9443/api/endpoints/2/docker/containers/{container_name}/json?all=true'
        response = requests.get(inspect_url, headers=headers, verify=False)

        # Get the container id and host port
        container_id = response.json()['Config']['Hostname']
        host_port = response.json()['NetworkSettings']['Ports']['80/tcp'][0]['HostPort']

        # Set the link
        web_console_url = f'http://{host_ip}:9999/webconsole/?cid={container_id}'
        web_url = f'http://{host_ip}:{host_port}'

        self.container = web_console_url
        self.extra_link = web_url
        
        return {"container": self.container, "web_url": self.extra_link}
    
    @XBlock.json_handler
    def stop_container(self, data, suffix=''):
        """
        Stopping container.
        """

        # Delete the container
        url = f'https://{host_ip}:9443/api/endpoints/2/docker/containers/{container_name}?v=true&force=true'
        response = requests.delete(url, headers=headers, data='{}', verify=False)

        self.container = None
        self.extra_link = None
        return {'message': 'Container deleted.'}


    @XBlock.handler
    def stop_timer(self, request, suffix=''):
        self.stop_timer()
        return {"elapsed_time": self.elapsed_time}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("MyXBlock",
             """<myxblock/>
             """),
            ("Multiple MyXBlock",
             """<vertical_demo>
                <myxblock/>
                <myxblock/>
                <myxblock/>
                </vertical_demo>
             """),
        ]
