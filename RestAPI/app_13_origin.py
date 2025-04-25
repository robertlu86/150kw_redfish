from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields, Namespace

app = Flask(__name__)
api = Api(app, version="0.6.6", title="CDU API", description="API for CDU system")

# Define default namespace
default_ns = Namespace("api/v1", description="api for CDU system")

data = {
    "sensor_value": {
        "temp_coolant_supply": 0,
        "temp_coolant_supply_spare": 0,
        "temp_coolant_return": 0,
        "temp_ambient": 0,
        "relative_humid": 0,
        "dew_point": 0,
        "temp_water_supply": 0,
        "temp_water_return": 0,
        "pressure_coolant_supply": 0,
        "pressure_coolant_supply_spare": 0,
        "pressure_coolant_return": 0,
        "pressure_filter_in": 0,
        "pressure_filter1_out": 0,
        "pressure_filter2_out": 0,
        "pressure_filter3_out": 0,
        "pressure_filter4_out": 0,
        "pressure_filter5_out": 0,
        "pressure_qlt_out": 0,
        "pressure_water_in": 0,
        "pressure_water_out": 0,
        "flow_coolant": 0,
        "flow_water": 0,
        "pH": 0,
        "conductivity": 0,
        "Turbidity": 0,
        "heat_capacity": 0,
        "power_comsume": 0,
    },
    "unit": {
        "temperature": "celcius",
        "pressure": "bar",
        "flow": "LPM",
        "power": "kW",
        "heat_capacity": "kW",
    },
    "pump_speed": {"pump1_speed": 0, "pump2_speed": 0},
    "pump_service_hours": {
        "pump1_service_hours": 172,
        "pump2_service_hours": 169,
    },
    "pump_state": {"pump1_state": "Enable", "pump2_state": "Disable"},
    "pump_health": {"pump1_health": "OK", "pump2_health": "Critical"},
    "filter_service_hours": {
        "filter_service_hours": 300,
    },
    "water_pv": {"water_PV": 0},
    "filter_mode": {
        "all_filter_sw": False,
    },
    "valve": {"EV1": "open", "EV2": "open", "EV3": "close", "EV4": "close"},
}

op_mode = {"mode": "stop"}
pump_speed_set = {"pump1_speed": 0, "pump2_speed": 0}
water_pv_set = {"water_PV": 0}
temp_set = {"temp_set": 0}
pressure_set = {"pressure_set": 0}
pump_swap_time = {"pump_swap_time": 0}
# filter_time_set = {
#     "time_between_filter_cycles": 0,
#     "filter_cycle_duration": 0
# }
# tank_sensor_value = [
#     {
#         "tank_id": "1",
#         "flow": 0,
#         "temp": 0,
#     },

#     {
#         "tank_id": "2",
#         "flow": 0,
#         "temp": 0,
#     },

#     {
#         "tank_id": "3",
#         "flow": 0,
#         "temp": 0,
#     },

#     {
#         "tank_id": "4",
#         "flow": 0,
#         "temp": 0,
#     }
# ]

# tank_io_status=[
#     {
#         "tank_id": "1",
#         "oil_level": "Normal",
#         "waste_oil_level": "Normal",
#         "door": "Close",
#         "LED_color": "red"
#     },

#     {
#         "tank_id": "2",
#         "oil_level": "Normal",
#         "waste_oil_level": "Normal",
#         "door": "Close",
#         "LED_color": "green"
#     },

#     {
#         "tank_id": "3",
#         "oil_level": "Normal",
#         "waste_oil_level": "Normal",
#         "door": "Close",
#         "LED_color": "blue"
#     },

#     {
#         "tank_id": "4",
#         "oil_level": "Normal",
#         "waste_oil_level": "Normal",
#         "door": "Close",
#         "LED_color": "white"
#     }
# ]

unit_set = {"unit": "Metric"}

all_filter_mode_set = {"all_filter_mode_set": False}

messages = {
    "M100": "Coolant Supply Temperature Over Range Warning",
    "M101": "Coolant Supply Temperature Spare Over Range Warning",
    "M102": "Coolant Return Temperature Over Range Warning",
    "M103": "Ambient Temperature Over Range Warning",
    "M104": "Condensation Warning",
    "M105": "Relative Humidity Over Range Warning",
    "M106": "Facility Water Inlet Temperature Over Range Warning",
    "M107": "Facility Water Outlet Temperature Over Range Warning",
    "M108": "Coolant Supply Pressure Over Range Warning",
    "M109": "Coolant Supply Pressure Spare Over Range Warning",
    "M110": "Coolant Return Pressure Spare Over Range Warning",
    "M111": "Filter Inlet Pressure Over Range Warning",
    "M112": "Filter1 Outlet Pressure Over Range Warning",
    "M113": "Filter2 Outlet Pressure Over Range Warning",
    "M114": "Filter3 Outlet Pressure Over Range Warning",
    "M115": "Filter4 Outlet Pressure Over Range Warning",
    "M116": "Filter5 Outlet Pressure Over Range Warning",
    "M117": "Collant Quality Meter Outlet Pressure Over Range Warning",
    "M118": "Facility Water Inlet Temperature Over Range Warning",
    "M119": "Facility Water Outlet Temperature Over Range Warning",
    "M120": "Coolant Flow Low Warning",
    "M121": "Facility Water Flow Low Warning",
    "M122": "pH Value Over Range Warning",
    "M123": "Conductivity Over Range Warning",
    "M124": "Turbidity Over Range Warning",
    "M200": "Coolant Supply Temperature Over Range Alert",
    "M201": "Coolant Supply Temperature Spare Over Range Alert",
    "M202": "Coolant Return Temperature Over Range Alert",
    "M203": "Ambient Temperature Over Range Alert",
    "M204": "Condensation Alert",
    "M205": "Relative Humidity Over Range Alert",
    "M206": "Facility Water Inlet Temperature Over Range Alert",
    "M207": "Facility Water Outlet Temperature Over Range Alert",
    "M208": "Coolant Supply Pressure Over Range Alert",
    "M209": "Coolant Supply Pressure Spare Over Range Alert",
    "M210": "Coolant Return Pressure Spare Over Range Alert",
    "M211": "Filter Inlet Pressure Over Range Alert",
    "M212": "Filter1 Outlet Pressure Over Range Alert",
    "M213": "Filter2 Outlet Pressure Over Range Alert",
    "M214": "Filter3 Outlet Pressure Over Range Alert",
    "M215": "Filter4 Outlet Pressure Over Range Alert",
    "M216": "Filter5 Outlet Pressure Over Range Alert",
    "M217": "Collant Quality Meter Outlet Pressure Over Range Alert",
    "M218": "Facility Water Inlet Temperature Over Range Alert",
    "M219": "Facility Water Outlet Temperature Over Range Alert",
    "M220": "Coolant Flow Low Alert",
    "M221": "Facility Water Flow Low Alert",
    "M222": "pH Value Over Range Alert",
    "M223": "Conductivity Over Range Alert",
    "M224": "Turbidity Over Range Alert",
    "M300": "Facility Water Proportional Valve Disconnection",
    "M301": "Coolant Pump1 Valve BV1 Error",
    "M302": "Coolant Pump1 Valve BV2 Error",
    "M303": "Coolant Pump2 Valve BV3 Error",
    "M304": "Coolant Pump2 Valve BV4 Error",
    "M305": "Coolant Pump1 Inverter Overload",
    "M306": "Coolant Pump2 Inverter Overload",
    "M307": "Coolant Pump1 Inverter Error",
    "M308": "Coolant Pump2 Inverter Error",
    "M309": "Internal Leakage",
    "M310": "Internal Leakage Sensor Broken",
    "M311": "External Leakage",
    "M312": "External Leakage Sensor Broken",
    "M312": "PLC Communication Broken",
}
# Define models for Swagger documentation
op_mode_model = default_ns.model(
    "OpMode",
    {
        "mode": fields.String(
            required=True,
            description="The operational mode",
            example="stop",
            enum=["stop", "manual", "auto"],
        )
    },
)

pump_speed_model = default_ns.model(
    "PumpSpeed",
    {
        "pump1_speed": fields.Integer(
            description="Speed of pump 1", example=50, min=0, max=100
        ),
        "pump2_speed": fields.Integer(
            description="Speed of pump 2", example=50, min=0, max=100
        ),
    },
)

water_pv_model = default_ns.model(
    "WaterPV",
    {
        "water_PV": fields.Integer(
            description="Water proportional valve position", example=50, min=0, max=100
        )
    },
)

temp_set_model = default_ns.model(
    "TempSet",
    {
        "temp_set": fields.Integer(
            required=True,
            description="The temperature setting 35-55 deg celcius",
            example=40,
            min=35,
            max=55,
        )
    },
)

pressure_set_model = default_ns.model(
    "PressureSet",
    {
        "pressure_set": fields.Integer(
            required=True, description="The pressure setting", example=1.2, min=0, max=2
        )
    },
)

pump_swap_time_model = default_ns.model(
    "PumpSwapTime",
    {
        "pump_swap_time": fields.Integer(
            description="Time interval for pump swapping in minutes",
            example=60,
            min=0,
            max=30000,
        )
    },
)

# filter_time_set_model = default_ns.model('FilterTimeSet', {
#     'time_between_filter_cycles': fields.Integer(description='Time between filter cycles in minutes',example=60, min=0, max=30000),
#     'filter_cycle_duration': fields.Integer(description='Duration of filter cycle in minutes',example=60, min=0, max=30000)
# })

unit_set_model = default_ns.model(
    "UnitSet",
    {
        "unit_set": fields.String(
            required=True,
            description="The unit setting",
            example="metric",
            enum=["metric", "imperial"],
        )
    },
)

unit_model = default_ns.model(
    "Unit",
    {
        "temperature": fields.String(
            description="Temperature unit",
            example="celcius",
            enum=["celcius", "fehrenheit"],
        ),
        "pressure": fields.String(
            description="Pressure unit", example="bar", enum=["bar", "psi"]
        ),
        "flow": fields.String(
            description="Flow unit", example="LPM", enum=["LPM", "GPM"]
        ),
        "power": fields.String(description="Power unit", example="kW"),
        "heat_capacity": fields.String(description="Heat capacity unit", example="kW"),
    },
)

# all_filter_mode_set_model = default_ns.model('AllFilterModeSet', {
#     'all_filter_mode_set': fields.Boolean(description='Status of all filter mode', example=True)
# })

valve_model = default_ns.model(
    "ValveStatus",
    {
        "EV1": fields.Boolean(description="Status of BV1 valve", example=True),
        "EV2": fields.Boolean(description="Status of BV2 valve", example=False),
        "EV3": fields.Boolean(description="Status of BV3 valve", example=True),
        "EV4": fields.Boolean(description="Status of BV4 valve", example=True),
    },
)

message_model = default_ns.model(
    "ErrorMessages",
    {
        "error_code": fields.String(description="Error code"),
        "message": fields.String(description="Error message"),
    },
)

pump_service_hour_model = default_ns.model(
    "pump_service_hour_model",
    {
        "pump1_service_hour": fields.Integer(
            description="Pump1 Service Time in hours", example=171
        ),
        "pump2_service_hour": fields.Integer(
            description="Pump2 Service Time in hours", example=169
        ),
    },
)

pump_state_model = default_ns.model(
    "pump_state",
    {
        "pump1_state": fields.Integer(description="Pump1 State", example="Enable"),
        "pump2_state": fields.Integer(description="Pump2 State", example="Disable"),
    },
)

pump_health_model = default_ns.model(
    "pump_health",
    {
        "pump1_health": fields.Integer(description="Pump1 State", example="OK"),
        "pump2_health": fields.Integer(description="Pump2 State", example="Critical"),
    },
)

filter_service_hour_model = default_ns.model(
    "filter_service_hour_model",
    {
        "filter_service_hour": fields.Integer(
            description="Filter service time in hours", example=300
        )
    },
)


@default_ns.route("/1.3MW/cdu/status/op_mode")
class CduOpMode(Resource):
    @default_ns.doc("get_op_mode")
    def get(self):
        """Get the current operational mode stop, auto, or manual"""
        return op_mode["mode"]

    @default_ns.expect(op_mode_model)
    @default_ns.doc("set_op_mode")
    def patch(self):
        """Set the operational mode auto, stop, or manual"""
        new_mode = api.payload["mode"]
        if new_mode in ["auto", "stop", "manual"]:
            op_mode["mode"] = new_mode
            return {
                "message": "op_mode updated successfully",
                "new_mode": op_mode["mode"],
            }, 200
        else:
            return {
                "message": "Invalid mode. Allowed values are 'auto', 'stop', 'manual'."
            }, 400


@default_ns.route("/1.3MW/cdu/status/sensor_value")
class CduSensorValue(Resource):
    @default_ns.doc("get_sensor_value")
    def get(self):
        """Get the current sensor values of CDU"""
        return data["sensor_value"]


@default_ns.route("/1.3MW/cdu/control/pump_speed")
class PumpSpeed(Resource):
    @default_ns.doc("get_pump_speed")
    def get(self):
        """Get the current pump speeds"""
        return pump_speed_set

    @default_ns.expect(pump_speed_model)
    @default_ns.doc("update_pump_speed")
    def patch(self):
        """Update the pump speeds in percentage(0-100) in manual mode"""
        updated_data = api.payload
        for key in updated_data:
            if key in pump_speed_set and 0 <= updated_data[key] <= 100:
                pump_speed_set[key] = updated_data[key]
            else:
                return {
                    "message": f"Invalid value for {key}. Must be between 0 and 100."
                }, 400
        return {
            "message": "Pump speed updated successfully",
            "pump_speed": pump_speed_set,
        }, 200


@default_ns.route("/1.3MW/cdu/control/water_pv")
class WaterPV(Resource):
    @default_ns.doc("get_water_pv")
    def get(self):
        """Get the opening of water proportional valve in percentage"""
        return water_pv_set

    @default_ns.expect(water_pv_model)
    @default_ns.doc("update_water_pv")
    def patch(self):
        """Update the opening of water proportional valve in percentage(0-100) in manual mode"""
        new_position = api.payload["water_PV"]
        if 0 <= new_position <= 100:
            water_pv_set["water_PV"] = new_position
            return {
                "message": "Water proportional valve position updated successfully",
                "new_position": water_pv_set["water_PV"],
            }, 200
        else:
            return {"message": "Invalid position. Must be between 0 and 100."}, 400


@default_ns.route("/1.3MW/cdu/control/temp_set")
class TempSet(Resource):
    @api.doc("get_temp_set")
    def get(self):
        """Get the current temperature setting"""
        return temp_set["temp_set"]

    @default_ns.expect(temp_set_model)
    @default_ns.doc("patch_temp_set")
    def patch(self):
        """Update the temperature setting in 35-55 deg celcius"""
        new_temp = api.payload["temp_set"]
        if 35 <= new_temp <= 55:
            temp_set["temp_set"] = new_temp
            return {
                "message": "temp_set updated successfully",
                "new_temp_set": temp_set["temp_set"],
            }, 200
        else:
            return {
                "message": "Invalid temperature. Temperature must be between 35 and 55."
            }, 400


@default_ns.route("/1.3MW/cdu/control/pressure_set")
class PressureSet(Resource):
    @default_ns.doc("get_pressure_set")
    def get(self):
        """Get the current pressure setting"""
        return pressure_set["pressure_set"]

    @default_ns.expect(pressure_set_model)
    @default_ns.doc("patch_pressure_set")
    def patch(self):
        """Update the pressure setting in 0-2 bar"""
        new_pressure = api.payload["pressure_set"]
        if 0 <= new_pressure <= 2:
            pressure_set["pressure_set"] = new_pressure
            return {
                "message": "pressure_set updated successfully",
                "new_pressure_set": pressure_set["pressure_set"],
            }, 200
        else:
            return {
                "message": "Invalid pressure. Pressure must be between 0 and 100."
            }, 400


@default_ns.route("/1.3MW/cdu/control/pump_swap_time")
class PumpSwapTime(Resource):
    @default_ns.doc("get_pump_swap_time")
    def get(self):
        """Get the time interval for pump swapping in minutes"""
        return pump_swap_time

    @default_ns.expect(pump_swap_time_model)
    @default_ns.doc("update_pump_swap_time")
    def patch(self):
        """Update the time interval for pump swapping in minutes"""
        new_time = api.payload["pump_swap_time"]
        if 0 <= new_time <= 30000:
            pump_swap_time["pump_swap_time"] = new_time
            return {
                "message": "Pump swap time updated successfully",
                "new_pump_swap_time": pump_swap_time["pump_swap_time"],
            }, 200
        else:
            return {
                "message": "Invalid value. Time interval must be between 0 and 30000."
            }, 400


# @default_ns.route('/1.3MW/cdu/control/filter_time_set')
# class FilterTimeSet(Resource):
#     @default_ns.doc('get_filter_time_set')
#     def get(self):
#         """Get the time settings for filter cycles in minutes"""
#         return filter_time_set

#     @default_ns.expect(filter_time_set_model)
#     @default_ns.doc('update_filter_time_set')
#     def patch(self):
#         """Update the time settings for filter cycles in minutes"""
#         updated_data = api.payload
#         for key in updated_data:
#             if 0 <= updated_data[key] <= 30000:
#                 filter_time_set[key] = updated_data[key]
#             else:
#                 return {"message": f"Invalid value for {key}. Time must be between 0 and 30000."}, 400
#         return {"message": "Filter time settings updated successfully", "filter_time_set": filter_time_set}, 200

# @default_ns.route('/1.3MW/tank/status/sensor_value')
# class TankSensorValue(Resource):
#     @default_ns.doc('get_tank_sensor_value')
#     def get(self):
#         """Get the current sensor values of Tanks"""
#         return tank_sensor_value

# @default_ns.route('/1.3MW/tank/status/io_status')
# class TankIOStatus(Resource):
#     @default_ns.doc('get_tank_io_status')
#     def get(self):
#         """Get the current status of Tanks"""
#         return tank_io_status


@default_ns.route("/1.3MW/cdu/status/pump_speed")
class TankIOStatus(Resource):
    @default_ns.doc("get_pump_status")
    def get(self):
        """Get speed of pumps"""
        return data["pump_speed"]


@default_ns.route("/1.3MW/cdu/status/pump_service_hours")
class pump_Service_hours(Resource):
    @default_ns.doc("get_pump_service_hours")
    def get(self):
        """Get service hours of pumps"""
        return data["pump_service_hours"]


@default_ns.route("/1.3MW/cdu/status/pump_state")
class pump_state(Resource):
    @default_ns.doc("get_pump_state")
    def get(self):
        """Get state of pumps"""
        return data["pump_state"]


@default_ns.route("/1.3MW/cdu/status/pump_health")
class pump_state(Resource):
    @default_ns.doc("get_pump_health")
    def get(self):
        """Get health of pumps"""
        return data["pump_health"]


@default_ns.route("/1.3MW/cdu/status/filter_Service_hours")
class filter_Service_hours(Resource):
    @default_ns.doc("get_filter_Service_hours")
    def get(self):
        """Get service hours of filters"""
        return data["filter_service_hours"]


@default_ns.route("/1.3MW/cdu/status/water_pv")
class TankIOStatus(Resource):
    @default_ns.doc("get_water_pv_status")
    def get(self):
        """Get opening of water proportional valve"""
        return data["water_pv"]


@default_ns.route("/1.3MW/unit_set")
class Unit(Resource):
    @default_ns.doc("get_unit_set")
    def get(self):
        """Get the current unit setting"""
        return unit_set

    @default_ns.expect(unit_set_model)
    @default_ns.doc("update_unit_set")
    def patch(self):
        """Update the unit setting to metric or imperial"""
        new_unit = api.payload["unit_set"]
        if new_unit.lower() in ["metric", "imperial"]:
            unit_set["unit"] = new_unit
            return {
                "message": "Unit updated successfully",
                "new_unit": unit_set["unit"],
            }, 200
        else:
            return {
                "message": "Invalid unit. Unit must be 'metric' or 'imperial'."
            }, 400


# @default_ns.route('/1.3MW/cdu/control/all_filter_mode_set')
# class AllFilterModeSet(Resource):
#     @default_ns.doc('get_all_filter_mode_set')
#     def get(self):
#         """Get the current status of the all filter mode"""
#         return all_filter_mode_set

#     @default_ns.expect(all_filter_mode_set_model)
#     @default_ns.doc('update_all_filter_mode_set')
#     def patch(self):
#         """Update the status of the all filter mode"""
#         new_status = api.payload['all_filter_mode_set']
#         if isinstance(new_status, bool):
#             all_filter_mode_set['all_filter_mode_set'] = new_status
#             return {"message": "All filter mode updated successfully", "new_all_filter_mode_set": all_filter_mode_set['all_filter_mode_set']}, 200
#         else:
#             return {"message": "Invalid value. Must be true or false."}, 400


@default_ns.route("/1.3MW/cdu/status/valve")
class ValveStatus(Resource):
    @default_ns.doc("get_valve_status")
    def get(self):
        """Get the status of electric valves"""
        return data["valve"]


@default_ns.route("/1.3MW/error_messages")
class ErrorMessages(Resource):
    @default_ns.doc("get_error_messages")
    @default_ns.marshal_with(message_model)
    def get(self):
        """Get the list of error messages happening in the system"""
        error_messages = [
            {"error_code": code, "message": message}
            for code, message in messages.items()
        ]
        return error_messages


@default_ns.route("/1.3MW/unit")
class Unit(Resource):
    # @default_ns.doc('get_unit')
    @default_ns.marshal_with(unit_model)
    def get(self):
        """Get the unit information"""
        return data["unit"]


# Add namespace to API
api.add_namespace(default_ns)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5002)
