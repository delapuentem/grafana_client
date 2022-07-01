#!/usr/bin/env python3
import requests, re

class GrafanaApiClient:
    def __init__(self, host, port, token):
        self.grafana_host = host
        self.grafana_port = port
        self.grafana_token = token

        self.headers = {'Authorization': f'Bearer {self.grafana_token}',}

    def get_datasources(self):
        '''Return a list of raw dicts with datasoruces information'''
        response = requests.get(f'http://{self.grafana_host}:{self.grafana_port}/api/datasources/', headers=self.headers)
        return response.json()

    def get_folders(self):
        '''Return list of dicts with folders info'''
        response = requests.get(f'http://{self.grafana_host}:{self.grafana_port}/api/search?query=%', headers=self.headers)
        return [item for item in response.json() if item['type'] == 'dash-folder']

    def get_dashboards(self):
        '''Return list of dicts with dashboards info'''
        response = requests.get(f'http://{self.grafana_host}:{self.grafana_port}/api/search?query=%', headers=self.headers)
        return [item for item in response.json() if item['type'] == 'dash-db']

    def get_dashboard_json(self, dashboard_uid):
        '''Return the raw dashboard JSON'''
        response = requests.get(f'http://{self.grafana_host}:{self.grafana_port}/api/dashboards/uid/{dashboard_uid}/', headers=self.headers)
        return response.json()

    def get_dashboard_panels(self, dashboard_uid):
        '''Return a list of dicts with the folder name, dashboard name, panel type, panel name, panel datasource, panel database and measurements for each panel of the dashboard'''
        # Exclude panels. Types of panels that you will not consider
        exclude_panels = ('row',)

        def __get_database_from_datasource(datasource):
            '''Return the database type, and database name from datasource name'''
            # The datasources info list
            datasources_list = [dict(name=item['name'], database=item['database'], type=item['type'], isDefault=item['isDefault']) for item in self.get_datasources()]
            # If datasource value is None, get the default datasource and database
            if datasource == 'None':
                return next(filter(lambda data: str(data['isDefault']) == str(True), datasources_list))
            else:
                # Return the first match, because there cannot be two datasources with the same name
                return next(filter(lambda data: str(data['name']) == str(datasource), datasources_list))

        def __get_datasource_from_variable(datasource, templating_list):
            # If datasource is None (default datasource) convert None type to string
            if datasource is None:
                datasource = str(datasource)
            # If datasource name starts with dollar, is a variable
            if bool(re.findall('\B\$\w+', datasource)) is True:
                datasource_variable = str(re.findall('\B\$\w+', datasource)[0]).replace('$', '')
                datasource = next(filter(lambda item: item['name'] == datasource_variable, templating_list))['current']['value']
            return datasource

        def __get_influxdb_measurements(target):
            # Search measurements in query regex formats
            measurement_regex_formats = (
                ('FROM ["\']\w+["\']'),
                ('FROM [\"\']\w+[\\w.]+\w+[\"\']'),
            )
            # If the query have made with query constructor rawQuery = False, if query is hand made rawQuery = True
            measurements = []
            raw_query = target['rawQuery'] if 'rawQuery' in target else False
            if raw_query is False:
                # Get the measurement of the panel
                measurements.append(target['measurement'] if 'measurement' in target else None)
            else:
                # Get the measurements of the query
                panel_query = str(target['query']).replace('\n', '')
                # Get the match regex format andvalues in the query
                for regex in measurement_regex_formats:
                    for item in re.findall(regex, panel_query):
                        measurements.append(str(item).replace('FROM ', '').replace('\'', '').replace('"', ''))
            return list(set(measurements))

        # Get the raw dashboard JSON and get the info into a dict
        dashboard_json = self.get_dashboard_json(dashboard_uid)
        # Has panels ? -> If have panels get the list, if not declare empty list
        panel_list = dashboard_json['dashboard']['panels'] if 'panels' in dashboard_json['dashboard'] else []
        # Get the data for each panel, excluding the exclude_panels
        raw_dashboard_panels = [dict(dashboard_folder_title = dashboard_json['meta']['folderTitle'], dashboard_title=dashboard_json['dashboard']['title'],
            panel_title=item['title'], panel_datasource=__get_datasource_from_variable(item['datasource'], dashboard_json['dashboard']['templating']['list']),
            targets=item['targets'],
            ) for item in panel_list if item['type'] not in exclude_panels]

        # Find measurements into queries in each panel for panels in raw_dashboard_panels -> targets
        dashboard_panels = []
        # For each panel in the dashboard
        for panel in raw_dashboard_panels:
            # Determinate the database name from the datasource type
            datasource_info = __get_database_from_datasource(panel['panel_datasource'])
            # For each query in each panel
            for target in panel['targets']:
                # If the query panel is hide, next
                if (target['hide'] if 'hide' in target else False) is False:
                    # For INFLUXDB type databases
                    if datasource_info['type'] == 'influxdb':
                        measurements = __get_influxdb_measurements(target)
                    # For OTHER type databases
                    else:
                        next
                    # Add measurements values
                    for measurement in measurements:
                        # Set 'default' name to panel_datasource if is None
                        panel_datasource = datasource_info['name'] if panel['panel_datasource'] == 'None' else panel['panel_datasource']
                        # For each muasurement append panel info to dashboard panels
                        dashboard_panels.append(dict(
                            dashboard_folder_title = panel['dashboard_folder_title'], dashboard_title=panel['dashboard_title'],
                            panel_title=panel['panel_title'], panel_datasource=panel_datasource, panel_measurement=measurement, panel_database=datasource_info['database'], panel_database_type=datasource_info['type']))
        return dashboard_panels
