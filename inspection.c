/*	运动预设参数	*/

//	相机pitch轴运动范围
float pit_limit_up;
float pit_limit_down;
//	p轴运动角速度。设计相机p轴以恒定角速度在up、down之间做往复运动。角度值实际上是个三角波
float omg_pit;

//	y轴旋转角速度
float omg_Yaw;
//	y轴旋转方向，0：逆时针	1：顺时针；这个一般不变，就是逆时针
uint8_t flag_yaw;

//	线速度
float spd;


void Straight(){
	/*	轨道运动参数	*/
	uint8_t flag_straight;	//	0：从点1到点2		1：从点2到点1
	float x1, y1, x2, y2;	//	轨道端点坐标
	
	
	/*	初始化参数	*/
	float pit_ini;	//	进入该段轨道时，p轴初始角度
	uint8_t flag_Pit;	//	pitch轴运动方向，0：正在从下向上运行		1：正在从上向下运行
	
	float yaw_ini;	//	c
	
	/*	过程参数	*/
	float t;	//	time	这里的t是个变量，即函数能把t时刻的数据算出来，出轨道的话要判断一下t最大值
	float x,y;	//	t时刻电机底盘坐标
	float ang_pit;	//	t时刻相机p角度
	float ang_yaw;	//	t时刻相机yaw角度
	
	/*	计算公式	*/
	
	/*	t时刻x、y计算	*/
	float dx,dy;
	float x_ini,y_ini;
	if(flag_straight == 0){
		float dx = x2 - x1;
		float dy = y2 - y1;
		x_ini = x1;
		y_ini = y1;
	}
	else if(flag_straight == 1){
		float dx = x1 - x2;
		float dy = y1 - y2;
		x_ini = x2;
		y_ini = y2;
	}
	x = x_ini + t*spd*dx/(dx*dx+dy*dy);
	y = y_ini + t*spd*dy/(dx*dx+dy*dy);
	
	/*	t时刻ang_yaw计算	*/
	if(flag_yaw == 0){
		ang_yaw = yaw_ini + t*omg_Yaw;
	}
	else if(flag_yaw == 1){
		ang_yaw = yaw_ini - t*omg_Yaw;
	}
	
	if(ang_yaw<0){
		uint8_t loop = ceil(ang_yaw/360);	//	ceil为除法，向上取整。此步骤意在将最终角度回归到0~360之间
		ang_yaw += loop*360;
	}
	else if(ang_yaw>360){
		uint8_t loop = ceil((ang_yaw-360)/360);
		ang_yaw -= loop*360;
	}
	
	
	/*	t时刻ang_pit计算	*/
	float one_loop_time = (pit_limit_up - pit_limit_down)/omg_pit;
	float loop_remain = t%(one_loop_time*2);	//	one_loop_time*2	是一次折返总时间，这个求余其实是计算出在t时间后，其运动了多少相对圈数，而非总圈数
	float ang_remain = loop_remain * omg_pit; //	换算成距离
	
	float ang_now;

	if(flag_Pit == 0){
		if(ang_remain > (pit_limit_up - pit_ini)){
			ang_now = ang_remain - (pit_limit_up - pit_ini);
			if(ang_now > (pit_limit_up - pit_limit_down)){
				ang_now = pit_limit_down + (ang_now - (pit_limit_up - pit_limit_down));
			}
			else{
				ang_now = pit_limit_up - ang_now;
			}
		}
		else{
			ang_now = pit_ini + ang_remain;
		}
	}
	else if(flag_Pit == 1){
		if(ang_remain > (pit_ini - pit_limit_down)){
			ang_now = ang_remain - (pit_ini - pit_limit_down);
			if(ang_now > (pit_limit_up - pit_limit_down)){
				ang_now = pit_limit_up - (ang_now - (pit_limit_up - pit_limit_down));
			}
			else{
				ang_now = pit_limit_down + ang_now;
			}
		}
		else{
			ang_now = pit_ini - ang_remain;
		}
	}
	
	ang_pit = ang_now;
	
}


void arc(){
	float PI = 3.14159
	
	/*	轨道运动参数	*/
	uint8_t flag_arc;	//	0：逆时针		1：顺时针
	float x_s, y_s, r, ang_s, ang_r;	//	圆弧轨道参数，x_s和y_s为圆心坐标，r为半径，ang_s为圆弧起始角度，ang_r为圆弧弧度角
	
	/*	初始化参数	*/
	float pit_ini;	//	进入该段轨道时，p轴初始角度
	uint8_t flag_Pit;	//	pitch轴运动方向，0：正在从下向上运行		1：正在从上向下运行
	
	float yaw_ini;	//	进入该段轨道时，y轴初始角度
	
	/*	过程参数	*/
	float t;	//	time	这里的t是个变量，即函数能把t时刻的数据算出来，出轨道的话要判断一下t最大值
	float x,y;	//	t时刻电机底盘坐标
	float ang_pit;	//	t时刻相机p角度
	float ang_yaw;	//	t时刻相机yaw角度
	
	/*	计算公式	*/
	
	/*	t时刻x、y计算	*/
	float dx,dy;
	float x_ini,y_ini;
	x_ini = x_s + r*cos(ang_s);	//	轨道起始绝对角度和轨道起始点有如下关系，虽然下面的计算没用到，但轨道建模可能会用
	y_ini = y_s + r*sin(ang_s);
	
	float omg_cha = (spd/r)*(360/2/PI);	//	计算角速度，注意这里的角速度单位是	度/秒	而非	弧度/秒
	
	
	if(flag_arc == 0){
		x = x_s + r*cos(ang_s + omg_cha * t);	//	这里cos函数输入为角度（ang变量均为角度
		y = y_s + r*sin(ang_s + omg_cha * t);
	}
	else if(flag_arc == 1){
		x = x_s + r*cos(ang_s - omg_cha * t);	//	这里cos函数输入为角度（ang变量均为角度
		y = y_s + r*sin(ang_s - omg_cha * t);
	}
	
	/*	t时刻ang_yaw计算	*/
	if(flag_yaw == 0){
		if(flag_arc == 0){
			ang_yaw = yaw_ini + t*omg_Yaw + t*omg_cha;
		}
		else if(flag_arc == 1){
			ang_yaw = yaw_ini + t*omg_Yaw - t*omg_cha;
		}
	}
	else if(flag_yaw == 1){
		if(flag_arc == 0){
			ang_yaw = yaw_ini - t*omg_Yaw + t*omg_cha;
		}
		else if(flag_arc == 1){
			ang_yaw = yaw_ini - t*omg_Yaw - t*omg_cha;
		}
	}
	
	if(ang_yaw<0){
		uint8_t loop = ceil(ang_yaw/360);	//	ceil为除法，向上取整。此步骤意在将最终角度回归到0~360之间
		ang_yaw += loop*360;
	}
	else if(ang_yaw>360){
		uint8_t loop = ceil((ang_yaw-360)/360);
		ang_yaw -= loop*360;
	}
	
	
	/*	t时刻ang_pit计算	*/
	float one_loop_time = (pit_limit_up - pit_limit_down)/omg_pit;
	float loop_remain = t%(one_loop_time*2);	//	one_loop_time*2	是一次折返总时间，这个求余其实是计算出在t时间后，其运动了多少相对圈数，而非总圈数
	float ang_remain = loop_remain * omg_pit; //	换算成距离
	
	float ang_now;

	if(flag_Pit == 0){
		if(ang_remain > (pit_limit_up - pit_ini)){
			ang_now = ang_remain - (pit_limit_up - pit_ini);
			if(ang_now > (pit_limit_up - pit_limit_down)){
				ang_now = pit_limit_down + (ang_now - (pit_limit_up - pit_limit_down));
			}
			else{
				ang_now = pit_limit_up - ang_now;
			}
		}
		else{
			ang_now = pit_ini + ang_remain;
		}
	}
	else if(flag_Pit == 1){
		if(ang_remain > (pit_ini - pit_limit_down)){
			ang_now = ang_remain - (pit_ini - pit_limit_down);
			if(ang_now > (pit_limit_up - pit_limit_down)){
				ang_now = pit_limit_up - (ang_now - (pit_limit_up - pit_limit_down));
			}
			else{
				ang_now = pit_limit_down + ang_now;
			}
		}
		else{
			ang_now = pit_ini - ang_remain;
		}
	}
	
	ang_pit = ang_now;
	
}