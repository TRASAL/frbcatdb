'''
description:    Create a db entry for a VOEvent
license:        APACHE 2.0
author:         Ronald van Haren, NLeSC (r.vanharen@esciencecenter.nl)
'''
from pyfrbcatdb.logger import logger
import requests
import json
import datetime
import os
import yaml
import sys
from urllib.parse import urljoin


class zenodo(logger):
    '''
    Class module that uploads a CSV file to Zenodo

    :param access_token: Zenodo access token
    :param CSV: CSV filename on systme
    :param logfile: log filename on system
    :param sandbox: use Zenodo sandbox environment for testing
    :type access_token: str
    :type CSV: str
    :type logfile: str
    :type sandbox: bool
    '''

    def __init__(self, access_token, CSV, logfile, sandbox=False):
        logger.__init__(self, logfile)
        self.access_token = access_token
        self.CSV = CSV
        self.sandbox = sandbox
        self.setBaseUrl()
        self.parse_metadata()
        self.uploadToZenodo()

    def setBaseUrl(self):
        '''
        Set Zenodo baseurl
        Need to use the sandbox environment for testing
        '''
        if not self.sandbox:
            self.baseurl = "https://zenodo.org/"
        else:
            self.baseurl = "https://sandbox.zenodo.org/"

    def parse_metadata(self):
        '''
        Read metadata from json file
        '''
        # define path to zenodo.json file
        filename = "zenodo.json"
        mfile = os.path.join(os.path.dirname
                             (sys.modules['pyfrbcatdb'].__file__),
                             filename)  # path to file
        with open(mfile) as f:
            self.metadata = yaml.safe_load(f)

    def uploadToZenodo(self):
        '''
        upload CSV file to Zenodo
        '''
        headers = {"Content-Type": "application/json"}
        titlestr = self.metadata['metadata']['title']
        # convert to elasticseartch string
        titlestrES = titlestr.split()[0] + ' AND ' + titlestr.split()[0]
        while True:
            try:
                resp = requests.get(urljoin(self.baseurl,
                                            '/api/deposit/depositions'),
                                    params={'q': titlestrES,
                                            'access_token': self.access_token})
                if not resp.json()[0]['submitted']:
                    delID = resp.json()[0]['record_id']
                    rdel = requests.delete(urljoin(self.baseurl, 'api/deposit/depositions/{}'.format(delID)),
                                           params={'access_token': self.access_token})
                    if (int(rdel.status_code) not in [204, 410]):
                        # 204: DELETE request succeeded
                        # 410: PID has been deleted
                        print(rdel.json())
                        raise IOError('Unable to delete unsubmitted entry from Zenodo')
                else:
                    # id of previous version
                    deposition_id = resp.json()[0]['record_id']
                    # get new version deposition_id
                    resp = requests.post(urljoin(self.baseurl, 'api/deposit/depositions/{}/actions/newversion'.format(deposition_id)),
                                         params={'access_token': self.access_token})
                    newversion_draft_url = resp.json()['links']['latest_draft']
                    deposition_id = int(newversion_draft_url.split("/")[-1])
                    break
            except IndexError:
                # create a new entry
                resp = requests.post(urljoin(self.baseurl, 'api/deposit/depositions'),
                                     params={'access_token': self.access_token},
                                     json={},
                                     headers=headers)
                # Get the deposition id from the previous response
                deposition_id = resp.json()['id']
                break
        # define version and set version in metadata
        version = datetime.datetime.now().strftime('%Y.%m.%d')
        versionFn = datetime.datetime.now().strftime('%Y_%m_%d')
        self.metadata['metadata']['version'] = version
        data = {'filename': "frbcat-{}.csv".format(versionFn)}
        # define file to upload
        files = {'file': open(self.CSV, 'rb')}
        resp = requests.post(urljoin
                             (self.baseurl, 'api/deposit/depositions/{}/files'.format(deposition_id)),
                             params={'access_token': self.access_token},
                             data=data,
                             files=files)
        # rename file to the one specified in data if needed
        if (resp.json()['filename'] != data['filename']):
            url = resp.json()['links']['self']
            url = url + '?access_token=' + self.access_token
            resp = requests.put(url,
                                data=json.dumps(data),
                                headers=headers)
        resp = requests.put(urljoin(self.baseurl, 'api/deposit/depositions/{}'.format(deposition_id)),
                            params={'access_token': self.access_token},
                            data=json.dumps(self.metadata),
                            headers=headers)
        # upload the actual file
        resp = requests.post(urljoin
                             (self.baseurl, 'api/deposit/depositions/{}/actions/publish'.format(deposition_id)),
                             params={'access_token': self.access_token})
