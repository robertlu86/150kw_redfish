from flask_restx import Namespace, Resource

TelemetryService_ns = Namespace('', description='Telemetry Collection')

TelemetryService_data = {
    "@odata.id": "/redfish/v1/TelemetryService",
    "@odata.type": "#TelemetryService.v1_0_0.TelemetryService",
    "@odata.context": "/redfish/v1/$metadata#TelemetryService.v1_0_0.TelemetryService",
    
    "Id": "TelemetryService",
    "Name": "CDU Telemetry Service",
    "Description": "Telemetry Service",
    # 5013 profile新增 v1.0.0
    "MetricDefinitions": {
        "@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions"
    },
    "MetricReportDefinitions": {
        "@odata.id": "/redfish/v1/TelemetryService/MetricReportDefinitions"
    },
    "Triggers": {
        "@odata.id": "/redfish/v1/TelemetryService/Triggers"
    },
    "Oem": {}
}

TelemetryService__MetricReports_data = {
    "@odata.id": "/redfish/v1/TelemetryService/MetricReports",
    "Name": "CDU Metric Reports Collection",
    "Members@odata.count": 3,
    "Members": [
        {"@odata.id": "/redfish/v1/TelemetryService/MetricReports/1"},
        {"@odata.id": "/redfish/v1/TelemetryService/MetricReports/2"},
        {"@odata.id": "/redfish/v1/TelemetryService/MetricReports/3"},
    ],
}

MetricReports_example_data = {
    "@odata.id": "/redfish/v1/TelemetryService/MetricReports/1",
    "Id": "CDU_Report_001",
    "Name": "CDU Report at 2025-03-31T08:00:00Z",
    "Timestamp": "2025-03-31T08:00:00Z",
    "MetricValues": [
        
    ],
}

expample_data = {
    "temp_clntSply": 0.0,
    "temp_clntSplySpare": 0.0,
    "temp_clntRtn": 0.0,
    "temp_clntRtnSpare": 0.0,
    "space": 0.0,
    "prsr_clntSply": -0.25,
    "prsr_clntSplySpare": -250.0,
    "prsr_clntRtn": -250.0,
    "prsr_clntRtnSpare": -250.0,
    "prsr_fltIn": -250.0,
    "prsr_fltOut": -250.0,
    "clnt_flow": -412500.0,
    "ambient_temp": 1000.0,
    "relative_humid": 2000.0,
    "dew_point": 0.0,
    "pH": 4000.0,
    "cdct": 8000.0,
    "tbd": 9600.0,
    "power": 7.0,
    "AC": 8.0,
    "inv1_freq": 1.5793999433517456,
    "inv2_freq": 0.0,
    "inv3_freq": 1.9121999740600586,
    "heat_capacity": 0.0,
    "fan_freq1": 12.0,
    "fan_freq2": 13.0,
    "fan_freq3": 14.0,
    "fan_freq4": 15.0,
    "fan_freq5": 16.0,
    "fan_freq6": 17.0,
    "fan_freq7": 18.0,
    "fan_freq8": 19.0
}


@TelemetryService_ns.route("/TelemetryService")
class TelemetryService(Resource):
    def get(self):
        return TelemetryService_data


@TelemetryService_ns.route("/TelemetryService/MetricReports")
class TelemetryService_MetricReports(Resource):
    def get(self):
        return TelemetryService__MetricReports_data
    
@TelemetryService_ns.route("/TelemetryService/MetricReports/1")
class MetricReports_1(Resource):
    def get(self):
        for k,v in expample_data.items():
            MetricReports_example_data["MetricValues"].append({
                "MetricId":k,
                "MetricValue":v,
                "Timestamp": "2025-03-31T08:00:00Z"
            })
        return MetricReports_example_data

@TelemetryService_ns.route("/TelemetryService/MetricReports/2")
class MetricReports_2(Resource):
    def get(self):
        for k,v in expample_data.items():
            MetricReports_example_data["MetricValues"].append({
                "MetricId":k,
                "MetricValue":v,
                "Timestamp": "2025-03-31T08:00:00Z"
            })
        return MetricReports_example_data
    
@TelemetryService_ns.route("/TelemetryService/MetricReports/3")
class MetricReports_3(Resource):
    def get(self):
        for k,v in expample_data.items():
            MetricReports_example_data["MetricValues"].append({
                "MetricId":k,
                "MetricValue":v,
                "Timestamp": "2025-03-31T08:00:00Z"
            })
        return MetricReports_example_data    
# 0513新增
METRIC_DEFS = [
    {
      "Id": "Fan_Speed",
      "Name": "fan speed",
      "MetricDataType": True,
      "Units": "RPM",
    }
]
REPORT_DEFS = [
    {
      "Id": "PeriodicReport",
      "Name": "PeriodicReport",
      "MetricReportType": "Periodic",
      "Interval": "PT60S",
      "Metrics": [{"@odata.id": f"/redfish/v1/TelemetryService/MetricDefinitions/{m['Id']}"} for m in METRIC_DEFS]
    }
]
TRIGGERS = [
    {
      "Id": "HighTemp",
      "Name": "HighTemp",
      "Metric": {"@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions/CPU_Temp"},
      "Condition": { "Comparison": "GreaterThan", "Value": 85 }
    }
]

# MetricDefinitions Collection
@TelemetryService_ns.route('/TelemetryService/MetricDefinitions')
class MetricDefinitionCollection(Resource):
    def get(self):
        members = []
        for m in METRIC_DEFS:
            members.append({"@odata.id": f"/redfish/v1/TelemetryService/MetricDefinitions/{m['Id']}"})
        return {
            "@odata.context": "/redfish/v1/$metadata#MetricDefinitionCollection.MetricDefinitionCollection",
            "@odata.id": "/redfish/v1/TelemetryService/MetricDefinitions",
            "@odata.type": "#MetricDefinitionCollection.MetricDefinitionCollection",
            "Name": "Metric Definition Collection",
            "Members@odata.count": len(members),
            "Members": members
        }, 200

# Individual MetricDefinition
@TelemetryService_ns.route('/TelemetryService/MetricDefinitions/<string:metric_id>')
class MetricDefinition(Resource):
    def get(self, metric_id):
        for m in METRIC_DEFS:
            if m['Id'] == metric_id:
                m = m.copy()
                m["@odata.context"] = "/redfish/v1/$metadata#MetricDefinition.MetricDefinition"
                m["@odata.id"] = f"/redfish/v1/TelemetryService/MetricDefinitions/{metric_id}"
                m["@odata.type"] = "#MetricDefinition.v1_0_0.MetricDefinition"
                return m, 200
        return {"error": "Not found"}, 404

# MetricReportDefinitions Collection
@TelemetryService_ns.route('/TelemetryService/MetricReportDefinitions')
class MetricReportDefCollection(Resource):
    def get(self):
        members = [{"@odata.id": f"/redfish/v1/TelemetryService/MetricReportDefinitions/{r['Id']}"} for r in REPORT_DEFS]
        return {
            "@odata.context": "/redfish/v1/$metadata#MetricReportDefinitionCollection.MetricReportDefinitionCollection",
            "@odata.id": "/redfish/v1/TelemetryService/MetricReportDefinitions",
            "@odata.type": "#MetricReportDefinitionCollection.MetricReportDefinitionCollection",
            "Name": "Metric Report Definition Collection",
            "Members@odata.count": len(members),
            "Members": members
        }, 200

# Individual MetricReportDefinition
@TelemetryService_ns.route('/TelemetryService/MetricReportDefinitions/<string:report_id>')
class MetricReportDef(Resource):
    def get(self, report_id):
        for r in REPORT_DEFS:
            if r['Id'] == report_id:
                r = r.copy()
                r["@odata.context"] = "/redfish/v1/$metadata#MetricReportDefinition.MetricReportDefinition"
                r["@odata.id"] = f"/redfish/v1/TelemetryService/MetricReportDefinitions/{report_id}"
                r["@odata.type"] = "#MetricReportDefinition.v1_0_0.MetricReportDefinition"
                return r, 200
        return {"error": "Not found"}, 404

# Triggers Collection
@TelemetryService_ns.route('/TelemetryService/Triggers')
class TriggerCollection(Resource):
    def get(self):
        members = [{"@odata.id": f"/redfish/v1/TelemetryService/Triggers/{t['Id']}"} for t in TRIGGERS]
        return {
            "@odata.context": "/redfish/v1/$metadata#TriggerCollection.TriggerCollection",
            "@odata.id": "/redfish/v1/TelemetryService/Triggers",
            "@odata.type": "#TriggerCollection.TriggerCollection",
            "Name": "Trigger Collection",
            "Members@odata.count": len(members),
            "Members": members
        }, 200

# Individual Trigger
@TelemetryService_ns.route('/TelemetryServiceTriggers/<string:trigger_id>')
class Trigger(Resource):
    def get(self, trigger_id):
        for t in TRIGGERS:
            if t['Id'] == trigger_id:
                t = t.copy()
                t["@odata.context"] = "/redfish/v1/$metadata#Trigger.Trigger"
                t["@odata.id"] = f"/redfish/v1/TelemetryService/Triggers/{trigger_id}"
                t["@odata.type"] = "#Trigger.v1_0_0.Trigger"
                return t, 200
        return {"error": "Not found"}, 404      