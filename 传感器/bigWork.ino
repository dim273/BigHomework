#include <Servo.h>

#define CLK 2
#define DT 3
#define TRIG_PIN 10  // 超声波Trig引脚
#define ECHO_PIN 11  // 超声波Echo引脚
// 添加定时器变量
unsigned long previousMillis = 0;  // 存储上次打印的时间

Servo servo;      // 舵机实例

int counter = 0;

int currentStateCLK;
int lastStateCLK;

bool canUseCLK = true;

void setup() {

  // 设置编码器引脚为输入
  pinMode(CLK,INPUT);
  pinMode(DT,INPUT);

  // 设置超声波传感器引脚
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.begin(9600);

  // 将引脚9连接到舵机上
  servo.attach(9);
  servo.write(counter);

  // 读取CLK初始状态
  lastStateCLK = digitalRead(CLK);
}

// 接收来自网页端的信息
void receiveMes() {
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    message.trim();
    
    if (message.equals("CanUse")) {
      canUseCLK = true;
    } 
    else if (message.equals("CanNotUse")) {
      canUseCLK = false;
    }
    else if (!canUseCLK){
      int index = message.indexOf(':');
      if(index != -1) {
        String value = message.substring(index + 1);
        counter = value.toInt();
      }
    }
  }
}

// 超声波测距函数
float getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);   // 发送10μs高电平触发信号
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH);  // 接收回波高电平时间(μs)
  return duration * 0.034 / 2;             // 计算距离(cm)：声速340m/s = 0.034cm/μs
}

void loop() {
  receiveMes();

  if(!canUseCLK) {
    servo.write(counter);
  }
  else {
    // 读取CLK当前状态
    currentStateCLK = digitalRead(CLK);
    // 如果CLK改变则进入。同时，我们仅对1个状态改变做出反应，避免重复计数
    if (currentStateCLK != lastStateCLK && currentStateCLK == 1){
    // 旋转编码器逆时针旋转，故减少
      if (digitalRead(DT) != currentStateCLK) {
        counter -= 1;
        if (counter<0)
          counter=0;
      } 
      else {
      // 顺时针旋转，故增加
        counter += 1;
        if (counter>179)
        counter=180;
      }
      // 控制舵机转动
      servo.write(counter);
    }
  }

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= 1200) {
    previousMillis = currentMillis;  // 更新时间戳
    
    // 获取距离并打印
    float distance = getDistance();
    Serial.print("{\"angle\":");
    Serial.print(counter);
    Serial.print(",\"distance\":");
    Serial.print(distance);
    Serial.println("}");
  }

  // 记住上次的CLK状态
  lastStateCLK = currentStateCLK;
}
