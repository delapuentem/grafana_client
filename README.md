# Grafana API Client
Custom library of tools for working with dates in any format in Python 3.x

## How to use

Make sure you have generated the api token with the necessary permissions at http://my-grafana-server:3000/api/dashboards/home

Import the library and inicialize GrafanaApiClient class.

```python
#!/usr/bin/env python3
import grafana_client

# Grafana API Token
grafana_token = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx''

# Make a connection with Grafana API
grafana_api_client = grafana_client.GrafanaApiClient(host='grafana-server-or-ipaddress', port='3000', token=grafana_token)
```

### get_datasources
Return a list of raw dicts with datasoruces information.

```python
grafana_api_client.get_datasources()
```

### get_folders
Return list of dicts with folders info.

```python
get_folders()
```

### get_dashboards
Return list of dicts with dashboards info.

```python
get_dashboards()
```

### get_dashboard_json
Return the raw dashboard JSON.

```python
get_dashboard_json(dashboard_uid='xxxxxxx')
```

### get_dashboard_panels
Return a list of dicts with the folder name, dashboard name, panel type, panel name, panel datasource, panel database and measurements for each panel of the dashboard.

```python
get_dashboard_panels(dashboard_uid='xxxxxxx')
```

For each measurement in each panel of the dashboard, return the following info:
- Dashboard folder name
- Dashboard name
- Panel title and type
- Panel datasource and database
- Panel measurement

**Exclude panels**

We can exclude by the type of panel. By default, row panel is excluded.

```python
get_dashboard_panels(dashboard_uid='xxxxxxx', exclude_panels=('row', 'text')
```

## Important notes and features
- **get_dashboard_panels**: Supports only datasources type influxdb
- **get_dashboard_panels**:If the datasource is None, it sets the default
- **get_dashboard_panels**: If the datasource is a variable, maps the selected value of the variable
- **get_dashboard_panels**:If a query has subqueries or has several measurements, it takes them all

## Upcoming developments and features
- **get_dashboard_panels**: Add more types of datasources
- **get_dashboard_panels**: Add logic to work with mixed datasource types
