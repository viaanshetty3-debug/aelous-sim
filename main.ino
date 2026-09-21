// ============================================================
// AEOLUS ARDUINO CONTROL FIRMWARE
// Target: Arduino Mega 2560 (Tabletop Vortex Chamber Prototype)
// Reference: HARDWARE_PLAN.md
// ============================================================

#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_BME680.h>

// ------------------------------------------------------------
// PIN CONFIGURATION
// ------------------------------------------------------------
// PWM Outputs
#define PIN_EXHAUST_FAN        3    // ~PWM: Main vortex fan
#define PIN_VACUUM_MOTOR       5    // ~PWM: Suction pressure
#define PIN_THERMAL_HEATER_1   6    // ~PWM: Heater bank 1
#define PIN_THERMAL_HEATER_2   9    // ~PWM: Heater bank 2
#define PIN_CIRCULATION_BLOWER 10   // ~PWM: Thermal circulation
#define PIN_MIST_PUMP          11   // ~PWM: Water circulation

// Digital Outputs (On/Off)
#define PIN_RELAY_MAIN         22   // Main power relay
#define PIN_RELAY_HEATER       23   // Heater array relay
#define PIN_RELAY_VACUUM       24   // Vacuum motor relay
#define PIN_BUZZER             25   // Alarm output
#define PIN_LED_R              26   // Red status
#define PIN_LED_G              27   // Green status
#define PIN_LED_B              28   // Blue status

// Digital Inputs
#define PIN_BTN_START          30   // Start button
#define PIN_BTN_STOP           31   // Stop button
#define PIN_BTN_ADJUST_UP      32   // Parameter up
#define PIN_BTN_ADJUST_DOWN    33   // Parameter down
#define PIN_THERMAL_CUTOFF     34   // Safety thermal switch (active low)
#define PIN_PRESSURE_ALARM     35   // Pressure too low alarm
#define PIN_TACH_EXHAUST       36   // Exhaust fan tachometer
#define PIN_TACH_VACUUM        37   // Vacuum motor tachometer

// Analog Inputs
#define PIN_PRESSURE_RAW       A0   // Raw pressure
#define PIN_TEMP_CHAMBER       A1   // Chamber temperature
#define PIN_VOLTAGE_MONITOR    A2   // 12V rail voltage
#define PIN_CURRENT_FAN        A3   // Exhaust current monitor
#define PIN_CURRENT_HEATER     A4   // Heater current monitor

// Buses
#define PIN_ONEWIRE            38   // DS18B20 1-Wire bus
#define I2C_PRESSURE_BME680    0x77
#define I2C_LCD                0x27

// ------------------------------------------------------------
// CONSTANTS & TIMINGS
// ------------------------------------------------------------
const int INTERVENTION_DURATION = 30000;   // 30 seconds (ms)
const int POST_DECAY_DURATION   = 40000;   // 40 seconds (ms)
const int TARGET_THERMAL_ANOMALY = 3;      // +3K
const int TARGET_VACUUM_PRESSURE = -250;   // Pa
const float VORTICITY_REDUCTION_TARGET = 117.30; // %

// ------------------------------------------------------------
// STATE MACHINE & GLOBALS
// ------------------------------------------------------------
enum SystemState {
  IDLE,
  INITIALIZATION,
  PRE_VORTEX,
  INTERVENTION,
  POST_DECAY,
  COOL_DOWN,
  SHUTDOWN
};

SystemState currentState = IDLE;
unsigned long stateEnterTime = 0;
int pressureAlarmCounter = 0;
bool simulationRunning = false;

// Sensor Readings
float chamberTemperature = 0.0;
float heaterTemperature[5] = {0.0};
int vacuumPressure = 0;
int exhaustFanRPM = 0;
int vacuumMotorRPM = 0;
float vortexReduction = 0.0;

// Device Instances
LiquidCrystal_I2C lcd(I2C_LCD, 20, 4);
OneWire oneWire(PIN_ONEWIRE);
DallasTemperature sensors(&oneWire);
Adafruit_BME680 bme;

// ------------------------------------------------------------
// FUNCTION PROTOTYPES
// ------------------------------------------------------------
void updateSensorReadings();
void checkSafetyLimits();
void updateStateLogic();
void updateVorticityReduction();
void allSystemsOff();
void transitionTo(SystemState newState);
void setRGB(int r, int g, int b);
void alarmCondition(const char* message);

// ------------------------------------------------------------
// SETUP
// ------------------------------------------------------------
void setup() {
  Serial.begin(115200);

  pinMode(PIN_EXHAUST_FAN, OUTPUT);
  pinMode(PIN_VACUUM_MOTOR, OUTPUT);
  pinMode(PIN_THERMAL_HEATER_1, OUTPUT);
  pinMode(PIN_THERMAL_HEATER_2, OUTPUT);
  pinMode(PIN_CIRCULATION_BLOWER, OUTPUT);
  pinMode(PIN_MIST_PUMP, OUTPUT);
  pinMode(PIN_RELAY_MAIN, OUTPUT);
  pinMode(PIN_RELAY_HEATER, OUTPUT);
  pinMode(PIN_RELAY_VACUUM, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_LED_R, OUTPUT);
  pinMode(PIN_LED_G, OUTPUT);
  pinMode(PIN_LED_B, OUTPUT);

  pinMode(PIN_BTN_START, INPUT_PULLUP);
  pinMode(PIN_BTN_STOP, INPUT_PULLUP);
  pinMode(PIN_THERMAL_CUTOFF, INPUT_PULLUP);

  Wire.begin();
  lcd.init();
  lcd.backlight();

  sensors.begin();
  bme.begin(I2C_PRESSURE_BME680);

  allSystemsOff();
  transitionTo(IDLE);
}

// ------------------------------------------------------------
// MAIN LOOP
// ------------------------------------------------------------
void loop() {
  updateSensorReadings();
  checkSafetyLimits();
  updateStateLogic();
  delay(10);
}

void updateStateLogic() {
  unsigned long timeInState = millis() - stateEnterTime;

  switch (currentState) {
    case IDLE:
      setRGB(0, 255, 0);  // Green
      lcd.setCursor(0, 0);
      lcd.print("Ready. Press START  ");
      if (!digitalRead(PIN_BTN_START)) {
        delay(50);
        if (!digitalRead(PIN_BTN_START)) {
          transitionTo(INITIALIZATION);
        }
      }
      break;

    case INITIALIZATION:
      setRGB(100, 100, 255);
      lcd.setCursor(0, 0);
      lcd.print("Initializing...     ");
      if (timeInState < 2000) {
        if (chamberTemperature > 50) {
          alarmCondition("CHAMBER TOO HOT");
          transitionTo(IDLE);
          break;
        }
        analogWrite(PIN_EXHAUST_FAN, 51);  // 20%
        analogWrite(PIN_VACUUM_MOTOR, 25);
      } else {
        transitionTo(PRE_VORTEX);
      }
      break;

    case PRE_VORTEX:
      setRGB(50, 200, 255);
      lcd.setCursor(0, 0);
      lcd.print("Building vortex...  ");
      if (timeInState < 10000) {
        float ramp = (float)timeInState / 10000.0;
        analogWrite(PIN_EXHAUST_FAN, (int)(192 * ramp)); // Ramp to 75%
        analogWrite(PIN_VACUUM_MOTOR, (int)(50 + 25 * ramp));
      } else {
        transitionTo(INTERVENTION);
      }
      break;

    case INTERVENTION:
      setRGB(255, 255, 0);  // Yellow
      lcd.setCursor(0, 0);
      lcd.print("INTERVENTION ACTIVE ");

      if (timeInState < INTERVENTION_DURATION) {
        // 1. Thermal ramp (0-5s) then hold
        float thermalRamp = (timeInState < 5000) ? ((float)timeInState / 5000.0) : 1.0;
        int thermalDuty = (int)(255 * thermalRamp);
        analogWrite(PIN_THERMAL_HEATER_1, thermalDuty);
        analogWrite(PIN_THERMAL_HEATER_2, thermalDuty);

        // 2. Vacuum ramp (0-5s) to -250 Pa
        float vacuumRamp = (timeInState < 5000) ? ((float)timeInState / 5000.0) : 1.0;
        analogWrite(PIN_VACUUM_MOTOR, (int)(150 * vacuumRamp));

        // 3. Steady exhaust
        analogWrite(PIN_EXHAUST_FAN, 192);

        // 4. Decay phase (last 5s)
        if (timeInState > 25000) {
          setRGB(255, 165, 0);  // Orange
          float decay = (float)(timeInState - 25000) / 5000.0;
          analogWrite(PIN_THERMAL_HEATER_1, (int)(255 * (1.0 - 0.7 * decay)));
          analogWrite(PIN_THERMAL_HEATER_2, (int)(255 * (1.0 - 0.7 * decay)));
          analogWrite(PIN_VACUUM_MOTOR, (int)(150 * (1.0 - 0.4 * decay)));
        }

        updateVorticityReduction();
      } else {
        transitionTo(POST_DECAY);
      }
      break;

    case POST_DECAY:
      setRGB(255, 100, 0);
      lcd.setCursor(0, 0);
      lcd.print("Post-decay phase    ");
      if (timeInState < POST_DECAY_DURATION) {
        analogWrite(PIN_THERMAL_HEATER_1, 76); // 30% hold
        analogWrite(PIN_THERMAL_HEATER_2, 76);
        analogWrite(PIN_VACUUM_MOTOR, 90);

        float exhaustRamp = 1.0 - (0.25 * (float)timeInState / POST_DECAY_DURATION);
        analogWrite(PIN_EXHAUST_FAN, (int)(192 * exhaustRamp));
        updateVorticityReduction();
      } else {
        transitionTo(COOL_DOWN);
      }
      break;

    case COOL_DOWN:
      setRGB(255, 0, 0);
      lcd.setCursor(0, 0);
      lcd.print("Cooling down...     ");
      if (timeInState < 30000) {
        float coolRamp = 1.0 - ((float)timeInState / 30000.0);
        analogWrite(PIN_THERMAL_HEATER_1, (int)(76 * coolRamp));
        analogWrite(PIN_THERMAL_HEATER_2, (int)(76 * coolRamp));
        analogWrite(PIN_EXHAUST_FAN, (int)(128 * coolRamp));
        analogWrite(PIN_VACUUM_MOTOR, 0);
      } else {
        transitionTo(SHUTDOWN);
      }
      break;

    case SHUTDOWN:
      setRGB(255, 0, 0);
      allSystemsOff();
      lcd.setCursor(0, 0);
      lcd.print("Test Complete. STOP ");
      if (!digitalRead(PIN_BTN_STOP)) {
        delay(50);
        if (!digitalRead(PIN_BTN_STOP)) {
          transitionTo(IDLE);
        }
      }
      break;
  }
}

// ------------------------------------------------------------
// SENSORS & SAFETY HELPERS
// ------------------------------------------------------------
void updateSensorReadings() {
  sensors.requestTemperatures();
  chamberTemperature = sensors.getTempCByIndex(0);
  for (int i = 0; i < 5; i++) {
    heaterTemperature[i] = sensors.getTempCByIndex(i + 1);
  }

  if (bme.performReading()) {
    static float baselinePressure = 0;
    if (currentState == IDLE || baselinePressure == 0) {
      baselinePressure = bme.pressure / 100.0;
    }
    vacuumPressure = (int)(-(bme.pressure / 100.0 - baselinePressure) * 100);
  }
}

void updateVorticityReduction() {
  vortexReduction = 100.0;
  if (vacuumPressure < -100) {
    vortexReduction += 25.0 * ((float)(vacuumPressure - (-100)) / (-250 - (-100)));
  }
  if (heaterTemperature[0] > 30) {
    vortexReduction += 20.0 * ((heaterTemperature[0] - 25.0) / 10.0);
  }
}

void checkSafetyLimits() {
  if (digitalRead(PIN_THERMAL_CUTOFF) == LOW || chamberTemperature > 80) {
    alarmCondition("OVER-TEMPERATURE");
    allSystemsOff();
    transitionTo(SHUTDOWN);
  }
}

void allSystemsOff() {
  analogWrite(PIN_EXHAUST_FAN, 0);
  analogWrite(PIN_VACUUM_MOTOR, 0);
  analogWrite(PIN_THERMAL_HEATER_1, 0);
  analogWrite(PIN_THERMAL_HEATER_2, 0);
  analogWrite(PIN_CIRCULATION_BLOWER, 0);
  analogWrite(PIN_MIST_PUMP, 0);
  digitalWrite(PIN_RELAY_MAIN, LOW);
  digitalWrite(PIN_RELAY_HEATER, LOW);
  digitalWrite(PIN_RELAY_VACUUM, LOW);
}

void transitionTo(SystemState newState) {
  currentState = newState;
  stateEnterTime = millis();
}

void setRGB(int r, int g, int b) {
  analogWrite(PIN_LED_R, r);
  analogWrite(PIN_LED_G, g);
  analogWrite(PIN_LED_B, b);
}

void alarmCondition(const char* message) {
  setRGB(255, 0, 0);
  digitalWrite(PIN_BUZZER, HIGH);
  delay(150);
  digitalWrite(PIN_BUZZER, LOW);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("ALARM:");
  lcd.setCursor(0, 1);
  lcd.print(message);
}
