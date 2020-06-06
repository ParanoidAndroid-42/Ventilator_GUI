#include <Wire.h>
#include <math.h>

#define e 2.718281828459


/* Arduino Registers
 *  
 * Register 0 - R
 * Register 1 - Vt
 * Register 2 - BPM
 * Register 3 - I_Ratio
 * Register 4 - E_Ratio
 * Register 5 - PEEP
 * 
 * Register 6 - Send volume when requested
 * Register 7 - Send flow when requested
 * Register 8 - Send pressure when requested
 * 
 * Register 255
 */

// ----------------------------------
float flowRate = 0;
float pressure = 0;
float pressure_last = 0;
float lungVolume = 0;
float lungVolume_last = 0;
float R = 7;     // Airway resistance
int Vt = 500;    // Volume
int BPM = 14;    // Breath rate
float PEEP = 5;
float I_Ratio = 1;
float E_Ratio = 1;
float s = 5;      // Graph ratio constant 5
// ----------------------------------
int Vt_new = Vt;
int BPM_new = BPM;
float PEEP_new = PEEP;
float I_Ratio_new = I_Ratio;
float E_Ratio_new = E_Ratio;

unsigned long start = 0;
int dataInterval = 10;  // ms
float period = (60000/BPM);
int V = Vt;

float inhaleTime = (period * I_Ratio/(I_Ratio+E_Ratio));
float exhaleTime = (period * E_Ratio/(I_Ratio+E_Ratio));

char data[15];
int received[8];
float sentValue = 0;
float receivedValue = 0;

bool inhaleState = true;
bool exhaleState = false;
bool newValueState = false;

int send_volume_data = 0;
int send_flow_data = 0;
int send_pressure_data = 0;

void setup()
{
  Wire.begin(0x8);              // join i2c bus as slave with address 8
  Wire.onReceive(receiveEvent); // register event
  Wire.onRequest(sendData);
  Serial.begin(9600);           // start serial for output
  //while(!Serial);
}

void loop(){
  period = (60000/BPM);
  V = Vt;
  
  inhaleTime = (period * I_Ratio/(I_Ratio+E_Ratio));
  exhaleTime = (period * E_Ratio/(I_Ratio+E_Ratio));

  if (Serial.available() > 1){
    R = Serial.parseInt();
  }
  
  if (inhaleState){
    start = millis();
    inhale();
    inhaleState = false;
    newValueState = true;
  }
  if (newValueState){
    setNewValues();
    newValueState = false;
    exhaleState = true;
  }
  if (exhaleState){
    start = millis();
    exhale();
    exhaleState = false;
    inhaleState = true;
  }
}

void inhale(){
  float start_PEEP = PEEP;
  unsigned long inhaleStartTime = millis();
  while (lungVolume < Vt-3){
    if (millis() > (inhaleStartTime + dataInterval) && lungVolume < Vt){
      inhaleStartTime = millis();
      int x = millis() - start;

      lungVolume = V*(1-pow(e,((-x*s)/inhaleTime)));
      flowRate = (lungVolume - lungVolume_last)*5;
      lungVolume_last = lungVolume;
      pressure = ((s*R)/(period/1000)+start_PEEP);
      pressure = (pressure + pressure_last)/2;
    }
    Serial.println(lungVolume);
  }
  pressure_last = pressure;
}

void exhale(){
  pressure = PEEP;
  unsigned long exhaleStartTime = millis();
  while (lungVolume > 1){
    if (millis() > (exhaleStartTime + dataInterval) && lungVolume > 0){
      exhaleStartTime = millis();
      int x = millis() - start;

      lungVolume = Vt*pow(e, (-(x*s)/exhaleTime));
      flowRate = (lungVolume - lungVolume_last)*5;
      lungVolume_last = lungVolume;
    }
  }
}

void setNewValues(){
  Vt = Vt_new;
  BPM = BPM_new;
  I_Ratio = I_Ratio_new;
  E_Ratio = E_Ratio_new;
}

void receiveEvent(int packetSize){
  
  for (int i = 0; i < packetSize; i++){
    received[i] = Wire.read();
  }
  
  if (packetSize > 1){

    //----------Register 1----------//
    if (received[1] == 1){
      Vt_new = 0;
      for (int i = 2; i < packetSize; i++){
        Vt_new += received[i];
      }
      //Serial.println(Vt);
    }

    //----------Register 2----------//
    if (received[1] == 2){
      BPM_new = 0;
      for (int i = 2; i < packetSize; i++){
        BPM_new += received[i];
      }
      Serial.println(BPM);
    }

    //----------Register 3----------//
    if (received[1] == 3){
      I_Ratio_new = 0;
      for (int i = 2; i < packetSize; i++){
        I_Ratio_new += received[i]/100;
      }
      //Serial.println(I_Ratio);
    }

    //----------Register 4----------//
    if (received[1] == 4){
      E_Ratio_new = 0;
      for (int i = 2; i < packetSize; i++){
        E_Ratio_new += received[i]/100;
      }
      //Serial.println(E_Ratio);
    }
    
    //----------Register 5----------//
    if (received[1] == 5){
      PEEP_new = 0;
      for (int i = 2; i < packetSize; i++){
        PEEP_new += received[i];
      }
    }

    //----------Register 6----------//
    if (received[1] == 6){
      send_volume_data = 0;
      send_flow_data = 0;
      send_pressure_data = 0;
      send_volume_data = received[2];
    }

    //----------Register 7----------//
    if (received[1] == 7){
      send_volume_data = 0;
      send_flow_data = 0;
      send_pressure_data = 0;
      send_flow_data = received[2];
    }

    //----------Register 8----------//
    if (received[1] == 8){
      send_volume_data = 0;
      send_flow_data = 0;
      send_pressure_data = 0;
      send_pressure_data = received[2];
    }

  }      
}

void sendData(){
  if (send_volume_data == 1){  
    dtostrf(lungVolume, 7, 3, data);
    Wire.write(data);
  }

  if (send_flow_data == 1){
    dtostrf(flowRate, 7, 3, data);
    Wire.write(data);
  }

  if (send_pressure_data == 1){
    dtostrf(pressure, 5, 2, data);
    Wire.write(data);
  }

}
