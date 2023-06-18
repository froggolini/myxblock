import os
import pkg_resources
import random
import string
import requests
import json
import fnmatch
import time
import logging
from datetime import datetime
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import  Scope, Integer, String, Boolean
from .utils import render_template
from xblockutils.studio_editable import StudioEditableXBlockMixin

# Logging
log = logging.getLogger(__name__)

# Disable SSL verification 
requests.packages.urllib3.disable_warnings()

# Portainer API
host_ip = '44.214.9.8'
api_key = 'xxx'
headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}

container_name = ''

@XBlock.needs("i18n")
class MyXBlock(StudioEditableXBlockMixin, XBlock):
    stack_id = Integer(
        default=0, scope=Scope.user_state,
        help="Stack ID",
    )

    container = String(
        default=None, scope=Scope.user_state,
        help="URL for terminal access",
    )

    extra_link = String(
        default=None, scope=Scope.user_state,
        help="Extra URL for terminal access",
    )

    extra_link_2 = String(
        default=None, scope=Scope.user_state,
        help="Extra URL for phpmyadmin access",
    )

    ssh_ip = String(
        default=None, scope=Scope.user_state,
        help="IP for ssh",
    )

    db_ip = String(
        default=None, scope=Scope.user_state,
        help="IP for db",
    )

    selected_value = String(
        default=None, scope=Scope.user_state,
        help="Image name",
    )

    container_name = String(
        default=None, scope=Scope.user_state,
        help="Container name",
    )

    xblock_type = String(
        display_name="Image type",
        help="Image for the lab. Available = xss / sqli",
        default='sqli',
        scope=Scope.content
    )
    editable_fields = ('xblock_type', 'display_name')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the MyXBlock, shown to students
        when viewing courses.
        """
        context = {
            'self': self,
            'container': self.container,
            'extra_link': self.extra_link,
            'extra_link_2': self.extra_link_2,
            'ssh_ip': self.ssh_ip,
            'db_ip': self.db_ip,
            'image_name': self.selected_value,
            'type': self.xblock_type
        }
        
        frag = Fragment()
        frag.add_content(render_template('static/html/myxblock.html', context))
        frag.add_css(self.resource_string("static/css/myxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/myxblock.js"))
        frag.initialize_js('MyXBlock', {'type': self.xblock_type})
        return frag

    @XBlock.json_handler
    def studio_submit(self, submissions, suffix=''):
        if submissions['xblock_type']== "":
            response = {
                'result': 'error',
                'message': 'You should give xblock type'
            }
        else:
            log.info(u'Received submissions: {}'.format(submissions))
            self.xblock_type = submissions['xblock_type']
            response = {
                'result': 'success',
            }
        return response
    
    @XBlock.json_handler
    def create_container(self, data, suffix=''):
        """
        Creating container.
        """
        start = time.perf_counter()
        
        if data['imageName'] not in ('xss', 'sqli'):
            print('error!')
            return
        
        if data['imageName'] == 'xss':
            self.selected_value = data['imageName']
            container_name = 'xss-' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32))
            
            # Create container
            create_url = f'https://{host_ip}:9443/api/endpoints/2/docker/containers/create?name={container_name}'
            create_payload = {
            'Image': 'web-xss:latest',
            'Tty': True,
            'ExposedPorts': {'80/tcp': {}},
            'HostConfig': {'PortBindings': {'80/tcp': [{'HostPort': ''}]}}
        }
            response = requests.post(create_url, headers=headers, data=json.dumps(create_payload), verify=False)
            dateTimeObj = datetime.now()
            print("[{}]  -  POST {}  -  {}".format(dateTimeObj,"/create",response.elapsed))

            # Start 
            start_url = f'https://{host_ip}:9443/api/endpoints/2/docker/containers/{container_name}/start'
            response = requests.post(start_url, headers=headers, data='{}', verify=False)

            # Inspect 
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

        else:
            self.selected_value = data['imageName']
            container_name = 'sqli-' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32))
            container_name = container_name.lower()

            # Create stack (compose)
            create_stack_url = f"https://{host_ip}:9443/api/stacks?type=2&method=string&endpointId=2"
            payload = json.dumps({
            "Name": container_name,
            "StackFileContent": self.resource_string("docker-compose.yml"),
            "Env": [],
            "Webhook": ""
            })
            response = requests.post(create_stack_url, headers=headers, data=payload, verify=False)
            self.stack_id = response.json()["Id"]

            # Get phpmyadmin port
            get_phpmyadmin = f"https://{host_ip}:9443/api/endpoints/2/docker/containers/json?filters={{\"label\": [\"com.docker.compose.project={container_name}\"], \"name\": [\"phpmy\"]}}" 
            response = requests.get(get_phpmyadmin, headers=headers, data={}, verify=False)
            phpmyadmin_port = response.json()[0]["Ports"][0]["PublicPort"]
            
            # Get apache ip and port
            get_apache= f"https://{host_ip}:9443/api/endpoints/2/docker/containers/json?filters={{\"label\": [\"com.docker.compose.project={container_name}\"], \"name\": [\"apache\"]}}" 
            response = requests.request("GET", get_apache, headers=headers, verify=False)
            apache_port = response.json()[0]["Ports"][3]["PublicPort"]
            
            networks = response.json()[0]['NetworkSettings']['Networks']
            for network_name in networks:
                if fnmatch.fnmatch(network_name, '*'):
                    ip_ssh = networks[network_name]['IPAddress']
                    self.ssh_ip = ip_ssh
            
            # Get ssh ip
            get_apache= f"https://{host_ip}:9443/api/endpoints/2/docker/containers/json?filters={{\"label\": [\"com.docker.compose.project={container_name}\"], \"name\": [\"db\"]}}" 
            response = requests.request("GET", get_apache, headers=headers, verify=False)
            
            networks = response.json()[0]['NetworkSettings']['Networks']
            for network_name in networks:
                if fnmatch.fnmatch(network_name, '*'):
                    ip_db = networks[network_name]['IPAddress']
                    self.db_ip = ip_db

            # Get attacker id
            get_apache= f"https://{host_ip}:9443/api/endpoints/2/docker/containers/json?filters={{\"label\": [\"com.docker.compose.project={container_name}\"], \"name\": [\"attacker\"]}}" 
            response = requests.request("GET", get_apache, headers=headers, verify=False)
            attacker_id = response.json()[0]["Id"]

            # Set the link
            web_console_url = f'http://{host_ip}:9999/webconsole/?cid={attacker_id}'
            web_url = f'http://{host_ip}:{apache_port}'
            phpmyadmin_url = f'http://{host_ip}:{phpmyadmin_port}'

            dateTimeObj = datetime.now()
            print("[{}]  -  POST {}  -  {}".format(dateTimeObj,"/stacks",response.elapsed))

            self.container = web_console_url
            self.extra_link = web_url
            self.extra_link_2 = phpmyadmin_url
            
        self.container_name = container_name
        request_time = time.perf_counter() - start
        print("Start container request completed in {0:.0f}s".format(request_time))
        
        return {"container": self.container, "web_url": self.extra_link, "php_url": self.extra_link_2, "ssh_ip": self.ssh_ip, "db_ip": self.db_ip}
    
    @XBlock.json_handler
    def stop_container(self, data, suffix=''):
        """
        Stopping container.
        """
        start = time.perf_counter()

        if data['imageName'] == 'xss':
            # Delete the container
            url = f'https://{host_ip}:9443/api/endpoints/2/docker/containers/{self.container_name}?v=true&force=true'
            response = requests.delete(url, headers=headers, data='{}', verify=False)
            
            dateTimeObj = datetime.now()
            print("[{}]  -  DELETE {}  -  {}".format(dateTimeObj,"/containers",response.elapsed))
            print("deleted")
        else:
            # Delete the container
            url = f'https://{host_ip}:9443/api/stacks/{self.stack_id}?endpointId=2'
            response = requests.delete(url, headers=headers, verify=False)

            dateTimeObj = datetime.now()
            print("[{}]  -  DELETE {}  -  {}".format(dateTimeObj,"/stacks",response.elapsed))
            print("deleted")
        
        request_time = time.perf_counter() - start
        print("Delete container request completed in {0:.0f}s".format(request_time))

        self.container = None
        self.extra_link = None
        self.extra_link_2 = None
        self.container_name = None
        self.stack_id = 0
        self.ssh_ip = None
        self.db_ip = None
        self.selected_value = None

        return {'message': 'Container deleted.'}
            
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