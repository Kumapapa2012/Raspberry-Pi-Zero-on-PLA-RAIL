// ポート10502で Listen し、以下の動作。
/*
# motor_control.js
## 動作概要
ポート10502で待ち受け。以下を行う。
1. Connect 時、コネクトしたホストの IP アドレスを表示
2. クライアントから、スライドバーの値を recv し表示。
3. クライアントに、受け取った値に ”Received:” をつけて返信
4. クライアントが受信した値を表示
*/
const LISTENPORT_SERVER=10502;
const DRV8830_ADDR = 0x64;
// server.js
var port = process.env.PORT || LISTENPORT_SERVER;
var Server = require('ws').Server;
var ws = new Server({port: port});
ws.onerror = wsOnError;

var i2c = require('i2c-bus');
var i2c1 = i2c.openSync(1);
var value_last=0;

function motor_control(r) {
	console.log('r=' + r);
	i2c1.writeByte(DRV8830_ADDR, 0, r,function (err){
		if (err) {
			console.log(err);								
			// Reset 8830 driver
			i2c1.writeByteSync(DRV8830_ADDR, 0, 0x00);
			i2c1.writeByteSync(DRV8830_ADDR, 1, 0x80);
		}
	});
}

ws.on('connection', function(w){
  
  //現在の値をClientに送信する。
  w.send("{\"type\":\"change\",\"value\":"+value_last+"}");
  
  w.on('message', function(msg){
    console.log('message from client');
    console.log(msg);
    console.log('-------------------');
    
    // モーター、2V まで行くか。
    //i2c1.writeByteSync(DRV8830_ADDR, 0, 0);
    cli_data=JSON.parse(msg);
    switch (cli_data.type) {
	case 'change':
		// 低電圧誤動作防止のため、cli_data.value <５０ ではモーター操作しない。
		// cli_data.value : 0 - 100
		// value_current: 0,50-100
		var value_current = (50+((cli_data.value*50)/100))*(cli_data.value>0);

	    // drv8830 の 1.94V = 100% として計算。現在は前進のみ。
	    // 1.94V が 0x19=25段階。
		// 電圧降下防止のため、モーターの電圧は段階的に変える。
		// 電圧を上げる時のみ。Slider の値の差が +３０ を上回る場合、一段階クッションを置く。
		if(value_current - value_last > 30) {
			var value_delta=value_last+(value_current - value_last) / 2;
			r=((( value_delta * 25)/100)<<2)|0x1;
			motor_control(r);
		}

		r=(((value_current * 25)/100)<<2)|0x1;
		console.log('r=' + r);
		motor_control(r);
		value_last = value_current;

		// クライアントに反映
		ws.clients.forEach(function(client) {
			setTimeout(function timeout() {
				try {
						client.send(msg);					
					} catch(e) {
						console.log(e);
						wsOnError();
					}
			}, 300);
		});
	    break;

	default :

	    break;		
    }
    console.log(cli_data["type"]);
    console.log(value_current);
  });
  
  w.on('close', function() {
    console.log('closing connection');
  });

});

	
	
function wsOnError() {};



