//
// モータを想定した2次系のダイナミクス
//
clf();

T=0.001;                    // 周期
t=0:T:3;                 // 終了時間
N=length(t);
// システムノイズ
v=rand(t,"normal");
sv=0;                  // システムノイズ σv
u=sv*v;
// システムのダイナミクス
A=[0 1; -36 -3.6];
B=[0;36];
c=[1 0];
AA=[1 0;0 1]+A*T;
BB=B*T;
// システムの時間発展
x0=[0.5;0];            // システムの初期値
x1=x0;                    // 真の状態x1 の初期化
for i=1:N-1
    x1(:,i+1)=AA*x1(:,i)+BB*u(i);
end
// 角度と角速度のプロット
subplot(2,1,1);
//plot(t,y,"color","green");
plot(t,x1(1,:),"color","red");
xtitle("モータの角度","t");
subplot(2,1,2);
plot(t,x1(2,:),"color","red");
xtitle("モータの角速度","t");

