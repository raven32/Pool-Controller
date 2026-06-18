import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.const import CONF_ID
from esphome.components import uart
from esphome import pins
from esphome.const import CONF_FLOW_CONTROL_PIN

MULTI_CONF = True
DEPENDENCIES = ["uart"]
CODEOWNERS = ["@wolfson292"]

pentair_if_ic_ns = cg.esphome_ns.namespace("pentair_if_ic")
PentairIfIcComponent = pentair_if_ic_ns.class_(
    "PentairIfIcComponent", cg.PollingComponent, uart.UARTDevice
)
PentairDeviceMode = pentair_if_ic_ns.enum("PentairDeviceMode")

DEVICE_MODES = {
    "pump_only": PentairDeviceMode.DEVICE_MODE_PUMP_ONLY,
    "chlorinator_only": PentairDeviceMode.DEVICE_MODE_CHLORINATOR_ONLY,
    "pump_and_chlorinator": PentairDeviceMode.DEVICE_MODE_PUMP_AND_CHLORINATOR,
}

CONF_PENTAIR_IF_IC_ID = "pentair_if_ic_id"
CONF_DEVICE_MODE = "device_mode"
CONF_USE_SAE_UNITS = "use_sae_units"

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(): cv.declare_id(PentairIfIcComponent),
        cv.Optional(CONF_FLOW_CONTROL_PIN): pins.gpio_output_pin_schema,
        cv.Optional(CONF_DEVICE_MODE, default="pump_and_chlorinator"): cv.enum(
            DEVICE_MODES, lower=True
        ),
        # Backward-compatible unit selector for the legacy flow/pressure sensors.
        # Preferred new YAML is to call flow_gpm / pressure_psi directly.
        cv.Optional(CONF_USE_SAE_UNITS, default=False): cv.boolean,
    }
).extend(uart.UART_DEVICE_SCHEMA).extend(cv.polling_component_schema("30s"))

FINAL_VALIDATE_SCHEMA = uart.final_validate_device_schema(
    "pentair_if_ic",
    require_tx=True,
    require_rx=True,
    baud_rate=9600,
    parity="NONE",
    stop_bits=1,
)

async def to_code(config):
    from esphome.cpp_helpers import gpio_pin_expression

    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_device_mode(config[CONF_DEVICE_MODE]))
    cg.add(var.set_use_sae_units(config[CONF_USE_SAE_UNITS]))

    if CONF_FLOW_CONTROL_PIN in config:
        pin = await gpio_pin_expression(config[CONF_FLOW_CONTROL_PIN])
        cg.add(var.set_flow_control_pin(pin))
